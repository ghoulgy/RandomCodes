#!/usr/bin/env python3
"""
net_trace_2.py - Parallel live in-memory Sproto decoder + Frida host controller.
- JIT decode mode (default): the Frida callback only submits to the worker
  pool; workers write the final .bin/.json directly. No temp files, no queue.
- --durable: keep the temp-file (_raw.bin) flow for crash recovery (--redecode)
- Proto skip filtering happens ENTIRELY in the JS hook (--skip -> proto IDs)
- Decode worker PROCESS pool (--workers, default = CPU cores)
- Fast path: package header resolved before expensive full-schema heuristic scan
- Proto ID resolution from parent protocol ('x.request' -> x's tag)
"""

import argparse
import concurrent.futures
import fnmatch
import json
import multiprocessing
import os
import re
import signal
import struct
import sys
import time
import queue
import threading
from collections import OrderedDict

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

HERE = os.path.dirname(os.path.abspath(__file__))
JS_PATH = os.path.join(HERE, "net_trace_2.js")
SCHEMA_PATH = os.path.join(HERE, "combined_proto.sproto")

# ================================================================
# SPROTO DECODER ENGINE
# ================================================================

def sproto_unpack(data: bytes):
    srcsz = len(data)
    dst = bytearray()
    i = 0
    try:
        while i < srcsz:
            header = data[i]
            i += 1
            if header == 0xff:
                if i >= srcsz: return None
                n = data[i] + 1
                i += 1
                chunk_sz = n * 8
                if i + chunk_sz > srcsz: return None
                dst.extend(data[i:i + chunk_sz])
                i += chunk_sz
            else:
                for b in range(8):
                    if (header >> b) & 1:
                        if i >= srcsz: return None
                        dst.append(data[i])
                        i += 1
                    else:
                        dst.append(0)
        return bytes(dst)
    except Exception:
        return None

class Field:
    def __init__(self, name, tag, typename, is_array=False, key=None):
        self.name = name
        self.tag = tag
        self.typename = typename
        self.is_array = is_array
        self.key = key

class SType:
    def __init__(self, name):
        self.name = name
        self.fields = []
        self.by_tag = {}

class Schema:
    def __init__(self):
        self.types = {}
        self.protocols = {}
        self.protocols_by_tag = {}
        
        pkg = SType('package')
        pkg.by_tag = {
            0: Field('type', 0, 'integer'),
            1: Field('session', 1, 'integer'),
            2: Field('ud', 2, 'string')
        }
        self.types['package'] = pkg

    def get_type(self, typename, scope=None):
        if not typename: return None
        if typename in self.types: return self.types[typename]
        
        if scope:
            parts = scope.split('.')
            for i in range(len(parts), 0, -1):
                candidate = '.'.join(parts[:i]) + '.' + typename
                if candidate in self.types: return self.types[candidate]
                
        suffix = '.' + typename
        matches = [t for name, t in self.types.items() if name.endswith(suffix)]
        if len(matches) == 1: return matches[0]
        elif len(matches) > 1 and scope:
            for m in matches:
                parent = m.name.rsplit('.', 1)[0]
                if scope.startswith(parent) or parent in scope: return m
            return matches[0]
        return None

