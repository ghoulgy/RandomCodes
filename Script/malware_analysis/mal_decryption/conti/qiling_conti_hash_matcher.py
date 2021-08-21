# Conti Ransomware
import json
import pefile
from qiling import *

# Hashes collected from the malware
sample_hashes =["0xd52132a3", "0xf701962c", "0x6a095e21", "0xdf1af05e", "0x5d48fbaf", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0xbe3d21a8", "0x5fa07416", "0xf06e87ca", "0x1b1acbcc", "0x269e9ef4", "0xb9072e66", "0x92f9234b", "0xf955c4d0", "0xf955c4d0", "0xa5eb6e47", "0xa5eb6e47", "0x2bdbdf4e", "0xcc12507f", "0xd3a7a468", "0xb32feeec", "0xdf1af05e", "0xb32feeec", "0xe6bc0210", "0x5243a16a", "0xeedec24b", "0xe6bc0210", "0xde5dbfdc", "0xd3a7a468", "0xe6bc0210", "0xe6bc0210", "0x1972bf90", "0x78ee4dfa", "0xeedec24b", "0xd3a7a468", "0x4d9702d0", "0x7324a0a2", "0x6a095e21", "0xa5eb6e47", "0xa5eb6e47", "0x1b99344d", "0x1b99344d", "0x2ffbe59f", "0x2ffbe59f", "0xc88071b1", "0x21cca665", "0xc45f4a8c", "0xc45f4a8c", "0xc45f4a8c", "0xf99eabb9", "0xc7dfa7fc", "0xd72e57a9", "0xd72e57a9", "0xd72e57a9", "0xd72e57a9", "0xd72e57a9", "0x5d48fbaf", "0xf06e87ca", "0xa897e98d", "0xd72e57a9", "0x2ffbe59f", "0x68da023e", "0x2ffbe59f", "0x68da023e", "0xaf724aac", "0x5d48fbaf", "0x57b499e3", "0x3a4532be", "0x3a4532be", "0x441bdf1e", "0x6a095e21", "0x6a095e21", "0xf4241d9a", "0xa5eb6e47", "0xa5eb6e47", "0xa5eb6e47", "0x9812c1b7", "0x1260d6db", "0xbd6ac662", "0xe558706f", "0x1ad64c3e", "0x4118bcd2", "0xbf983c41", "0x1fbbb84f", "0xbf983c41", "0x1fbbb84f", "0xcc37b4cb", "0x6877b7f6", "0x6877b7f6", "0x6877b7f6", "0x6877b7f6", "0x5dacc2ba", "0x21cca665", "0xf99eabb9", "0xb96fdcc6", "0x9209ce83", "0xa5eb6e47", "0xd72e57a9", "0xa9a24646", "0xa5eb6e47", "0x5d48fbaf", "0x3a4532be", "0x21cca665", "0xf99eabb9", "0x21cca665", "0xf99eabb9", "0x1d7ab241", "0x5a8ce5b8", "0x5a8ce5b8", "0xc45f4a8c", "0xb5e437b0", "0x2ad410e3", "0xbbd8bcb8", "0x7d154065", "0xbbd8bcb8", "0x663b63f4", "0x31d910df", "0x22cb760f", "0x7d154065", "0x7d154065", "0x7d154065", "0xd54e6bd3", "0x1fbbb84f", "0x1fbbb84f", "0x1fbbb84f", "0xede8a61e", "0xd54e6bd3", "0x1fbbb84f", "0x93afb23a", "0xa62cc8e1", "0xf06e87ca", "0x1fbbb84f", "0x1fbbb84f", "0xf06e87ca", "0x1fbbb84f", "0x1fbbb84f", "0x1b1acbcc", "0x1fbbb84f", "0xf91ac9a0", "0xd54e6bd3", "0xabcb0a67", "0xabcb0a67", "0x6c6c937b", "0xf91ac9a0", "0xd54e6bd3", "0xa5eb6e47", "0x4d9702d0", "0x7ba2639", "0xc8fb7817", "0xa5eb6e47", "0x1fbbb84f", "0x5a8ce5b8", "0x5a8ce5b8", "0x5a8ce5b8", "0xf06e87ca", "0xc65c5ee6", "0xc45f4a8c", "0xa5eb6e47", "0xe2b40f85", "0x1fbbb84f", "0x397b11df", "0x397b11df", "0x9aea18e1", "0x75fcf770", "0x1668d771", "0xd72e57a9", "0x4d9702d0", "0x7ba2639", "0x7ba2639", "0x7ba2639", "0xa1f2bf63", "0x21cca665", "0xf99eabb9", "0xe4b69f3b", "0x21cca665", "0xf99eabb9", "0xb87c8bb7", "0x55710126", "0xe558706f", "0xa0ee5aad", "0x4310229a", "0x4118bcd2", "0xa0ee5aad", "0x57b499e3", "0x4118bcd2", "0xa0ee5aad", "0xf05ad6da", "0xb87c8bb7", "0xcd976938", "0x87b69cc9", "0x55d15957", "0xe34ea561", "0x61856121", "0x4118bcd2", "0xa0ee5aad", "0x19515ab5", "0x61856121", "0x4118bcd2", "0xa0ee5aad", "0x87b69cc9", "0xb87c8bb7", "0xaf17f6da", "0xb87c8bb7", "0x5cc1ccbc", "0x5cc1ccbc", "0x5cc1ccbc", "0x5cc1ccbc", "0xb87c8bb7", "0xa247ff77", "0xb87c8bb7", "0xb87c8bb7", "0x21cca665", "0xf99eabb9", "0xe4b69f3b", "0xf99eabb9", "0xb87c8bb7", "0xd54e6bd3", "0xf91ac9a0", "0xd54e6bd3", "0x441bdf1e"]

dlls_name = [
    # "oleaut32.dll",
    # "iphlpapi.dll",
    # "kernel32.dll",
    "RstrtMgr.dll",
]
# dlls_name = [
    # "shell32.dll",
    # "netapi32.dll",
    # "advapi32.dll",
    # "shlwapi.dll",
    # "ws2_32.dll",
    # "user32.dll",
    # "ole32.dll"
# ]

match_func_hash_dict = {}

def my_sandbox(path, rootfs):
    ql = Qiling(path, rootfs, console=False, output="off")
    
    # Allocate memory in ecx so in can be assign with a function name
    ql.mem.map(ql.reg.ecx//4096*4096, 4096)
    
    for dll_name in dlls_name:
        print(dll_name)
        pe = pefile.PE(dll_name)

        try:
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if ql.mem.is_mapped(ql.reg.ecx//4096*4096, 4096) == False: 
                    ql.mem.map(ql.reg.ecx//4096*4096, 4096)
                
                if exp.name is not None:
                    func_name = exp.name.decode()
                    # Filter for shell32.dll
                    if "CreateStorageItem" in func_name:
                        continue

                    # _cdecl call: edx, ecx, stack as args
                    ql.mem.string(ql.reg.ecx, func_name)
                    ql.reg.edx = len(func_name)

                    # Function for hash calculation
                    ql.run(begin=0x405970, end=0x405ab4)
                    # Return eax as calculated hash value from the string function given
                    for sample_hash in sample_hashes:
                        if hex(ql.reg.eax) == sample_hash:
                            match_func_hash_dict.update({hex(ql.reg.eax): func_name})
        except:
            print(f"{func_name} error")

    # Print all the matched hash<->func_name as json dump and save it into a file
    with open('data2.json', 'w', encoding='utf-8') as of:
        json.dump(match_func_hash_dict, of, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    my_sandbox(["unpacked_conti.exe"], "~/Desktop/qiling/examples/rootfs/x86_windows")
