import frida, os, sys, time

OUT = './dumped_dex'
os.makedirs(OUT, exist_ok=True)

def on_message(message, data):
    if message['type'] == 'send':
        p = message['payload']
        if p.get('type') == 'dex_dump' and data is not None:
            name = os.path.join(OUT, p['base'].replace(':', '_') + '.dex')
            with open(name, 'wb') as f:
                f.write(data)
            print(f"[host] wrote {name} ({len(data)} bytes)")
    elif message['type'] == 'error':
        print('[script error]', message.get('description'), message.get('stack'))

device = frida.get_device_manager().add_remote_device('127.0.0.1:31337')
pid = device.spawn(['com.gof.global'])
session = device.attach(pid)
session.on('detached', lambda reason, *a: print('[!] detached:', reason, a))  # <- was missing

script = session.create_script(open('hook5.js', encoding='utf-8').read())
script.on('message', on_message)
script.load()

# arm EVERYTHING before resume — closes the race you saw in your log
print('[*]', script.exports_sync.init())    # older frida: script.exports.init()

device.resume(pid)
time.sleep(10)                              # let the packer unpack
print('[*]', script.exports_sync.scan())
sys.stdin.read()