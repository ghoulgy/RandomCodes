#!/usr/bin/env python3
"""
sproto_decoder.py - Full Sproto recursive binary message decoder.
- Handles 0-pack unpacking and framing headers.
- Automatically peels RPC envelopes and resolves inner payloads using schema.
- Accurately resolves nested types (e.g., .side_data.overview).
- Uses tag penalization to prevent float/binary arrays from false-matching as structs.
"""

import os, re, sys, struct, argparse, glob
from collections import OrderedDict

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


# ================================================================
# SPROTO 0-PACK UNPACKER
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
                if i >= srcsz:
                    return None
                n = data[i] + 1
                i += 1
                chunk_sz = n * 8
                if i + chunk_sz > srcsz:
                    return None
                dst.extend(data[i:i + chunk_sz])
                i += chunk_sz
            else:
                for b in range(8):
                    if (header >> b) & 1:
                        if i >= srcsz:
                            return None
                        dst.append(data[i])
                        i += 1
                    else:
                        dst.append(0)
        return bytes(dst)
    except Exception:
        return None


# ================================================================
# SCHEMA PARSER & RESOLVER
# ================================================================

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

        # Default envelope header fallback
        pkg = SType('package')
        f_type = Field('type', 0, 'integer')
        f_sess = Field('session', 1, 'integer')
        f_ud   = Field('ud', 2, 'string')
        pkg.fields = [f_type, f_sess, f_ud]
        pkg.by_tag = {0: f_type, 1: f_sess, 2: f_ud}
        self.types['package'] = pkg

    def get_type(self, typename, scope=None):
        if not typename:
            return None
        if typename in self.types:
            return self.types[typename]

        # Scope resolution hierarchy
        if scope:
            parts = scope.split('.')
            for i in range(len(parts), 0, -1):
                candidate = '.'.join(parts[:i]) + '.' + typename
                if candidate in self.types:
                    return self.types[candidate]

        # Suffix matching
        suffix = '.' + typename
        matches = [t for name, t in self.types.items() if name.endswith(suffix)]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1 and scope:
            for m in matches:
                parent = m.name.rsplit('.', 1)[0]
                if scope.startswith(parent) or parent in scope:
                    return m
            return matches[0]

        return None


def parse_schema(text):
    schema = Schema()
    lines = []
    for line in text.split('\n'):
        idx = line.find('#')
        if idx >= 0:
            line = line[:idx]
        lines.append(line.rstrip())

    current_type = None
    current_proto = None
    current_section = None
    type_stack = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

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

        if current_type is None and current_proto is None:
            m = re.match(r'^(\w+)\s+(\d+)\s*\{', s)
            if m:
                pname = m.group(1)
                ptag = int(m.group(2))
                current_proto = {
                    'name': pname,
                    'tag': ptag,
                    'request': None,
                    'response': None,
                }
                schema.protocols[pname] = current_proto
                schema.protocols_by_tag[ptag] = current_proto
                continue

        if current_proto and current_type is None:
            m_req = re.match(r'^request\s+(\w+)', s)
            if m_req:
                current_proto['request'] = m_req.group(1)
                continue

            m_resp = re.match(r'^response\s+(\w+)', s)
            if m_resp:
                current_proto['response'] = m_resp.group(1)
                continue

            if re.match(r'^request\s*\{', s):
                tname = current_proto['name'] + '.request'
                current_type = SType(tname)
                schema.types[tname] = current_type
                current_section = 'request'
                continue

            elif re.match(r'^response\s*\{', s):
                tname = current_proto['name'] + '.response'
                current_type = SType(tname)
                schema.types[tname] = current_type
                current_section = 'response'
                continue

        if s == '}' or s.startswith('}'):
            if type_stack:
                current_type = type_stack.pop()
            elif current_section and current_type:
                if current_section == 'request':
                    current_proto['request'] = current_type.name
                elif current_section == 'response':
                    current_proto['response'] = current_type.name
                current_section = None
                current_type = None
            elif current_type:
                current_type = None
            elif current_proto:
                current_proto = None
            continue

        if current_type:
            m = re.match(r'(\w+)\s+(\d+)\s*:\s*(.+)', s)
            if m:
                fname = m.group(1)
                ftag = int(m.group(2))
                ftype = m.group(3).strip()
                is_array, key = False, None

                if ftype.startswith('*'):
                    is_array = True
                    ftype = ftype[1:]
                    km = re.match(r'(\w+)\((\w*)\)', ftype)
                    if km:
                        ftype = km.group(1)
                        key = km.group(2)
                    elif ftype.endswith('()'):
                        ftype = ftype[:-2]
                        key = ''

                im = re.match(r'(integer)\(\d+\)', ftype)
                if im:
                    ftype = 'integer'

                f = Field(fname, ftag, ftype, is_array, key)
                current_type.fields.append(f)
                current_type.by_tag[ftag] = f
                continue

    return schema


