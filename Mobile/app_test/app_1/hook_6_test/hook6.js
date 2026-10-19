'use strict';

const DEX_PATTERN  = '64 65 78 0a 30 ?? ?? 00';   // "dex\n0XX\0"
const META_PATTERN = 'af 1b b1 fa';               // 0xFAB11BAF little-endian
const MAX_DEX  = 100 * 1024 * 1024;
const MAX_META = 256 * 1024 * 1024;
const seen = new Set();
const jniHooked = new Set();

let scanJob = null, pendingTag = null;

/* ------------------------------------------------ helpers */
function findModule(name) {
  try { const m = Process.findModuleByName(name); if (m) return m; } catch (e) {}
  const lower = name.toLowerCase();
  const mods = Process.enumerateModules();
  for (let i = 0; i < mods.length; i++)
    if (mods[i].name.toLowerCase() === lower) return mods[i];
  return null;
}

function findGlobalExport(name) {
  try {
    if (typeof Module.findGlobalExportByName === 'function') {
      const a = Module.findGlobalExportByName(name); if (a) return a;
    }
  } catch (e) {}
  try { const a = Module.findExportByName(null, name); if (a) return a; } catch (e) {}
  return null;
}

/* ------------------------------------------------ dex dumping (unchanged logic) */
function dumpDex(base, sizeHint, tag, rangeEnd) {
  if (base === null || base.isNull()) return;
  let magic = null;
  try { magic = base.readByteArray(4); } catch (e) { return; }
  if (magic === null) return;
  const b = new Uint8Array(magic);
  if (b[0] !== 0x64 || b[1] !== 0x65 || b[2] !== 0x78 || b[3] !== 0x0a) return;

  let avail = 0;
  if (rangeEnd) {
    try { avail = parseInt(rangeEnd.sub(base).toString(), 16); } catch (e) {}
  }

  let fileSize = 0;
  try { fileSize = base.add(0x20).readU32(); } catch (e) {}

  let total;
  if (fileSize >= 0x70 && fileSize <= MAX_DEX) {
    total = fileSize;
    if (sizeHint > total && sizeHint <= MAX_DEX) total = sizeHint;
  } else {
    total = Math.min(avail || sizeHint || 0, MAX_DEX);
  }
  if (total < 0x70) return;
  if (avail > 0) total = Math.min(total, avail);

  const key = 'dex:' + base.toString() + ':' + total;
  if (seen.has(key)) return;
  seen.add(key);

  console.log('[+] ' + tag + ' DEX @ ' + base + ' size=' + total);
  try {
    send({ type: 'dex_dump', base: base.toString(), size: total },
         base.readByteArray(total));
  } catch (e) {
    console.log('[-] dex read failed @ ' + base + ': ' + e.message);
  }
}

/* ------------------------------------------------ global-metadata dumping (NEW) */
function dumpMetadata(base, tag, rangeEnd) {
  if (base === null || base.isNull()) return;

  // pattern already confirmed the magic; version field is the false-positive filter
  let ver = 0;
  try { ver = base.add(4).readU32(); } catch (e) { return; }
  if (ver < 10 || ver > 60) return;                 // real metadata versions: ~16..31

  const key = 'meta:' + base.toString();
  if (seen.has(key)) return;
  seen.add(key);

  let total = 0;
  if (rangeEnd) {
    try { total = parseInt(rangeEnd.sub(base).toString(), 16); } catch (e) {}
  }
  if (total < 0x1000) return;                       // too small to be metadata
  total = Math.min(total, MAX_META);

  console.log('[+] ' + tag + ' global-metadata v' + ver + ' @ ' + base +
              ' (up to ' + (total / 1048576).toFixed(1) + 'MB of mapping)');
  try {
    send({ type: 'meta_dump', base: base.toString(), version: ver, size: total },
         base.readByteArray(total));
  } catch (e) {
    console.log('[-] meta read failed @ ' + base + ': ' + e.message);
  }
}