def parse_schema(text):
    schema = Schema()
    lines = []
    for line in text.split('\n'):
        line = line.split('#')[0].rstrip()
        if line.strip():
            lines.append(line.strip())

    current_type = None
    current_proto = None
    current_section = None
    type_stack = []

    for s in lines:
        m = re.match(r'^\.(\w+)\s*\{', s)
        if m:
            tname = m.group(1)
            if current_type:
                nested = current_type.name + '.' + tname
                type_stack.append(current_type)
            elif type_stack:
                nested = type_stack[-1].name + '.' + tname
            else:
                nested = tname
            current_type = SType(nested)
            schema.types[nested] = current_type
            continue

        if not current_type and not current_proto:
            m = re.match(r'^(\w+)\s+(\d+)\s*\{', s)
            if m:
                current_proto = {
                    'name': m.group(1),
                    'tag': int(m.group(2)),
                    'request': None,
                    'response': None
                }
                schema.protocols[m.group(1)] = current_proto
                schema.protocols_by_tag[int(m.group(2))] = current_proto
                continue

        if current_proto and not current_type:
            req_match = re.match(r'^request\s+(\w+)', s)
            resp_match = re.match(r'^response\s+(\w+)', s)
            req_block = re.match(r'^request\s*\{', s)
            resp_block = re.match(r'^response\s*\{', s)

            if req_match:
                current_proto['request'] = req_match.group(1)
            elif resp_match:
                current_proto['response'] = resp_match.group(1)
            elif req_block:
                current_type = SType(current_proto['name'] + '.request')
                schema.types[current_type.name] = current_type
                current_section = 'request'
            elif resp_block:
                current_type = SType(current_proto['name'] + '.response')
                schema.types[current_type.name] = current_type
                current_section = 'response'
            
            if req_match or resp_match or req_block or resp_block:
                continue

        # closing-brace handling: a .type closing inside a protocol
        # no longer drops the protocol itself
        if s.startswith('}'):
            if type_stack:
                current_type = type_stack.pop()
            elif current_section and current_type:
                current_proto[current_section] = current_type.name
                current_section = None
                current_type = None
            elif current_type:
                current_type = None
            else:
                current_proto = None
            continue

        if current_type:
            m = re.match(r'(\w+)\s+(\d+)\s*:\s*(.+)', s)
            if m:
                fname = m.group(1)
                ftag = int(m.group(2))
                ftype = m.group(3).strip()
                is_arr = False
                key = None
                
                if ftype.startswith('*'):
                    is_arr = True
                    ftype = ftype[1:]
                    km = re.match(r'(\w+)\((\w*)\)', ftype)
                    if km:
                        ftype = km.group(1)
                        key = km.group(2)
                    elif ftype.endswith('()'):
                        ftype = ftype[:-2]
                        key = ''
                        
                if re.match(r'(integer)\(\d+\)', ftype):
                    ftype = 'integer'
                    
                f = Field(fname, ftag, ftype, is_arr, key)
                current_type.by_tag[f.tag] = f

    return schema

# header sanity check used before recursively decoding unknown blobs
def is_valid_sproto_header(data, offset=0):
    if offset + 2 > len(data):
        return False
    entry_count = struct.unpack_from('<H', data, offset)[0]
    if entry_count == 0 or entry_count > 64:
        return False
    return offset + 2 + entry_count * 2 <= len(data)

