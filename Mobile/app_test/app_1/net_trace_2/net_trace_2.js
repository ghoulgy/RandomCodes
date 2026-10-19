'use strict';

const GATE_MODULE = 'libtolua.so';
const ENCODE_RVA  = 0x423D0;
const DECODE_RVA  = 0x41ED0;

// Proto pre-filter. The host (net_trace_2.py) replaces the placeholder with
// JSON before loading this script, e.g.:
//   {"skipIds":[16,230],"knownIds":[1,2,3, ...],"dropHeaderOnly":true}
//   skipIds        - protocol tags to drop outright
//   knownIds       - all known protocol tags (used by dropHeaderOnly)
//   dropHeaderOnly - drop keepalive-style messages that are only a package
//                    header (no body) with no recognizable proto id
const FILTER = __FILTER__;
const SKIP_IDS = new Set(FILTER.skipIds);
const KNOWN_IDS = new Set(FILTER.knownIds);

const Lfn = {};
let gatePassed = false;
let encCount = 0, decCount = 0;
let msgSeq = 0;

function u16(b, o) { return b[o] | (b[o + 1] << 8); }
function u32(b, o) { return (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16) | (b[o + 3] << 24)) >>> 0; }

// Parse a sproto package header. Returns { typeId, headerOnly } or null.
function scanPackage(b, len) {
    const n = u16(b, 0);
    if (n === 0 || n > 64) return null;
    if (2 + n * 2 > len) return null;
    let lastTag = -1;
    let dptr = 2 + n * 2;
    let typeId = null;
    for (let i = 0; i < n; i++) {
        const e = u16(b, 2 + i * 2);
        let tag;
        if (e & 1) {
            tag = lastTag + 1 + (e >> 1);            // nil (field absent)
        } else {
            const bits = e >> 1;
            tag = lastTag + 1;
            if (bits > 0) {
                if (tag === 0) typeId = bits - 1;    // 'type' as embedded int
            } else {
                if (dptr + 4 > len) return null;
                const sz = u32(b, dptr);
                if (tag === 0) {
                    if (sz !== 4 || dptr + 8 > len) return null;
                    typeId = u32(b, dptr + 4);       // 'type' as 4-byte int
                    dptr += 8;
                } else {
                    dptr += 4 + sz;
                    if (dptr > len) return null;
                }
            }
        }
        lastTag = tag;
    }
    return { typeId: typeId, headerOnly: dptr >= len };
}

function isSkipped(data) {
    if (data === null || data.byteLength < 2) return false;
    if (SKIP_IDS.size === 0 && !FILTER.dropHeaderOnly) return false;
    const b = new Uint8Array(data);
    const len = b.length;

    // 1. RPC envelope: 2 index entries, field0 size 4 -> proto id @ offset 10
    if (len >= 18 && u16(b, 0) === 2 && u32(b, 6) === 4) {
        const id = u32(b, 10);
        if (SKIP_IDS.has(id) || SKIP_IDS.has(id & 0xFFFF) || SKIP_IDS.has((id >>> 16) & 0xFFFF))
            return true;
    }

    // 2. package header (an envelope-shaped buffer parses the same way)
    const pkg = scanPackage(b, len);
    if (pkg !== null) {
        if (pkg.typeId !== null && SKIP_IDS.has(pkg.typeId)) return true;
        if (FILTER.dropHeaderOnly && pkg.headerOnly &&
                (pkg.typeId === null || !KNOWN_IDS.has(pkg.typeId)))
            return true;
    }
    return false;
}

function onGate(mod) {
    if (gatePassed) return;
    gatePassed = true;
    console.log('[gate] ' + mod.name + ' @ ' + mod.base);
    if (SKIP_IDS.size > 0 || FILTER.dropHeaderOnly)
        console.log('[skip] hook-side pre-filter: ' + SKIP_IDS.size + ' proto id(s)' +
                    (FILTER.dropHeaderOnly ? ' + header-only (package)' : ''));

    const map = {};
    let exps = [];
    try { exps = mod.enumerateExports(); } catch (e) { return; }
    for (let i = 0; i < exps.length; i++) map[exps[i].name] = exps[i].address;

    const need = [
        ['lua_tolstring', 'pointer', ['pointer', 'int', 'pointer']],
        ['lua_type',      'int',     ['pointer', 'int']],
        ['lua_gettop',    'int',     ['pointer']],
    ];
    for (let i = 0; i < need.length; i++) {
        const a = map[need[i][0]];
        if (a !== undefined)
            Lfn[need[i][0]] = new NativeFunction(a, need[i][1], need[i][2]);
    }

    Interceptor.attach(mod.base.add(DECODE_RVA), {
        onEnter: function (args) {
            decCount++;
            const data = readLuaString(args[0], 2);
            if (data !== null && !isSkipped(data)) {
                send({ event: 'decode_in', dir: 'in', len: data.byteLength, n: decCount, seq: ++msgSeq, ts: Date.now() }, data);
            }
        }
    });

    Interceptor.attach(mod.base.add(ENCODE_RVA), {
        onEnter: function (args) {
            encCount++;
            this.L = args[0];
        },
        onLeave: function (retval) {
            let data = null;
            let top = 1;
            try { top = Lfn.lua_gettop(this.L); } catch (e) {}

            for (let i = -1; i >= -Math.max(1, top); i--) {
                data = readLuaString(this.L, i);
                if (data !== null) break;
            }

            if (data !== null && !isSkipped(data)) {
                send({ event: 'encode_out', dir: 'out', len: data.byteLength, n: encCount, seq: ++msgSeq, ts: Date.now() }, data);
            }
        }
    });
}

function readLuaString(L, idx) {
    if (Lfn.lua_tolstring === undefined) return null;
    let t = -2;
    try { t = Lfn.lua_type(L, idx); } catch (e) { return null; }
    if (t !== 4 && t !== 7) return null;
    const lenBuf = Memory.alloc(8);
    let ptr = null;
    try { ptr = Lfn.lua_tolstring(L, idx, lenBuf); } catch (e) { return null; }
    if (ptr === null || ptr.isNull()) return null;
    const len = Process.pointerSize === 4 ? lenBuf.readU32() : lenBuf.readU64().toNumber();
    if (len <= 0 || len > 0x1000000) return null;
    try { return ptr.readByteArray(len); } catch (e) { return null; }
}

(function main() {
    console.log('[*] Sproto Lua-layer capture initialized');

    const m = Process.findModuleByName(GATE_MODULE);
    if (m !== null) { onGate(m); return; }
    try {
        Process.attachModuleObserver({
            onAdded: function (module) { if (module.name === GATE_MODULE) onGate(module); },
            onRemoved: function (module) {}
        });
    } catch (e) {}
    const t = setInterval(function () {
        const mm = Process.findModuleByName(GATE_MODULE);
        if (mm !== null) { clearInterval(t); onGate(mm); }
    }, 250);
})();