/* ------------------------------------------------ chunked scanner, dual pattern */
const SLICE = 16 * 1024 * 1024;   // scan this much per event-loop turn
const CHUNK = 32 * 1024 * 1024;   // piece size inside one (huge) range

function scanAll(tag) {
  if (scanJob) { pendingTag = tag; return; }
  let all = [];
  try { all = Process.enumerateRanges('r--'); } catch (e) { return; }
  const ranges = [];
  for (let i = 0; i < all.length; i++) {
    const r = all[i];
    if (r.size < 0x70) continue;
    if (r.file && r.file.path) {
      const p = r.file.path;
      // skip system libs + the APK itself (on-disk metadata there is encrypted)
      if (p.indexOf('/system/') === 0 || p.indexOf('/apex/') === 0 ||
          p.indexOf('/vendor/') === 0 || p.indexOf('/data/app/') === 0) continue;
    }
    ranges.push(r);
  }
  scanJob = { ranges: ranges, idx: 0, off: 0, hits: 0, metaHits: 0, bytes: 0,
              tag: tag, t0: Date.now(), lastLog: Date.now() };
  setTimeout(scanSlice, 0);
}

function scanSlice() {
  const q = scanJob;
  if (!q) return;
  let budget = SLICE;
  while (q.idx < q.ranges.length && budget > 0) {
    const r = q.ranges[q.idx];
    const len = Math.min(CHUNK + 16, r.size - q.off);   // +16 = pattern overlap
    const start = r.base.add(q.off);
    const rangeEnd = r.base.add(r.size);

    let ms = [], mmeta = [];
    try { ms = Memory.scanSync(start, len, DEX_PATTERN); } catch (e) {}
    try { mmeta = Memory.scanSync(start, len, META_PATTERN); } catch (e) {}

    q.bytes += len; budget -= len; q.off += CHUNK;

    for (let j = 0; j < ms.length; j++) {
      q.hits++;
      dumpDex(ms[j].address, 0, 'scan:' + q.tag, rangeEnd);
    }
    for (let j = 0; j < mmeta.length; j++) {
      q.metaHits++;
      dumpMetadata(mmeta[j].address, 'scan:' + q.tag, rangeEnd);
    }

    if (q.off >= r.size) { q.idx++; q.off = 0; }
  }
  if (Date.now() - q.lastLog > 5000) {
    q.lastLog = Date.now();
    console.log('[scan:' + q.tag + '] ...' + q.idx + '/' + q.ranges.length +
                ' ranges, ' + (q.bytes / 1048576).toFixed(0) + 'MB, ' +
                q.hits + ' dex / ' + q.metaHits + ' meta candidates');
  }
  if (q.idx < q.ranges.length) { setTimeout(scanSlice, 0); return; }   // yield
  console.log('[scan:' + q.tag + '] DONE — ' + q.hits + ' dex, ' + q.metaHits +
              ' meta candidates, ' + (q.bytes / 1048576).toFixed(0) + 'MB in ' +
              ((Date.now() - q.t0) / 1000).toFixed(1) + 's');
  scanJob = null;
  if (pendingTag) {
    const t = pendingTag; pendingTag = null;
    setTimeout(function () { scanAll('event:' + t); }, 500);
  }
}

function scheduleScan(tag) {
  if (scanJob) { pendingTag = tag; return; }        // busy -> rerun after current
  if (pendingTag) { pendingTag = tag; return; }     // already scheduled -> coalesce
  pendingTag = tag;
  setTimeout(function () {
    const t = pendingTag; pendingTag = null;
    scanAll('event:' + t);
  }, 800);
}