def decode_message(data, schema, type_name, offset=0):
    result = OrderedDict()
    pos = offset
    try:
        if pos + 2 > len(data): return result, 0
        entry_count = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        if entry_count == 0: return result, pos

        entries = []
        last_tag = -1
        idx_end = pos + entry_count * 2
        
        for _ in range(entry_count):
            if pos + 2 > len(data): break
            entry = struct.unpack_from('<H', data, pos)[0]
            pos += 2
            if entry & 1:
                entries.append((last_tag + 1 + (entry >> 1), None, 'nil'))
            else:
                bits = entry >> 1
                if bits > 0:
                    entries.append((last_tag + 1, bits - 1, 'embedded'))
                else:
                    entries.append((last_tag + 1, None, 'data'))
            last_tag = entries[-1][0]

        dpos = idx_end
        stype = schema.get_type(type_name) if type_name else None

        for tag, value, kind in entries:
            field = stype.by_tag.get(tag) if stype else None
            fname = field.name if field else f"tag_{tag}"
            
            if kind == 'nil': continue
            elif kind == 'embedded':
                if field and field.typename == 'boolean': result[fname] = (value != 0)
                else: result[fname] = value
            elif kind == 'data':
                if dpos + 4 > len(data): break
                size = struct.unpack_from('<I', data, dpos)[0]
                dpos += 4
                if dpos + size > len(data): break
                content = data[dpos:dpos+size]
                dpos += size

                if field:
                    target_stype = schema.get_type(field.typename, scope=stype.name if stype else None)
                    if field.is_array:
                        if size == 0:
                            result[fname] = []
                        elif field.typename == 'integer':
                            arr = []
                            if size > 0:
                                int_sz = content[0]
                                sub_data = content[1:]
                                if int_sz == 4:
                                    for j in range(0, len(sub_data) - len(sub_data) % 4, 4):
                                        arr.append(struct.unpack_from('<i', sub_data, j)[0])
                                elif int_sz == 8:
                                    for j in range(0, len(sub_data) - len(sub_data) % 8, 8):
                                        arr.append(struct.unpack_from('<q', sub_data, j)[0])
                            result[fname] = arr
                        elif field.typename == 'boolean':
                            result[fname] = [b != 0 for b in content]
                        elif field.typename == 'double':
                            result[fname] = [struct.unpack_from('<d', content, j)[0] for j in range(0, size - size % 8, 8)]
                        elif field.typename in ('string', 'binary'):
                            arr = []
                            aptr = 0
                            while aptr + 4 <= size:
                                s_len = struct.unpack_from('<I', content, aptr)[0]
                                aptr += 4
                                if aptr + s_len > size: break
                                if field.typename == 'string':
                                    arr.append(content[aptr:aptr + s_len].decode('utf-8', 'replace'))
                                else:
                                    arr.append(content[aptr:aptr + s_len].hex())
                                aptr += s_len
                            result[fname] = arr
                        elif target_stype:
                            arr = []
                            aptr = 0
                            while aptr + 4 <= size:
                                elem_sz = struct.unpack_from('<I', content, aptr)[0]
                                aptr += 4
                                if aptr + elem_sz > size: break
                                sub, _ = decode_message(content[aptr:aptr + elem_sz], schema, target_stype.name)
                                arr.append(sub)
                                aptr += elem_sz
                            result[fname] = arr
                        else:
                            result[fname] = content.hex() if size > 0 else ''
                    else:
                        if field.typename == 'integer':
                            # oversized (>=9B) integers are tried as nested
                            # structs first, like sproto_decoder
                            if size == 4: result[fname] = struct.unpack_from('<i', content, 0)[0]
                            elif size == 8: result[fname] = struct.unpack_from('<q', content, 0)[0]
                            elif 0 < size < 8: result[fname] = int.from_bytes(content, 'little', signed=True)
                            else:
                                sub, _ = decode_message(content, schema, '')
                                result[fname] = sub if sub else content.hex()
                        elif field.typename == 'double':
                            result[fname] = struct.unpack_from('<d', content, 0)[0] if size == 8 else content.hex()
                        elif field.typename in ('string', 'binary'):
                            if field.typename == 'string' and size > 0: result[fname] = content.decode('utf-8', 'replace')
                            else: result[fname] = content.hex() if size > 0 else ''
                        elif field.typename == 'boolean':
                            result[fname] = (content[0] != 0) if size > 0 else False
                        elif target_stype:
                            sub, _ = decode_message(content, schema, target_stype.name)
                            result[fname] = sub if size > 0 else {}
                        else:
                            result[fname] = content.hex() if size > 0 else ''
                else:
                    # unknown/unnamed fields get recursive struct decode
                    # (with header sanity check) before falling back to utf-8/hex
                    if size == 4: result[fname] = struct.unpack_from('<i', content, 0)[0]
                    elif size == 8: result[fname] = struct.unpack_from('<q', content, 0)[0]
                    elif size > 0:
                        if is_valid_sproto_header(content):
                            sub, _ = decode_message(content, schema, '')
                            if sub and len(sub) > 0:
                                result[fname] = sub
                                continue
                        try:
                            dec = content.decode('utf-8')
                            if all(c.isprintable() or c in '\r\n\t' for c in dec): result[fname] = dec
                            else: result[fname] = content.hex()
                        except Exception: result[fname] = content.hex()
                    else: result[fname] = ''
        return result, dpos
    except Exception:
        return result, pos

def evaluate_fields(v):
    named = unnamed = 0
    if isinstance(v, dict):
        for k, val in v.items():
            if str(k).startswith('tag_'): unnamed += 1
            else: named += 1
            n, u = evaluate_fields(val)
            named += n; unnamed += u
    elif isinstance(v, list):
        for item in v:
            n, u = evaluate_fields(item)
            named += n; unnamed += u
    return named, unnamed

def find_best_type(data, schema, tolerance=10):
    """Full-schema heuristic scan — expensive, only used when headers fail."""
    best = None
    for type_name in schema.types:
        result, consumed = decode_message(data, schema, type_name, 0)
        if result and len(result) > 0 and consumed >= len(data) - tolerance:
            named, unnamed = evaluate_fields(result)
            coverage = consumed / len(data) if len(data) > 0 else 0
            score = (named - (unnamed * 5)) * coverage
            if best is None or score > best[3]:
                best = (type_name, result, named, score)
    return best

def extract_proto_tags(val):
    if isinstance(val, int): return [val, val & 0xFFFF, (val >> 16) & 0xFFFF]
    elif isinstance(val, str) and val.isdigit(): return [int(val), int(val) & 0xFFFF]
    return []

