#!/usr/bin/env python3
"""
net_trace.py - Threaded Dual-capture & live in-memory Sproto decoder.
Features non-blocking background decoding to prevent Frida packet loss.
"""

import argparse
import json
import os
import re
import struct
import sys
import time
import shutil
import queue
import threading
from collections import OrderedDict
import frida

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)

HERE = os.path.dirname(os.path.abspath(__file__))
JS_PATH = os.path.join(HERE, "net_trace.js")
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

        if s.startswith('}'):
            if type_stack:
                current_type = type_stack.pop()
            elif current_section:
                current_proto[current_section] = current_type.name
                current_section = None
                current_type = None
            else:
                current_type = None
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
                            if size == 4: result[fname] = struct.unpack_from('<i', content, 0)[0]
                            elif size == 8: result[fname] = struct.unpack_from('<q', content, 0)[0]
                            elif size > 0: result[fname] = int.from_bytes(content, 'little', signed=True)
                            else: result[fname] = 0
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
                    if size == 4: result[fname] = struct.unpack_from('<i', content, 0)[0]
                    elif size == 8: result[fname] = struct.unpack_from('<q', content, 0)[0]
                    elif size > 0:
                        try:
                            dec = content.decode('utf-8')
                            if all(c.isprintable() or c in '\r\n\t' for c in dec): result[fname] = dec
                            else: result[fname] = content.hex()
                        except: result[fname] = content.hex()
                    else: result[fname] = ''
        return result, dpos
    except:
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
    """Accurately identifies raw bodies inside packets without explicit header tags."""
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

def extract_proto_candidates(data):
    candidates = []
    if len(data) >= 4:
        for offset in range(0, min(16, len(data) - 2), 2):
            u16 = struct.unpack_from('<H', data, offset)[0]
            if 0 < u16 < 65535: candidates.append(u16)
            if offset + 4 <= len(data):
                u32 = struct.unpack_from('<I', data, offset)[0]
                if 0 < u32 < 0x7FFFFFFF: candidates.append(u32)
    return candidates

def decode_buffer(data, schema, session_map=None, is_out=True):
    # 1. Envelope Peeling
    env_res = decode_envelope(data, schema)
    if env_res:
        return env_res[0], env_res[1], env_res[2]

    # 2. Heuristics & Nested Raw Structs
    best = find_best_type(data, schema)
    if best and best[2] >= 2 and best[3] > 1.5:
        return None, (best[0], best[1]), best[2] * 10

    # 3. Standard Standard Package parsing
    pkg, consumed = decode_message(data, schema, 'package', 0)
    if pkg and 0 < consumed <= len(data):
        ptype = pkg.get('type')
        session = pkg.get('session')

        if not isinstance(ptype, int):
            for heur_cand in extract_proto_candidates(data):
                if heur_cand in schema.protocols_by_tag:
                    ptype = heur_cand
                    break

        if session is not None and session_map is not None:
            if is_out and isinstance(ptype, int):
                session_map[session] = ptype
            elif not is_out and session in session_map:
                ptype = session_map.pop(session)

        if isinstance(ptype, int) and ptype in schema.protocols_by_tag:
            proto = schema.protocols_by_tag[ptype]
            kind = 'request' if is_out else 'response'
            tname = proto.get(kind)
            
            remaining = data[consumed:] if pkg else data
            if tname:
                resolved = schema.get_type(tname).name if schema.get_type(tname) else tname
                c, _ = decode_message(remaining, schema, resolved)
                if pkg and 'type' not in pkg: pkg['type'] = ptype
                return pkg, (resolved, c), evaluate_fields(c)[0] + 100
            else:
                if pkg and 'type' not in pkg: pkg['type'] = ptype
                return pkg, (proto['name'], {}), 100

        if len(data[consumed:]) > 0:
            best_sub = find_best_type(data[consumed:], schema)
            if best_sub:
                return pkg, (best_sub[0], best_sub[1]), best_sub[2] + 50
            raw, _ = decode_message(data[consumed:], schema, '')
            if raw:
                return pkg, ('(unknown)', raw), 10

    if best and best[2] > 0:
        return None, (best[0], best[1]), best[2]

    raw, _ = decode_message(data, schema, '', 0)
    return None, ('(unknown)', raw), 0

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
# HOST CONTROLLER & BACKGROUND THREAD DUMPER
# ================================================================

