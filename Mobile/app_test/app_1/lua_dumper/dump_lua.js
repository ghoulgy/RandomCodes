'use strict';

// ===================== config =====================
const GATE_MODULE  = 'libil2cpp.so';    // wait for this module, THEN hook
const LOADER_NAMES = ['luaL_loadbuffer', 'luaL_loadbufferx'];
const FILE_NAMES   = ['luaL_loadfile', 'luaL_loadfilex'];
const LUA_RE       = /^(lua|tolua)/i;   // lua_*, luaL_*, tolua_*
const MAX_CHUNK    = 0x4000000;         // 64 MB sanity cap

// ===================== state =====================
const hooked  = new Set();   // addresses already hooked
const scanned = new Set();   // "name@base" of modules already scanned
let gatePassed   = false;
let loadersArmed = 0;

// ===================== hooks =====================
function hookLoader(name, addr, via) {
    const key = addr.toString();
    if (hooked.has(key)) return;
    hooked.add(key);
    if (LOADER_NAMES.indexOf(name) !== -1) loadersArmed++;
    console.log('[+] hooked ' + name + ' @ ' + addr + ' (' + via + ')');

    Interceptor.attach(addr, {
        onEnter(args) {
            // (lua_State* L, const char* buf, size_t size, const char* name [, mode])
            const size = args[2].toInt32();
            if (size <= 0 || size > MAX_CHUNK) return;

            let chunkName = 'unnamed';
            try {
                const s = args[3].readCString();
                if (s) chunkName = s;
            } catch (e) {}

            let data = null;
            try { data = args[1].readByteArray(size); } catch (e) {}
            if (data === null) return;

            send({ event: 'chunk', api: name, name: chunkName, size: size }, data);
        }
    });
}

function hookFileLoader(name, addr, via) {   // log-only: shows file-based loading
    const key = 'file:' + addr.toString();
    if (hooked.has(key)) return;
    hooked.add(key);
    console.log('[+] hooked (log-only) ' + name + ' @ ' + addr + ' (' + via + ')');
    Interceptor.attach(addr, {
        onEnter(args) {
            try { console.log('[loadfile] ' + args[1].readCString()); } catch (e) {}
        }
    });
}

// ===================== module scanning =====================
function scanModule(m) {
    const key = m.name + '@' + m.base;
    if (scanned.has(key)) return;
    scanned.add(key);

    let exports;
    try { exports = m.enumerateExports(); } catch (e) { return; }

    const luaish = [];
    for (let i = 0; i < exports.length; i++) {
        const e = exports[i];
        if (!LUA_RE.test(e.name)) continue;
        luaish.push(e.name);
        if (LOADER_NAMES.indexOf(e.name) !== -1)    hookLoader(e.name, e.address, m.name);
        else if (FILE_NAMES.indexOf(e.name) !== -1) hookFileLoader(e.name, e.address, m.name);
    }
    if (luaish.length > 0) {
        const preview = luaish.slice(0, 10).join(', ') +
            (luaish.length > 10 ? ' ... (+' + (luaish.length - 10) + ')' : '');
        console.log('[scan] ' + m.name + ' -> ' + luaish.length + ' lua-ish exports: ' + preview);
    }
}

// ===================== THE GATE =====================
function onIl2CppLoaded(mod) {
    if (gatePassed) return;
    gatePassed = true;
    console.log('[gate] ' + GATE_MODULE + ' mapped @ ' + mod.base + ' - arming hooks now');

    scanModule(mod);                                // libil2cpp.so itself
    Process.enumerateModules().forEach(scanModule); // plus everything else loaded

    if (loadersArmed === 0) {
        console.log('[!] no lua loader found in any loaded module.');
        console.log('[!] symbols may be stripped/renamed -> next step: RVA hook via Il2CppDumper/IDA');
    }
}

function findLinkerExport(name) {
    try {
        const p = Module.findGlobalExportByName(name);
        if (p !== null) return p;
    } catch (e) {}
    for (const m of Process.enumerateModules()) {
        if (m.name !== 'linker64' && m.name !== 'linker') continue;
        try {
            const p = m.findExportByName(name);
            if (p !== null) return p;
        } catch (e) {}
    }
    return null;
}

// Fallback: watch the dynamic linker itself
function armDlopenGate() {
    const sym = findLinkerExport('android_dlopen_ext') || findLinkerExport('dlopen');
    if (sym === null) {
        console.log('[!] no dlopen symbol found - polling instead');
        const t = setInterval(function () {
            const m = Process.findModuleByName(GATE_MODULE);
            if (m !== null) { clearInterval(t); onIl2CppLoaded(m); }
        }, 250);
        return;
    }
    console.log('[*] dlopen gate armed @ ' + sym);
    Interceptor.attach(sym, {
        onLeave(retval) {
            if (gatePassed || retval.isNull()) return;
            const m = Process.findModuleByName(GATE_MODULE);
            if (m !== null) onIl2CppLoaded(m);
        }
    });
}

// ===================== main =====================
(function main() {
    const m = Process.findModuleByName(GATE_MODULE);
    if (m !== null) {
        console.log('[*] ' + GATE_MODULE + ' already loaded @ ' + m.base);
        onIl2CppLoaded(m);
    } else {
        console.log('[*] ' + GATE_MODULE + ' not mapped yet - waiting...');
        let observerOk = false;
        try {
            Process.attachModuleObserver({
                onAdded(module) {
                    if (module.name === GATE_MODULE) onIl2CppLoaded(module);
                    else if (gatePassed)             scanModule(module);
                },
                onRemoved(module) {}
            });
            observerOk = true;
            console.log('[*] module observer armed');
        } catch (e) {
            console.log('[!] module observer unavailable: ' + e);
        }
        if (!observerOk) armDlopenGate();
    }
})();