def decode_envelope(data, schema):
    if len(data) < 18: return None
    if struct.unpack_from('<H', data, 0)[0] != 2: return None
    if struct.unpack_from('<I', data, 6)[0] != 4: return None
    
    proto_val = struct.unpack_from('<I', data, 10)[0]
    f1_sz = struct.unpack_from('<I', data, 14)[0]
    
    if 18 + f1_sz > len(data): return None
    inner_payload = data[18:18 + f1_sz]
    
    proto = None
    matched_tag = None
    for tag in extract_proto_tags(proto_val):
        if tag in schema.protocols_by_tag:
            proto = schema.protocols_by_tag[tag]
            matched_tag = tag
            break
            
    env_info = OrderedDict([
        ("raw_proto_id", proto_val), 
        ("matched_tag", matched_tag),
        ("proto_name", proto['name'] if proto else "(unknown)")
    ])
    
    if proto:
        for kind in ('request', 'response'):
            if proto.get(kind):
                resolved = schema.get_type(proto[kind]).name if schema.get_type(proto[kind]) else proto[kind]
                content, _ = decode_message(inner_payload, schema, resolved)
                if content:
                    return env_info, (resolved, content), evaluate_fields(content)[0] + 200

    best = find_best_type(inner_payload, schema)
    if best and best[2] > 0:
        return env_info, (best[0], best[1]), best[2] + 100
        
    raw_inner, _ = decode_message(inner_payload, schema, '')
    return env_info, ("(raw_inner)", raw_inner), 50

def decode_buffer(data, schema, session_map=None, is_out=True):
    # 1. Envelope Peeling (cheap)
    env_res = decode_envelope(data, schema)
    if env_res:
        return env_res[0], env_res[1], env_res[2]

    # 2. FAST PATH: package header first — skips find_best_type entirely
    #    when the header already names a known proto with a decodable body
    pkg, consumed = decode_message(data, schema, 'package', 0)
    if pkg and 0 < consumed <= len(data):
        ptype = pkg.get('type')
        session = pkg.get('session')

        # A real sproto package carries type and/or session as INTEGERS.
        # If neither is an int (e.g. a raw response body whose tag-1 struct
        # decodes 'session' as a dict -> unhashable crash), it's not a
        # package — discard that interpretation, heuristic scan takes over.
        if isinstance(ptype, int) or isinstance(session, int):
            if session is not None and isinstance(session, int) and session_map is not None:
                if is_out and isinstance(ptype, int):
                    session_map[session] = ptype
                elif not is_out and session in session_map:
                    ptype = session_map.pop(session)

            if isinstance(ptype, int) and ptype in schema.protocols_by_tag:
                proto = schema.protocols_by_tag[ptype]
                remaining = data[consumed:]
                # direction-appropriate kind first, then the other;
                # accept only a NON-EMPTY decode, else fall through
                kinds = ('request', 'response') if is_out else ('response', 'request')
                for kind in kinds:
                    tname = proto.get(kind)
                    if not tname:
                        continue
                    resolved = schema.get_type(tname).name if schema.get_type(tname) else tname
                    if len(remaining) == 0:
                        if 'type' not in pkg: pkg['type'] = ptype
                        return pkg, (resolved, {}), 100
                    c, _ = decode_message(remaining, schema, resolved)
                    if c:
                        if 'type' not in pkg: pkg['type'] = ptype
                        return pkg, (resolved, c), evaluate_fields(c)[0] + 100
        else:
            pkg = None   # not a package after all

    # 3. Heuristic full scan — only when the fast path failed
    best = find_best_type(data, schema)
    if best and best[2] >= 2 and best[3] > 1.5:
        return None, (best[0], best[1]), best[2] * 10

    # 4. Package fallbacks (header parsed but proto/body didn't resolve)
    if pkg and 0 < consumed <= len(data) and len(data[consumed:]) > 0:
        best_sub = find_best_type(data[consumed:], schema)
        if best_sub:
            return pkg, (best_sub[0], best_sub[1]), best_sub[2] + 50
        raw, _ = decode_message(data[consumed:], schema, '')
        if raw:
            return pkg, ('(unknown)', raw), 10

    if best and best[2] > 0:
        return None, (best[0], best[1]), best[2]

    raw, _ = decode_message(data, schema, '', 0)
    if raw:
        return None, ('(unknown)', raw), 1
    return None, None, 0

def prepare_variants(raw_data):
    candidates = []
    seen = set()
    def add_cand(buf):
        if buf and buf not in seen:
            seen.add(buf)
            candidates.append(buf)
            
    add_cand(raw_data)
    
    if len(raw_data) > 2:
        be2 = struct.unpack('>H', raw_data[:2])[0]
        le2 = struct.unpack('<H', raw_data[:2])[0]
        if be2 == len(raw_data) - 2 or le2 == len(raw_data) - 2:
            add_cand(raw_data[2:])
            
    if len(raw_data) > 4:
        be4 = struct.unpack('>I', raw_data[:4])[0]
        le4 = struct.unpack('<I', raw_data[:4])[0]
        if be4 == len(raw_data) - 4 or le4 == len(raw_data) - 4:
            add_cand(raw_data[4:])
            
    for base in list(candidates):
        unpacked = sproto_unpack(base)
        if unpacked:
            add_cand(unpacked)
            
    return candidates

