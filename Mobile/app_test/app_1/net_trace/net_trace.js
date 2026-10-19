'use strict';

const GATE_MODULE = 'libtolua.so';
const ENCODE_RVA  = 0x423D0;
const DECODE_RVA  = 0x41ED0;

const Lfn = {};
let gatePassed = false;
let encCount = 0, decCount = 0;

function onGate(mod) {
    if (gatePassed) return;
    gatePassed = true;
    console.log('[gate] ' + mod.name + ' @ ' + mod.base);

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
            if (data !== null) {
                send({ event: 'decode_in', dir: 'in', len: data.byteLength }, data);
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
            
            // Scan the entire stack from top to bottom to find the string
            for (let i = -1; i >= -Math.max(1, top); i--) {
                data = readLuaString(this.L, i);
                if (data !== null) break;
            }

            if (data !== null) {
                send({ event: 'encode_out', dir: 'out', len: data.byteLength }, data);
            } else {
                console.log(`[!] ENCODE_OUT #${encCount} fired, but no string found on stack.`);
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
    console.log('[*] Stack-scanning binary capture initialized');
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