# ================================================================
# BINARY DECODER
# ================================================================

def is_valid_sproto_header(data, offset=0):
    if offset + 2 > len(data):
        return False
    entry_count = struct.unpack_from('<H', data, offset)[0]
    if entry_count == 0 or entry_count > 64:
        return False
    return offset + 2 + entry_count * 2 <= len(data)


def decode_message(data, schema, type_name, offset=0, debug=False, indent=""):
    result = OrderedDict()
    pos = offset

    try:
        if pos + 2 > len(data):
            return result, 0

        entry_count = struct.unpack_from('<H', data, pos)[0]
        pos += 2

        if entry_count == 0:
            return result, pos

        entries = []
        last_tag = -1
        idx_end = pos + entry_count * 2

        for i in range(entry_count):
            if pos + 2 > len(data):
                break
            entry = struct.unpack_from('<H', data, pos)[0]
            pos += 2

            if entry & 1:
                delta = entry >> 1
                tag = last_tag + 1 + delta
                entries.append((tag, None, 'nil'))
            else:
                bits = entry >> 1
                tag = last_tag + 1
                if bits > 0:
                    value = bits - 1
                    entries.append((tag, value, 'embedded'))
                else:
                    entries.append((tag, None, 'data'))
            last_tag = tag

        dpos = idx_end
        stype = schema.get_type(type_name) if type_name else None

        for tag, value, kind in entries:
            field = stype.by_tag.get(tag) if stype else None
            fname = field.name if field else f"tag_{tag}"

            if kind == 'nil':
                continue

            elif kind == 'embedded':
                if field and field.typename == 'boolean':
                    result[fname] = (value != 0)
                else:
                    result[fname] = value

            elif kind == 'data':
                if dpos + 4 > len(data):
                    break

                size = struct.unpack_from('<I', data, dpos)[0]
                dpos += 4

                if dpos + size > len(data):
                    break

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
                                if aptr + s_len > size:
                                    break
                                s_bytes = content[aptr:aptr + s_len]
                                aptr += s_len
                                if field.typename == 'string':
                                    arr.append(s_bytes.decode('utf-8', errors='replace'))
                                else:
                                    arr.append(s_bytes.hex())
                            result[fname] = arr
                        elif target_stype:
                            arr = []
                            aptr = 0
                            while aptr + 4 <= size:
                                elem_sz = struct.unpack_from('<I', content, aptr)[0]
                                aptr += 4
                                if aptr + elem_sz > size:
                                    break
                                elem_data = content[aptr:aptr + elem_sz]
                                aptr += elem_sz
                                sub, _ = decode_message(elem_data, schema, target_stype.name, 0, debug, indent + "    ")
                                arr.append(sub)
                            result[fname] = arr
                        else:
                            result[fname] = content.hex() if size > 0 else ''

                    else:
                        if field.typename == 'integer':
                            if size == 4:
                                result[fname] = struct.unpack_from('<i', content, 0)[0]
                            elif size == 8:
                                result[fname] = struct.unpack_from('<q', content, 0)[0]
                            elif 0 < size < 8:
                                result[fname] = int.from_bytes(content, 'little', signed=True)
                            else:
                                sub, _ = decode_message(content, schema, '', 0, debug, indent + "    ")
                                result[fname] = sub if sub else content.hex()
                        elif field.typename == 'double':
                            if size == 8:
                                result[fname] = struct.unpack_from('<d', content, 0)[0]
                            else:
                                result[fname] = content.hex()
                        elif field.typename in ('string', 'binary'):
                            if field.typename == 'string':
                                result[fname] = content.decode('utf-8', errors='replace') if size > 0 else ''
                            else:
                                result[fname] = content.hex() if size > 0 else ''
                        elif field.typename == 'boolean':
                            result[fname] = (content[0] != 0) if size > 0 else False
                        elif target_stype:
                            if size > 0:
                                sub, _ = decode_message(content, schema, target_stype.name, 0, debug, indent + "    ")
                                result[fname] = sub
                            else:
                                result[fname] = {}
                        else:
                            result[fname] = content.hex() if size > 0 else ''

                else:
                    if size == 4:
                        result[fname] = struct.unpack_from('<i', content, 0)[0]
                    elif size == 8:
                        result[fname] = struct.unpack_from('<q', content, 0)[0]
                    elif size > 0:
                        if is_valid_sproto_header(content):
                            sub, _ = decode_message(content, schema, '', 0, False, indent + "    ")
                            if sub and len(sub) > 0:
                                result[fname] = sub
                                continue
                        try:
                            decoded_str = content.decode('utf-8')
                            if all(c.isprintable() or c in '\r\n\t' for c in decoded_str):
                                result[fname] = decoded_str
                            else:
                                result[fname] = content.hex()
                        except Exception:
                            result[fname] = content.hex()
                    else:
                        result[fname] = ''

        return result, dpos

    except (struct.error, IndexError):
        return result, pos