def decode_smart(data, schema, session_map=None, is_out=True):
    variants = prepare_variants(data)
    best_res = (None, None)
    best_score = -1

    for cand in variants:
        pkg, content, score = decode_buffer(cand, schema, session_map, is_out)
        if score > best_score:
            best_score = score
            best_res = (pkg, content)

    return best_res

# ================================================================
# PROTO IDENTIFICATION
# ================================================================

def find_parent_proto(schema, type_name):
    """First protocol that owns this body type.
    'notify_general_bp_extra_info.request' -> ('notify_general_bp_extra_info', 15481, True)
    Returns (proto_name, tag, exact) or None."""
    if not type_name:
        return None

    # inline '<proto>.request' / '<proto>.response' -> exact parent
    for suffix in ('.request', '.response'):
        if type_name.endswith(suffix):
            parent = type_name[:-len(suffix)]
            if parent in schema.protocols:
                return parent, schema.protocols[parent]['tag'], True

    # shared type referenced by some protocol's request/response -> first match
    for pname, proto in schema.protocols.items():
        for kind in ('request', 'response'):
            tname = proto.get(kind)
            if not tname:
                continue
            st = schema.get_type(tname)
            if (st and st.name == type_name) or tname == type_name:
                return pname, proto['tag'], False

    return None

# ================================================================
# SHARED DECODE PIPELINE (JIT and durable, pool and single thread)
# No skip logic here — proto filtering happens entirely in the JS hook.
# ================================================================

def process_item(item, schema, session_map):
    """Full decode pipeline for one captured message.
    Returns a console line (str) or None.

    JIT mode:  item['bin_path'] is None -> worker writes the final .bin itself.
    Durable:   item['bin_path'] set     -> promote the temp file via os.replace.
    """
    data = item["data"]
    try:
        is_out = item["dir"] == "out"
        pkg, content = None, None
        proto_name, proto_id = "UNKNOWN", "UNKNOWN"

        try:
            pkg, content = decode_smart(data, schema, session_map, is_out)
        except Exception as e:
            # JIT mode has no temp file on disk, so on failure still save the
            # raw bytes — never lose a captured message entirely
            if not item.get("bin_path"):
                try:
                    with open(os.path.join(item["bin_dir"], "UNKNOWN",
                                           f"{item['prefix']}.bin"), "wb") as f:
                        f.write(data)
                except OSError:
                    pass
            return f"[-] Decode Exception on {item['tag']} #{item['counter']}: {e}"

        type_name = content[0] if (content and content[0]) else None

        # --- initial identification (envelope / package header) ---
        if pkg and 'raw_proto_id' in pkg:
            proto_id = pkg['raw_proto_id']
            proto_name = pkg.get('proto_name', "UNKNOWN")
        elif pkg and 'type' in pkg:
            proto_id = pkg['type']
            if isinstance(proto_id, int) and proto_id in schema.protocols_by_tag:
                proto_name = schema.protocols_by_tag[proto_id]['name']
        elif type_name and type_name not in ("(unknown)", "(raw_inner)"):
            proto_name = type_name

        # --- resolve proto id from the parent protocol of the body type ---
        # display name keeps the full type ('notify_general_bp_extra_info.request'),
        # only the ID is taken from the parent protocol (e.g. 15481)
        if type_name and type_name not in ("(unknown)", "(raw_inner)"):
            parent = find_parent_proto(schema, type_name)
            if parent is not None:
                parent_name, parent_tag, exact = parent
                if exact:
                    proto_name = type_name
                    proto_id = parent_tag
                elif proto_id == "UNKNOWN":
                    proto_id = parent_tag

        is_unk = proto_name in ("UNKNOWN", "(unknown)")
        final_bin = os.path.join(item["bin_dir"], "UNKNOWN" if is_unk else "", f"{item['prefix']}.bin")
        save_json = os.path.join(item["json_dir"], "UNKNOWN" if is_unk else "", f"{item['prefix']}_{proto_name}.json")

        if item.get("bin_path"):
            os.replace(item["bin_path"], final_bin)          # durable: promote temp file
        else:
            with open(final_bin, "wb") as f:
                f.write(data)                                # JIT: write final file directly

        decoded_output = {
            "proto_id": proto_id,
            "proto_name": proto_name,
            "package": pkg,
            "body": content[1] if content else None,
        }
        with open(save_json, "w", encoding="utf-8") as f:
            json.dump(decoded_output, f, ensure_ascii=False, indent=2)

        return f"[{item['tag']}] {len(data):4d} B -> {final_bin} | Proto: {proto_name} (ID: {proto_id})"
    except Exception as e:
        return f"[-] Worker exception on {item['event']} #{item['counter']}: {e}"

