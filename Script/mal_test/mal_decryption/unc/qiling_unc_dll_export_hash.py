# Shellcode from UNC in-memory malware loader
import pefile
from qiling import *

class custom_hash_dll_func_name:
    def __init__(self, ql, shellcode):
        self.ql = ql
        self.shellcode = shellcode

    def main_process(self, dll_name, result_hash):
        is_found = False
        pe = pefile.PE(dll_name)
        hash_dll_name = self._calc_name_dll_hash(dll_name)

        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name is not None:
                hash_func_name = self._calc_name_func_hash(exp.name)

                if self._calc_sum_of_hash(hash_dll_name, hash_func_name) == result_hash:
                    print(f"Found!!! {dll_name}, {exp.name.decode()}, {result_hash}")
                    is_found = True
                    break
                else:
                    is_found = False

        return is_found


    def _calc_sum_of_hash(self, hdn, hfn):
        sum_of_hash = hex(hdn + hfn).lstrip("0x")
        if (len(sum_of_hash) > 8):
            sum_of_hash = sum_of_hash[1:]
        sum_of_hash = "0x" + sum_of_hash
        # print(f"Sum of hash: {sum_of_hash}")
        return sum_of_hash


    def _calc_name_dll_hash(self, dll_name):
        dll_name_fmt = b''
        for n in dll_name:
            dll_name_fmt += n.encode() + b"\x00"
        dll_name_fmt += b"\x00\x00"
        # e.g dll_name_fmt = "A\x00D\x00V\x00A\x00P\x00I\x003\x002\x00.\x00d\x00l\x00l\x00\x00\x00"

        hash_dll_name = 0
        for int_chr in dll_name_fmt:
            if int_chr > 0x61:
                 int_chr = int_chr - 0x20         # Convert to capital letter

            self.ql.reg.eax = hash_dll_name
            self.ql.run()

            hash_dll_name = self.ql.reg.eax
            hash_dll_name += int_chr

        # print(f"{dll_name_fmt.decode()}: {hex(hash_dll_name)}")
        return hash_dll_name


    def _calc_name_func_hash(self, lib_func):
        lib_func += b"\x00"
        hash_func_name = 0

        for int_chr in lib_func:
            self.ql.reg.eax = hash_func_name
            self.ql.run()

            hash_func_name = self.ql.reg.eax
            hash_func_name += int_chr

        # print(f"{lib_func}: {hex(hash_func_name)}")
        return hash_func_name


def main():
    shellcode = b"\xC1\xC8\x0D" # ror eax, 0xD
    ql = Qiling(shellcoder=shellcode,
                rootfs="/qiling/examples/rootfs/x86_windows",
                ostype="windows",
                archtype="x86",
                console=False)

    dll_name_list = ["wininet.dll", "kernel32.dll"]
    func_hash_list = ["0xc69f8957", "0x3b2e55eb", "0x869e4675", "0x7b18062d", "0x5de2c5aa", 
        "0x315e2145", "0x0be057b7", "0x56a2b5f0", "0xe553a458", "0xe2899612", ]

    chdfn = custom_hash_dll_func_name(ql, shellcode)
    total_hash_found = 0
    total_func_hash_list = len(func_hash_list)
    print(f"Total func hash count: {total_func_hash_list}")
    for dll_name in dll_name_list:
        found_hash_list = []

        for func_hash in func_hash_list:
            bool_found = chdfn.main_process(dll_name, func_hash)
            if bool_found:
                found_hash_list.append(func_hash)
                total_hash_found += 1

        # Remove founded hash
        if len(found_hash_list) > 0:
            for founded in found_hash_list:
                func_hash_list.remove(founded)


    print(f"Found {total_hash_found} out of {total_func_hash_list}")


if __name__ == "__main__":
    main()

'''
Found!!! wininet.dll, InternetConnectA, 0xc69f8957
Found!!! wininet.dll, HttpOpenRequestA, 0x3b2e55eb
Found!!! wininet.dll, InternetSetOptionA, 0x869e4675
Found!!! wininet.dll, HttpSendRequestA, 0x7b18062d
Found!!! wininet.dll, InternetErrorDlg, 0x0be057b7
Found!!! wininet.dll, InternetReadFile, 0xe2899612
Found!!! kernel32.dll, GetLastError, 0x5de2c5aa
Found!!! kernel32.dll, ExitProcess, 0x56a2b5f0
Found!!! kernel32.dll, VirtualAlloc, 0xe553a458

'''