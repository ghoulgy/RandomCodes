import frida, os, sys, time, struct, zlib, hashlib

OUT = './dumped_dex'
os.makedirs(OUT, exist_ok=True)
seen_hash = set()

def repair_dex(buf: bytes) -> bytes:
    b = bytearray(buf)
    if len(b) < 0x70:
        return bytes(b)
    b[0:4] = b'dex\n'
    if not (0x30 <= b[4] <= 0x39 and b[7] == 0):
        b[4:8] = b'035\x00'
    struct.pack_into('<I', b, 0x20, len(b))                    # file_size
    struct.pack_into('<I', b, 0x24, 0x70)                      # header_size
    struct.pack_into('<I', b, 0x28, 0x12345678)                # endian_tag
    b[0x0c:0x20] = hashlib.sha1(bytes(b[0x20:])).digest()      # signature
    struct.pack_into('<I', b, 0x08, zlib.adler32(bytes(b[0x0c:])))  # checksum
    return bytes(b)

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']

        if p.get('type') == 'dex_dump' and data:
            digest = hashlib.sha256(data).hexdigest()
            if digest in seen_hash:
                print(f"[host] duplicate dex skipped ({p['size']} bytes)")
                return
            seen_hash.add(digest)
            name = p['base'].replace('0x', '').replace(':', '_') + f"_{p['size']}.dex"
            path = os.path.join(OUT, name)
            fixed = repair_dex(data)
            with open(path, 'wb') as f:
                f.write(fixed if len(fixed) >= 0x70 else data)
            print(f"[host] wrote {path} ({len(data)} bytes, header repaired)")

        elif p.get('type') == 'meta_dump' and data:
            digest = hashlib.sha256(data).hexdigest()
            if digest in seen_hash:
                print(f"[host] duplicate metadata skipped ({p['size']} bytes)")
                return
            seen_hash.add(digest)
            ver = p.get('version', '?')
            name = f"global-metadata_v{ver}_{p['size']}.dat"
            path = os.path.join(OUT, name)
            with open(path, 'wb') as f:
                f.write(data)          # raw — Il2CppDumper reads by offsets,
                                       # trailing mapping garbage is ignored
            print(f"[host] wrote {path} ({len(data)} bytes, metadata v{ver})")

    elif message['type'] == 'error':
        print('[script error]', message.get('description'), message.get('stack'))

def on_detached(reason, *args):
    print('[!] detached:', reason, args)
    os._exit(0)

device = frida.get_device_manager().add_remote_device('127.0.0.1:31337')
pid = device.spawn(['com.gof.global'])
session = device.attach(pid)
session.on('detached', on_detached)

script = session.create_script(open('hook6.js', encoding='utf-8').read())
script.on('message', on_message)
script.load()

print('[*]', script.exports_sync.init())   # arm everything BEFORE resume
device.resume(pid)

# host-side polling replaces the Java-level triggers
for i in range(30):                         # ~60 seconds
    time.sleep(2)
    try:
        script.exports_sync.scan(f'poll{i}')
    except Exception as e:
        print('[-] scan failed:', e)
        break

print('[*] poll window finished. Interact with the app, then Ctrl+C to exit.')
sys.stdin.read()