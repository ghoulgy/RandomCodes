// Get what kind of lib so file loaded by libnesec.so
function monitorNesecLoads() {
    const TARGET_CALLER = "libnesec.so";
    
    console.log(`[*] 开始监控由 ${TARGET_CALLER} 发起的动态加载 (无 Module 依赖版)...`);

    // 核心 Hook 逻辑
    function attachHook(funcName, funcPtr, isInternal = false) {
        if (!funcPtr) return;

        Interceptor.attach(funcPtr, {
            onEnter: function(args) {
                this.libName = null;
                this.callerAddr = this.returnAddress; 
                
                if (!args[0].isNull()) {
                    try {
                        this.libName = args[0].readCString();
                    } catch (e) {
                        // 忽略无效的内存地址读取错误
                    }
                }
            },
            onLeave: function(retval) {
                if (this.libName && this.callerAddr) {
                    let callerModule = null;
                    try {
                        callerModule = Process.findModuleByAddress(this.callerAddr);
                    } catch(e) {}
                    
                    if (callerModule && callerModule.name === TARGET_CALLER) {
                        const offset = this.callerAddr.sub(callerModule.base);
                        
                        console.log(`\n[!] 发现 ${TARGET_CALLER} 加载了动态库:`);
                        console.log(`    -> 目标库名: ${this.libName}`);
                        console.log(`    -> 调用指令偏移: 0x${offset.toString(16)} (位于 ${TARGET_CALLER} 内部)`);
                        console.log(`    -> 使用的 API: ${funcName} ${isInternal ? "(底层强制拦截)" : ""}`);
                        
                        if (!retval.isNull()) {
                            const shortName = this.libName.split('/').pop();
                            let loadedModule = null;
                            try {
                                loadedModule = Process.findModuleByName(shortName);
                            } catch(e) {}
                            
                            if (loadedModule) {
                                console.log(`    -> 加载成功! 新库基址: ${loadedModule.base}`);
                                
                                // === NEW CODE: Dump first 0x40 bytes ===
                                try {
                                    console.log(`    -> [ELF Header Dump] First 0x40 bytes at ${loadedModule.base}:`);
                                    console.log(hexdump(loadedModule.base, {
                                        offset: 0,
                                        length: 0x40,
                                        header: true,
                                        ansi: true // Set to false if your terminal doesn't support colors
                                    }));
                                } catch (readErr) {
                                    console.log(`    -> [!] 无法读取 ELF 头部内存: ${readErr}`);
                                }
                                // =======================================

                            } else {
                                console.log(`    -> 加载成功! (返回句柄: ${retval})`);
                            }
                        } else {
                            console.log(`    -> 加载失败 (返回 null)!`);
                        }
                    }
                }
            }
        });
        console.log(`[+] 成功挂载 Hook: ${funcName} @ ${funcPtr}`);
    }

    // ==========================================
    // 替代 Module.findExportByName 的自定义查找函数
    // ==========================================
    function getSymbolAddress(funcName) {
        // Android 中的 dlopen 通常导出在 libdl.so 或 libc.so 中
        const targetLibs = ["libdl.so", "libc.so"];
        
        for (let i = 0; i < targetLibs.length; i++) {
            const mod = Process.findModuleByName(targetLibs[i]);
            if (mod) {
                const exports = mod.enumerateExports();
                for (let j = 0; j < exports.length; j++) {
                    if (exports[j].name === funcName) {
                        return exports[j].address;
                    }
                }
            }
        }
        return null;
    }

    // 1. 手动查找并 Hook 标准的 dlopen API
    const stdDlopen = getSymbolAddress("dlopen");
    if (stdDlopen) attachHook("dlopen", stdDlopen);

    const stdDlopenExt = getSymbolAddress("android_dlopen_ext");
    if (stdDlopenExt) attachHook("android_dlopen_ext", stdDlopenExt);

    // 2. 遍历底层 Linker，强行找出并未公开的 do_dlopen 进行 Hook
    const linkerName = Process.pointerSize === 8 ? "linker64" : "linker";
    const linkerModule = Process.findModuleByName(linkerName);
    
    if (linkerModule) {
        let foundInternal = false;
        const exports = linkerModule.enumerateExports();
        
        for (let i = 0; i < exports.length; i++) {
            if (exports[i].name.indexOf("do_dlopen") !== -1) {
                attachHook(exports[i].name, exports[i].address, true);
                foundInternal = true;
            }
        }
        
        if (!foundInternal) {
            console.log(`[-] 在 ${linkerName} 中未找到底层的 do_dlopen 符号。`);
        }
    } else {
        console.log(`[-] 未能找到 ${linkerName} 模块。`);
    }
}

setImmediate(monitorNesecLoads);