# ================================================================
# SMART RESOLUTION & RECURSIVE ENVELOPE PEELING
# ================================================================

def evaluate_fields(v):
    named = 0
    unnamed = 0
    if isinstance(v, dict):
        for k, val in v.items():
            if str(k).startswith('tag_'):
                unnamed += 1
            else:
                named += 1
            n, u = evaluate_fields(val)
            named += n
            unnamed += u
    elif isinstance(v, list):
        for item in v:
            n, u = evaluate_fields(item)
            named += n
            unnamed += u
    return named, unnamed


def find_best_type(data, schema, tolerance=10):
    best = None
    for type_name in schema.types:
        result, consumed = decode_message(data, schema, type_name, 0)
        if result and len(result) > 0:
            named, unnamed = evaluate_fields(result)
            coverage = consumed / len(data) if len(data) > 0 else 0
            if consumed >= len(data) - tolerance:
                # Heavily penalize unresolved tags to prevent float arrays from spoofing structs
                score = (named - (unnamed * 5)) * coverage 
                if best is None or score > best[3]:
                    best = (type_name, result, named, score)
    return best


def extract_proto_tags(val):
    tags = []
    if isinstance(val, int):
        tags.append(val)
        tags.append(val & 0xFFFF)
        tags.append((val >> 16) & 0xFFFF)
    elif isinstance(val, str) and val.isdigit():
        t = int(val)
        tags.append(t)
        tags.append(t & 0xFFFF)
    return tags


def decode_envelope(data, schema, debug=False):
    """
    Peels Sproto RPC envelopes where Field 0 is Tag/Cmd and Field 1 is inner body.
    """
    if len(data) < 18:
        return None

    # Inspect envelope structure: 2 entries, size 4 tag, followed by body
    entries = struct.unpack_from('<H', data, 0)[0]
    if entries != 2:
        return None

    f0_sz = struct.unpack_from('<I', data, 6)[0]
    if f0_sz != 4:
        return None

    proto_val = struct.unpack_from('<I', data, 10)[0]
    f1_sz = struct.unpack_from('<I', data, 14)[0]

    if 18 + f1_sz > len(data):
        return None

    inner_payload = data[18:18 + f1_sz]

    # Look up protocol by candidate tags
    proto = None
    matched_tag = None
    for tag in extract_proto_tags(proto_val):
        if tag in schema.protocols_by_tag:
            proto = schema.protocols_by_tag[tag]
            matched_tag = tag
            break

    envelope_info = OrderedDict([
        ("raw_proto_id", proto_val),
        ("matched_tag", matched_tag),
        ("proto_name", proto['name'] if proto else "(unknown)"),
        ("payload_len", f1_sz)
    ])

    if proto:
        for kind in ('request', 'response'):
            tname = proto.get(kind)
            if tname:
                st = schema.get_type(tname)
                resolved = st.name if st else tname
                content, _ = decode_message(inner_payload, schema, resolved, 0, debug)
                if content:
                    return envelope_info, (resolved, content), evaluate_fields(content)[0] + 200

    # Fallback to direct type search on inner payload
    best_inner = find_best_type(inner_payload, schema)
    if best_inner and best_inner[2] > 0:
        return envelope_info, (best_inner[0], best_inner[1]), best_inner[2] + 100

    raw_inner, _ = decode_message(inner_payload, schema, '', 0, debug)
    if raw_inner:
        return envelope_info, ("(raw_inner)", raw_inner), 50

    return None


def decode_buffer(data, schema, debug=False):
    # 1. Check if packet is an envelope
    env_res = decode_envelope(data, schema, debug)
    if env_res:
        return env_res[0], env_res[1], env_res[2]

    # 2. Direct schema type matching
    best = find_best_type(data, schema)
    if best and best[2] >= 2 and best[3] > 1.5:
        return None, (best[0], best[1]), best[2] * 10

    # 3. Standard .package decode
    pkg, consumed = decode_message(data, schema, 'package', 0, debug)
    if pkg and 0 < consumed < len(data):
        ptype = pkg.get('type')
        if isinstance(ptype, int) and 0 <= ptype <= 0xFFFFFFFF:
            remaining = data[consumed:]
            proto = schema.protocols_by_tag.get(ptype)
            if proto:
                for kind in ('request', 'response'):
                    tname = proto.get(kind)
                    if tname:
                        st = schema.get_type(tname)
                        resolved = st.name if st else tname
                        if len(remaining) > 0:
                            content, _ = decode_message(remaining, schema, resolved, 0, debug)
                            if content:
                                return pkg, (resolved, content), evaluate_fields(content)[0] + 100
                        else:
                            return pkg, (resolved, {}), 100

            if len(remaining) > 0:
                best_sub = find_best_type(remaining, schema)
                if best_sub:
                    return pkg, (best_sub[0], best_sub[1]), best_sub[2] + 50
                raw, _ = decode_message(remaining, schema, '', 0, debug)
                if raw:
                    return pkg, ('(unknown)', raw), 10

    if best and best[2] > 0:
        return None, (best[0], best[1]), best[2]

    raw, _ = decode_message(data, schema, '', 0, debug)
    if raw:
        return None, ('(raw)', raw), 1

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