# ================================================================
# PROCESS-POOL WORKERS
# ================================================================

_MP_SCHEMA = None
_MP_SESSION = None

def _mp_init(schema_text, session_map):
    """Runs once in every worker process."""
    global _MP_SCHEMA, _MP_SESSION
    # workers ignore Ctrl+C; the parent controls shutdown & drain
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except Exception:
        pass
    _MP_SCHEMA = parse_schema(schema_text)
    _MP_SESSION = session_map   # shared Manager dict

def _mp_process(item):
    return process_item(item, _MP_SCHEMA, _MP_SESSION)

# ================================================================
# HOST CONTROLLER & DUMPER
# JIT (default): callback only submits, workers write final files.
# Durable (--durable): callback writes NNN_raw.bin first (crash recovery).
# ================================================================

class AsyncDumper:
    def __init__(self, outdir, schema, schema_text=None, filter_mode="both",
                 workers=0, durable=False):
        self.outdir = outdir
        self.schema = schema
        self.filter_mode = filter_mode.lower()
        self.durable = durable

        self.enc_dir = os.path.join(outdir, "encode_out")
        self.dec_dir = os.path.join(outdir, "decode_in")
        self.decoded_out_dir = os.path.join(outdir, "decoded_out")
        self.decoded_in_dir = os.path.join(outdir, "decoded_in")
        self.session_map = {}

        for d in [self.enc_dir, self.dec_dir, self.decoded_out_dir, self.decoded_in_dir]:
            os.makedirs(os.path.join(d, "UNKNOWN"), exist_ok=True)
            os.makedirs(d, exist_ok=True)

        self.enc = 0
        self.dec = 0

        self.workers = max(0, workers or 0)
        self.pool = None
        self.manager = None
        self.outstanding = 0
        self._lock = threading.Lock()

        if self.workers >= 1:
            # process pool: true parallel decoding (GIL makes threads useless
            # for CPU-bound pure-Python decode work)
            self.manager = multiprocessing.Manager()
            self.session_map = self.manager.dict()
            self.pool = concurrent.futures.ProcessPoolExecutor(
                max_workers=self.workers,
                initializer=_mp_init,
                initargs=(schema_text, self.session_map))
        else:
            # legacy single in-process worker thread
            self.decode_queue = queue.Queue()
            self.worker = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker.start()

    def submit(self, item):
        """Dispatch one item immediately (no intermediate queue in pool mode)."""
        if self.pool is not None:
            with self._lock:
                self.outstanding += 1
            self.pool.submit(_mp_process, item).add_done_callback(self._on_done)
        else:
            self.decode_queue.put(item)

    def _on_done(self, future):
        """Runs in the parent when a worker process finishes an item."""
        try:
            line = future.result()
        except Exception as e:
            print(f"[-] Pool error: {e}")
            line = None
        if line:
            print(line)
        # decrement last: outstanding==0 implies all prints flushed
        with self._lock:
            self.outstanding -= 1

    def on_message(self, message, data):
        """Frida callback thread: JIT — pure dispatch, no disk I/O here
        (unless --durable)."""
        if message["type"] == "send":
            p = message.get("payload", {}) or {}
            ev = p.get("event")
            is_out = (ev == "encode_out")
            is_in = (ev == "decode_in")
            if not (is_out or is_in) or not data:
                return
            if self.filter_mode == "in" and is_out: return
            if self.filter_mode == "out" and not is_out: return

            ts, seq = p.get('ts', time.time() * 1000), p.get('seq', 0)

            if is_out:
                self.enc += 1; counter = self.enc; bin_dir, json_dir = self.enc_dir, self.decoded_out_dir
            else:
                self.dec += 1; counter = self.dec; bin_dir, json_dir = self.dec_dir, self.decoded_in_dir
            prefix = "%03d" % counter

            bin_path = None
            if self.durable:
                # crash-safe: bytes hit the disk before decode is even scheduled
                bin_path = os.path.join(bin_dir, f"{prefix}_raw.bin")
                with open(bin_path, "wb") as f:
                    f.write(data)

            self.submit({
                "event": ev, "counter": counter,
                "dir": "out" if is_out else "in", "tag": "OUT" if is_out else "IN ",
                "ts": ts, "seq": seq, "data": data, "bin_path": bin_path,
                "prefix": prefix, "bin_dir": bin_dir, "json_dir": json_dir
            })

        elif message["type"] == "error":
            print("[!] JS Error: " + str(message.get("description")))

    def pending_count(self):
        if self.pool is not None:
            with self._lock:
                return self.outstanding
        return self.decode_queue.qsize()

    # ---------------- single-thread mode ----------------

    def _worker_loop(self):
        while True:
            item = self.decode_queue.get()
            if item is None: break
            try:
                self._process_sproto(item)
            except Exception as e:
                print(f"[-] Worker exception on {item['event']} #{item['counter']}: {e}")
            self.decode_queue.task_done()

    def _process_sproto(self, item):
        line = process_item(item, self.schema, self.session_map)
        if line:
            print(line)

    # ---------------- shutdown ----------------

    def drain(self):
        """Block until every dispatched item is fully processed."""
        if self.pool is not None:
            self.pool.shutdown(wait=True)
            while True:
                with self._lock:
                    if self.outstanding <= 0:
                        break
                time.sleep(0.05)
        else:
            pending = self.decode_queue.qsize()
            if pending:
                print(f"[*] Draining {pending} message(s) …")
            self.decode_queue.put(None)
            self.worker.join()

    def shutdown(self):
        """Force cleanup (idempotent; safe after drain)."""
        if self.pool is not None:
            try: self.pool.shutdown(wait=False)
            except Exception: pass
        if self.manager is not None:
            try: self.manager.shutdown()
            except Exception: pass

