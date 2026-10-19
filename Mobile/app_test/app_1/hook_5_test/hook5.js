var dumpedAddresses = new Set();

function dumpDex(basePtr, argSize, source) {
    if (!basePtr || basePtr.isNull()) return;

    var baseStr = basePtr.toString();
    if (dumpedAddresses.has(baseStr)) return;

    try {
        // Verify DEX magic: "dex\n" (0x64 0x65 0x78 0x0A)
        var magic = basePtr.readByteArray(4);
        var bytes = new Uint8Array(magic);
        if (bytes[0] !== 0x64 || bytes[1] !== 0x65 || bytes[2] !== 0x78 || bytes[3] !== 0x0a) {
            return;
        }

        var headerSize = basePtr.add(0x20).readU32();
        var finalSize = argSize > 0 ? Math.max(headerSize, argSize) : headerSize;

        if (finalSize < 1024 || finalSize > 50 * 1024 * 1024) return;

        console.log(`\n[+] [${source}] DEX Detected at: ${baseStr}`);
        console.log(`    -> Header Size : ${headerSize} bytes (${(headerSize / 1024).toFixed(2)} KB)`);
        console.log(`    -> Dumping     : ${finalSize} bytes...`);

        var dexBuffer = basePtr.readByteArray(finalSize);
        send({
            type: "dex_dump",
            base: baseStr,
            size: finalSize
        }, dexBuffer);

        dumpedAddresses.add(baseStr);
        console.log("[+] Dispatched to PC successfully!\n");
    } catch (e) {
        // Silently skip inaccessible memory pages
    }
}

function hookArtSymbols() {
    var libart = Process.findModuleByName("libart.so");
    if (!libart) {
        setTimeout(hookArtSymbols, 300);
        return;
    }

    console.log("[*] libart.so base: " + libart.base);

    // Use enumerateSymbols() instead of enumerateExports()
    var symbols = libart.enumerateSymbols();
    console.log("[*] Total internal symbols in libart.so: " + symbols.length);

    var hookCount = 0;

    symbols.forEach(function(sym) {
        var name = sym.name;

        // Match OpenCommon, OpenMemory, or DexFile constructors
    var isOpenCommon =  name.indexOf("OpenCommon") !== -1 ||
                        name.indexOf("DexFileLoader") !== -1 ||
                        name.indexOf("DexFileLoader::Open") !== -1 ||
                        name.indexOf("LoadDexFiles") !== -1 ||
                        name.indexOf("OatFileManager") !== -1 ||
                        name.indexOf("DexFile::Open") !== -1;

        var isDexConstructor = name.indexOf("_ZN3art7DexFileC1") !== -1 || name.indexOf("_ZN3art7DexFileC2") !== -1;

        if (isOpenCommon || isDexConstructor) {
            try {
                Interceptor.attach(sym.address, {
                    onEnter: function(args) {
                        for (var i = 0; i < 4; i++) {
                            try {
                                dumpDex(args[i], args[i + 1] ? args[i + 1].toInt32() : 0, name.slice(0, 30));
                            } catch (err) {}
                        }
                    }
                });
                hookCount++;
            } catch (e) {}
        }
    });

    console.log("[*] Placed " + hookCount + " hooks on internal ART loader symbols.");

    // Fallback: If 0 hooks placed or symbols stripped, trigger memory scanning
    if (hookCount === 0) {
        console.log("[-] No visible symbols found in .symtab. Activating memory scanner fallback...");
    }
    
    // Always trigger periodic memory scan to catch dynamically allocated DEX blocks
    setTimeout(scanMemoryForDex, 2000);
    setTimeout(scanMemoryForDex, 5000);
}

function scanMemoryForDex() {
    console.log("[*] Running in-memory DEX signature scan...");
    var ranges = Process.enumerateRanges('r--');

    ranges.forEach(function(range) {
        try {
            // Scan for DEX magic "dex\n035\0"
            Memory.scan(range.base, range.size, "64 65 78 0a 30 ?? ?? 00", {
                onMatch: function(address, size) {
                    var fileSize = address.add(0x20).readU32();
                    dumpDex(address, fileSize, "Memory.scan");
                },
                onError: function() {},
                onComplete: function() {}
            });
        } catch (e) {}
    });
}

setImmediate(hookArtSymbols);