def decode_smart(data, schema, debug=False):
    variants = prepare_variants(data)
    best_res = (None, None)
    best_score = -1

    for cand in variants:
        pkg, content, score = decode_buffer(cand, schema, debug)
        if score > best_score:
            best_score = score
            best_res = (pkg, content)

    return best_res


# ================================================================
# PRETTY PRINTER & CLI
# ================================================================

def pp(v, indent="  "):
    if isinstance(v, dict):
        if not v:
            return "{}"
        lines = ["{"]
        for k, val in v.items():
            if isinstance(val, (dict, list)):
                lines.append(f"{indent}{k} = {pp(val, indent + '  ')}")
            elif isinstance(val, str) and len(val) > 80:
                lines.append(f"{indent}{k} = \"{val[:40]}...\" ({len(val)} chars)")
            else:
                lines.append(f"{indent}{k} = {repr(val)}")
        lines.append(indent[:-2] + "}" if len(indent) > 2 else "}")
        return "\n".join(lines)
    elif isinstance(v, list):
        if not v:
            return "[]"
        lines = ["["]
        for item in v:
            lines.append(f"{indent}{pp(item, indent + '  ')}")
        lines.append(indent[:-2] + "]" if len(indent) > 2 else "]")
        return "\n".join(lines)
    return repr(v)


def main():
    ap = argparse.ArgumentParser(description="Full Sproto recursive message decoder")
    ap.add_argument('--schema', required=True, help='.sproto schema file')
    ap.add_argument('--file', help='single .bin file')
    ap.add_argument('--dir', help='directory of .bin files')
    ap.add_argument('--type', help='force a specific type name')
    ap.add_argument('--debug', action='store_true', help='verbose output')
    args = ap.parse_args()

    print(f"Loading schema: {args.schema}")
    with open(args.schema, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    schema = parse_schema(text)
    print(f"  types: {len(schema.types)}, protocols: {len(schema.protocols)}")
    print()

    files = []
    if args.file:
        files = [args.file]
    elif args.dir:
        for sub in ['encode_out', 'decode_in', '']:
            d = os.path.join(args.dir, sub) if sub else args.dir
            if os.path.isdir(d):
                files.extend(sorted(glob.glob(os.path.join(d, '*.bin'))))
        files = sorted(set(files))

    if not files:
        print("No .bin files found. Use --file or --dir")
        sys.exit(1)

    print(f"Files: {len(files)}\n" + "=" * 60 + "\n")

    for filepath in files:
        with open(filepath, 'rb') as f:
            data = f.read()

        fname = os.path.basename(filepath)
        direction = "OUT" if 'encode_out' in filepath else "IN" if 'decode_in' in filepath else "??"

        print(f"=== {direction} {fname} ({len(data)} B) ===")

        if args.type:
            target_data = data
            unpacked = sproto_unpack(data)
            if unpacked:
                target_data = unpacked
            # Strip 18 bytes envelope if forced type is meant for inner payload
            if len(target_data) > 18 and struct.unpack_from('<H', target_data, 0)[0] == 2:
                f0_sz = struct.unpack_from('<I', target_data, 6)[0]
                if f0_sz == 4:
                    target_data = target_data[18:]
            result, consumed = decode_message(target_data, schema, args.type, 0, args.debug)
            if result:
                named = evaluate_fields(result)[0]
                print(f"  [{args.type}] {consumed}/{len(target_data)}B, {named} named fields")
                print(pp(result, "  "))
            else:
                print(f"  [FAILED as {args.type}]")

        else:
            package, content = decode_smart(data, schema, args.debug)

            if package and content:
                print(f"  [envelope] {pp(package, '    ')}")
                type_name, result = content
                named = evaluate_fields(result)[0]
                print(f"  [content: {type_name}] {named} named fields")
                print(pp(result, "  "))

            elif content:
                type_name, result = content
                named = evaluate_fields(result)[0]
                print(f"  [{type_name}] {named} named fields")
                print(pp(result, "  "))

            else:
                print("  [FAILED]")

        print()


if __name__ == "__main__":
    main()