def main():
    ap = argparse.ArgumentParser(description="Real-time in-memory Sproto capture")
    ap.add_argument("target", help="Target process name or package name")
    ap.add_argument("--spawn", action="store_true", help="Spawn package instead of attaching")
    ap.add_argument("--host", default="127.0.0.1:31337", help="Frida server host:port (default 127.0.0.1:31337)")
    ap.add_argument("--out", default="sproto_dump", help="Output directory")
    ap.add_argument("--filter", choices=["in", "out", "both"], default="both", help="Filter capture direction (default both)")
    ap.add_argument("--skip", nargs="+", default=["package", "*loginauth*"], metavar="PATTERN",
                    help="Proto name globs to drop IN THE JS HOOK (resolved to proto IDs "
                         "and injected into the script; hook-side only, no effect in "
                         "--redecode mode). The special name 'package' drops header-only "
                         "keepalive-style messages. Default: package *loginauth*. "
                         "Pass 'none' to disable.")
    ap.add_argument("--workers", type=int, default=None, metavar="N",
                    help="Number of decode worker PROCESSES (default: CPU core count). "
                         "0 = single in-process worker thread (legacy mode).")
    ap.add_argument("--durable", action="store_true",
                    help="Write NNN_raw.bin temp files before decoding (crash recovery "
                         "via --redecode). Default: JIT mode — bytes are held in memory "
                         "until the worker writes the final .bin/.json.")
    ap.add_argument("--redecode", metavar="DIR",
                    help="Offline mode: re-decode leftover *_raw.bin files in this output "
                         "directory, then exit (target argument is ignored)")
    args = ap.parse_args()

    import frida   # imported here so worker processes don't load it

    with open(SCHEMA_PATH, "r", encoding="utf-8", errors="replace") as f:
        schema_text = f.read()
    schema = parse_schema(schema_text)

    # flatten "a,b c" style input into a pattern list
    skip_patterns = []
    for part in (args.skip or []):
        for p in part.split(','):
            p = p.strip()
            if p:
                skip_patterns.append(p)
    if len(skip_patterns) == 1 and skip_patterns[0].lower() in ("none", "-"):
        skip_patterns = []

    # ---- resolve skip patterns -> JS hook filter ----
    skip_ids = set()
    drop_header_only = False
    for p in skip_patterns:
        pl = p.lower()
        if pl in ("package", "*package*"):
            drop_header_only = True
        rx = re.compile(fnmatch.translate(pl))
        for pname, proto in schema.protocols.items():
            if rx.match(pname.lower()):
                skip_ids.add(proto["tag"])

    print(f"[*] Loaded schema: {len(schema.types)} types, {len(schema.protocols)} protocols.")
    print(f"[*] Capture filter active: {args.filter.upper()}")
    if skip_ids or drop_header_only:
        msg = f"[*] Hook-side skip: {len(skip_ids)} proto id(s)"
        if drop_header_only:
            msg += " + header-only (package) messages"
        print(msg)
    else:
        print("[*] Hook-side skip: disabled")

    workers = args.workers if args.workers is not None else (os.cpu_count() or 2)
    print(f"[*] Decode workers: {workers} process(es)" if workers >= 1
          else "[*] Decode workers: single thread")
    print("[*] Decode mode: durable (temp files, --redecode recovery)" if args.durable
          else "[*] Decode mode: JIT (in-memory dispatch, no temp files)")

    # ---------------- offline re-decode mode ----------------
    if args.redecode:
        if skip_patterns:
            print("[!] --skip is hook-side only and does NOT apply in --redecode mode")
        dumper = AsyncDumper(args.redecode, schema, schema_text,
                             filter_mode=args.filter, workers=workers, durable=True)
        n = 0
        for bin_dir, direction, ev, json_dir in (
                (dumper.enc_dir, "out", "encode_out", dumper.decoded_out_dir),
                (dumper.dec_dir, "in", "decode_in", dumper.decoded_in_dir)):
            if not os.path.isdir(bin_dir):
                continue
            if args.filter == "in" and direction == "out": continue
            if args.filter == "out" and direction == "in": continue
            for fn in sorted(os.listdir(bin_dir)):
                if not fn.endswith("_raw.bin"):
                    continue
                bin_path = os.path.join(bin_dir, fn)
                try:
                    with open(bin_path, "rb") as f:
                        blob = f.read()
                except OSError:
                    continue
                prefix = fn[:-len("_raw.bin")]
                dumper.submit({
                    "event": ev,
                    "counter": int(prefix) if prefix.isdigit() else n,
                    "dir": direction, "tag": "OUT" if direction == "out" else "IN ",
                    "ts": int(os.path.getmtime(bin_path) * 1000), "seq": 0,
                    "data": blob, "bin_path": bin_path, "prefix": prefix,
                    "bin_dir": bin_dir, "json_dir": json_dir,
                })
                n += 1
        print(f"[*] Re-decoding {n} leftover file(s) from {args.redecode} …")
        dumper.drain()
        dumper.shutdown()
        print("[*] Done.")
        return

    manager = frida.get_device_manager()
    device = manager.add_remote_device(args.host)
    print(f"[*] Connected to Frida @ {args.host}")

    with open(JS_PATH, "r", encoding="utf-8") as f:
        script_source = f.read()

    # inject the proto filter into the JS (placeholder replace)
    if "__FILTER__" not in script_source:
        print("[!] net_trace_2.js has no __FILTER__ placeholder — "
              "hook-side skip disabled. Update the JS file.")
        filter_json = '{"skipIds":[],"knownIds":[],"dropHeaderOnly":false}'
    elif not skip_ids and not drop_header_only:
        filter_json = '{"skipIds":[],"knownIds":[],"dropHeaderOnly":false}'
    else:
        filter_json = json.dumps({
            "skipIds": sorted(skip_ids),
            "knownIds": sorted({p["tag"] for p in schema.protocols.values()}),
            "dropHeaderOnly": drop_header_only,
        })
    script_source = script_source.replace("__FILTER__", filter_json)

    dumper = AsyncDumper(args.out, schema, schema_text,
                         filter_mode=args.filter, workers=workers, durable=args.durable)
    try:
        pid = device.spawn([args.target]) if args.spawn else None
        session = device.attach(pid) if pid else device.attach(args.target)

        script = session.create_script(script_source)
        script.on("message", dumper.on_message)
        script.load()

        if pid:
            device.resume(pid)

        print(f"[*] Sproto capture running — Press Ctrl+C to stop")
        last_warn = 0
        while True:
            time.sleep(1)
            q = dumper.pending_count()
            if q > 100 and q >= last_warn + 100:
                print(f"[!] Decoder backlog: {q} messages in flight")
                last_warn = q
            elif q <= 10:
                last_warn = 0

    except KeyboardInterrupt:
        pending = dumper.pending_count()
        if pending:
            print(f"\n[*] Draining {pending} message(s) …")
        dumper.drain()
        print("[*] Stopped.")
    finally:
        try:
            session.detach()
        except Exception:
            pass
        dumper.shutdown()

if __name__ == "__main__":
    main()