/* ------------------------------------------------ native event triggers */
function hookLoaders() {
  const hookedAddrs = new Set();
  ['dlopen', 'android_dlopen_ext', '__loader_dlopen', '__loader_android_dlopen_ext']
  .forEach(function (name) {
    const addr = findGlobalExport(name);
    if (!addr || hookedAddrs.has(addr.toString())) return;
    hookedAddrs.add(addr.toString());
    try {
      Interceptor.attach(addr, {
        onEnter: function (args) {
          this.path = args[0].isNull() ? '' : (args[0].readCString() || '');
        },
        onLeave: function (retval) {
          if (retval.isNull()) return;
          const p = this.path;
          if (!p || !/\.so$/i.test(p)) return;
          if (p.indexOf('/system/') === 0 || p.indexOf('/apex/') === 0 ||
              p.indexOf('/vendor/') === 0) return;
          console.log('[dlopen] ' + p);
          hookJniOnLoad(p);
          scheduleScan('dlopen');
        }
      });
      console.log('[*] hooked ' + name);
    } catch (e) {}
  });
}

function hookJniOnLoad(path) {
  const mod = findModule(path.substring(path.lastIndexOf('/') + 1));
  if (!mod) return;
  let jni = null;
  try { jni = mod.findExportByName('JNI_OnLoad'); } catch (e) {}
  if (!jni || jni.isNull()) return;
  const key = jni.toString();
  if (jniHooked.has(key)) return;
  jniHooked.add(key);
  try {
    Interceptor.attach(jni, {
      onLeave: function () {
        console.log('[*] JNI_OnLoad(' + mod.name + ') returned -> scanning');
        scheduleScan('JNI_OnLoad');
      }
    });
    console.log('[*] hooked JNI_OnLoad in ' + mod.name);
  } catch (e) {}
}

/* packers hand the decrypted payload to the loader via memfd — high-value trigger */
function hookMemfd() {
  const addr = findGlobalExport('memfd_create');
  if (!addr) return;
  try {
    Interceptor.attach(addr, {
      onEnter: function (a) { this.name = a[0].isNull() ? '' : a[0].readCString(); },
      onLeave: function (rv) {
        if (!rv.isNull() && rv.toInt32() >= 0) {
          console.log('[memfd_create] ' + (this.name || '(null)') + ' -> fd ' + rv.toInt32());
          scheduleScan('memfd');
        }
      }
    });
    console.log('[*] hooked memfd_create');
  } catch (e) {}
}

/* ------------------------------------------------ ART choke points (bonus) */
function hookArtLoader() {
  const libart = findModule('libart.so');
  if (!libart) { setTimeout(hookArtLoader, 500); return; }

  const wanted = [
    '_ZN3art7DexFile10OpenMemoryE',
    '_ZN3art7DexFile10OpenCommonE',
    '_ZN3art7DexFile4OpenE',
    '_ZN3art13DexFileLoader4OpenE',
    '_ZN3art16ArtDexFileLoader4OpenE',
    '_ZN3art7DexFileC1E',
    '_ZN3art7DexFileC2E'
  ];

  let n = 0;
  libart.enumerateSymbols().forEach(function (sym) {
    if (sym.type !== 'function') return;
    if (!sym.address || sym.address.isNull()) return;
    if (sym.address.compare(libart.base) < 0 ||
        sym.address.compare(libart.base.add(libart.size)) >= 0) return;
    if (!wanted.some(function (p) { return sym.name.indexOf(p) === 0; })) return;

    try {
      Interceptor.attach(sym.address, {
        onEnter: function (args) {
          dumpDex(args[1], 0, sym.name.slice(0, 40));
          dumpDex(args[1], args[2].toUInt32(), sym.name.slice(0, 40));
          dumpDex(args[2], args[3].toUInt32(), sym.name.slice(0, 40));
        }
      });
      console.log('    [art] hooked: ' + sym.name);
      n++;
    } catch (e) {}
  });
  console.log('[*] ART symbol hooks: ' + n);
}

rpc.exports = {
  init: function () {
    hookLoaders();
    hookMemfd();
    hookArtLoader();
    Interceptor.flush();
    return 'armed';
  },
  scan: function (tag) { scanAll(tag || 'rpc'); return 'ok'; }
};

setInterval(function () { console.log('[hb] alive'); }, 10000);