#!/usr/bin/env python3
"""Dump Lua chunks via luaL_loadbuffer(x), talking to a TCP frida-server."""

import argparse, hashlib, os, re, time
import frida

HERE = os.path.dirname(os.path.abspath(__file__))
JS_PATH = os.path.join(HERE, "dump_lua.js")


def sanitize(name: str) -> str:
    name = (name or "").lstrip("@=").strip()
    name = re.sub(r'[<>:"|?*\\/]', "_", name)
    name = re.sub(r"\s+", "_", name)
    return name[:120] or "chunk"


def pick_ext(data: bytes) -> str:
    if data[:3] == b"\x1bLJ":      # LuaJIT bytecode
        return ".luac"
    if data[:4] == b"\x1bLua":     # Lua bytecode
        return ".luac"
    return ".lua"                  # plaintext source


class LuaDumper:
    def __init__(self, outdir: str):
        self.outdir = outdir
        os.makedirs(outdir, exist_ok=True)
        self.seen = set()
        self.saved = 0

    def on_message(self, message, data):
        if message["type"] == "send":
            payload = message["payload"]
            if payload.get("event") == "chunk":
                self.save_chunk(payload, data)
        elif message["type"] == "error":
            print("[!] script error:", message.get("description"))
            print(message.get("stack", ""))

    def save_chunk(self, payload, data):
        if not data:
            return
        digest = hashlib.sha256(data).hexdigest()
        if digest in self.seen:
            print(f"[dup] {payload['name']} ({len(data)} bytes)")
            return
        self.seen.add(digest)

        base, ext = sanitize(payload.get("name")), pick_ext(data)
        path = os.path.join(self.outdir, base + ext)
        n = 1
        while os.path.exists(path):
            path = os.path.join(self.outdir, f"{base}_{n}{ext}")
            n += 1

        with open(path, "wb") as f:
            f.write(data)
        self.saved += 1
        print(f"[+] {path} ({len(data):,} bytes, via {payload['api']})")

def load_agent(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        print("[!] warning: UTF-8 BOM detected - remove it (save without BOM)")
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        sys.exit(f"[!] {path} is not valid UTF-8: {e}")
    # The agent is pure ASCII now, so ANY non-ASCII char is copy-paste corruption
    for i, line in enumerate(source.splitlines(), 1):
        bad = [hex(ord(c)) for c in line if ord(c) > 126 or (ord(c) < 32 and c != "\t")]
        if bad:
            print(f"[!] warning: suspicious characters on line {i}: {bad}")
    return source

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="package name (or PID with --pid)")
    ap.add_argument("--pid", action="store_true", help="target is a numeric PID")
    ap.add_argument("--spawn", action="store_true",
                    help="spawn the app (catches scripts loaded at startup)")
    ap.add_argument("--host", default="127.0.0.1:31337",
                    help="frida-server TCP address (default: 127.0.0.1:31337 via adb forward)")
    ap.add_argument("--out", default="lua_dump", help="output directory")
    args = ap.parse_args()

    with open(JS_PATH, encoding="utf-8") as f:
        js_source = load_agent(JS_PATH)
        
    # ---- TCP remote device (frida-server -l 0.0.0.0:31337) ----
    manager = frida.get_device_manager()
    device = manager.add_remote_device(args.host)
    print(f"[*] connected to frida-server @ {args.host} ({device.name})")

    dumper = LuaDumper(args.out)

    try:
        if args.spawn:
            pid = device.spawn([args.target])
            session = device.attach(pid)
        else:
            pid = None
            session = device.attach(int(args.target) if args.pid else args.target)

        script = session.create_script(js_source)
        script.on("message", dumper.on_message)
        script.load()

        if pid is not None:
            device.resume(pid)

        print(f"[*] dumping to {args.out}/ — Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            session.detach()
            print(f"[*] done: {dumper.saved} unique chunks in {args.out}/")
    finally:
        try:
            manager.remove_remote_device(device)
        except Exception:
            pass


if __name__ == "__main__":
    main()