class AsyncDumper:
    def __init__(self, outdir, schema, filter_mode="both"):
        self.outdir = outdir
        self.schema = schema
        self.filter_mode = filter_mode.lower()
        
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
        
        # Threading Queue to prevent Frida from dropping packets
        self.decode_queue = queue.Queue()
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()

    def on_message(self, message, data):
        """Executed on Frida's callback thread. Instant return to prevent blocking."""
        if message["type"] == "send":
            p = message.get("payload", {})
            ev = p.get("event")

            if ev in ("encode_out", "decode_in") and data:
                is_out = (ev == "encode_out")
                
                if self.filter_mode == "in" and is_out: return
                if self.filter_mode == "out" and not is_out: return

                if is_out:
                    self.enc += 1
                    counter, bin_dir, json_dir, tag_str = self.enc, self.enc_dir, self.decoded_out_dir, "OUT"
                else:
                    self.dec += 1
                    counter, bin_dir, json_dir, tag_str = self.dec, self.dec_dir, self.decoded_in_dir, "IN "

                prefix = "%03d" % counter
                
                # Instantly save raw binary
                temp_bin = os.path.join(bin_dir, f"{prefix}_raw.bin")
                with open(temp_bin, "wb") as f:
                    f.write(data)

                # Push to background thread for heavy processing
                self.decode_queue.put((counter, is_out, tag_str, data, bin_dir, json_dir, temp_bin, prefix))

        elif message["type"] == "error":
            print("[!] JS Error: " + str(message.get("description")))

    def _worker_loop(self):
        """Executed in the background. Performs heavy schema decoding."""
        while True:
            item = self.decode_queue.get()
            if item is None: break
            
            counter, is_out, tag_str, data, bin_dir, json_dir, temp_bin, prefix = item
            pkg, content = None, None
            proto_name, proto_id = "UNKNOWN", "UNKNOWN"
            
            try:
                pkg, content = decode_smart(data, self.schema, self.session_map, is_out)
                
                if pkg and 'raw_proto_id' in pkg: 
                    proto_id = pkg['raw_proto_id']
                    proto_name = pkg.get('proto_name', "UNKNOWN")
                elif pkg and 'type' in pkg:
                    proto_id = pkg['type']
                    if proto_id in self.schema.protocols_by_tag:
                        proto_name = self.schema.protocols_by_tag[proto_id]['name']
                elif content and content[0] and content[0] != "(unknown)" and content[0] != "(raw_inner)":
                    proto_name = content[0]
            except Exception as e:
                print(f"[-] Decode Exception on {tag_str} #{counter}: {e}")

            # Route to final structural folders
            is_unk = (proto_name == "UNKNOWN")
            final_bin = os.path.join(bin_dir, "UNKNOWN" if is_unk else "", f"{prefix}.bin")
            save_json = os.path.join(json_dir, "UNKNOWN" if is_unk else "", f"{prefix}_{proto_name}.json")

            os.replace(temp_bin, final_bin)

            decoded_output = {
                "package": pkg, 
                "body": content[1] if content else None
            }
            
            with open(save_json, "w", encoding="utf-8") as f:
                json.dump(decoded_output, f, ensure_ascii=False, indent=2)

            # Parallel Grouping logic
            try:
                session_id = pkg.get('session') if pkg else None
                if session_id is not None:
                    sess_dir = os.path.join(self.outdir, "grouped_by_session", f"session_{session_id}")
                    os.makedirs(sess_dir, exist_ok=True)
                    shutil.copy2(final_bin, os.path.join(sess_dir, f"{prefix}_{tag_str.strip()}_{proto_name}.bin"))
                    shutil.copy2(save_json, os.path.join(sess_dir, f"{prefix}_{tag_str.strip()}_{proto_name}.json"))

                safe_proto = str(proto_name).replace(":", "_").replace("/", "_").replace("\\", "_")
                proto_dir_name = f"{proto_id}_{safe_proto}"
                proto_dir = os.path.join(self.outdir, "grouped_by_proto", proto_dir_name)
                os.makedirs(proto_dir, exist_ok=True)
                shutil.copy2(final_bin, os.path.join(proto_dir, f"{prefix}_{tag_str.strip()}.bin"))
                shutil.copy2(save_json, os.path.join(proto_dir, f"{prefix}_{tag_str.strip()}.json"))
            except Exception as e:
                pass

            print(f"[{tag_str}] {len(data):4d} B -> {final_bin} | Proto: {proto_name} (ID: {proto_id})")
            self.decode_queue.task_done()

def main():
    ap = argparse.ArgumentParser(description="Real-time Sproto Capture & Threaded Decoder")
    ap.add_argument("target", help="Target process name or package name")
    ap.add_argument("--spawn", action="store_true", help="Spawn package instead of attaching")
    ap.add_argument("--host", default="127.0.0.1:31337", help="Frida server host:port (default 127.0.0.1:31337)")
    ap.add_argument("--out", default="dual_dump", help="Output directory")
    ap.add_argument("--filter", choices=["in", "out", "both"], default="both", help="Filter capture direction: in, out, or both (default is both)")
    args = ap.parse_args()

    with open(SCHEMA_PATH, "r", encoding="utf-8", errors="replace") as f:
        schema = parse_schema(f.read())
        
    print(f"[*] Loaded schema: {len(schema.types)} types, {len(schema.protocols)} protocols.")
    print(f"[*] Capture filter active: {args.filter.upper()}")

    manager = frida.get_device_manager()
    device = manager.add_remote_device(args.host)
    print(f"[*] Connected to Frida @ {args.host}")

    with open(JS_PATH, "r", encoding="utf-8") as f: 
        script_source = f.read()
    
    dumper = AsyncDumper(args.out, schema, filter_mode=args.filter)
    try:
        pid = device.spawn([args.target]) if args.spawn else None
        session = device.attach(pid) if pid else device.attach(args.target)
        
        script = session.create_script(script_source)
        script.on("message", dumper.on_message)
        script.load()

        if pid: 
            device.resume(pid)

        print(f"[*] Live capturing ({args.filter.upper()}) & threaded decoding running — Press Ctrl+C to stop")
        while True: 
            time.sleep(1)

    except KeyboardInterrupt: 
        print("\n[*] Stopping capture...")
    finally:
        try: 
            session.detach()
        except: 
            pass

if __name__ == "__main__":
    main()