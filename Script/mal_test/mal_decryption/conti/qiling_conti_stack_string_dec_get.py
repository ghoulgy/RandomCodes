# Conti Ransomware
from qiling import *

# Get decrypted stack strings in the buffer 
def get_dec_str(ql):
	print(ql.mem.read(ql.reg.ebp+ql.reg.ecx-0xbc, 0xb8).decode())
	ql.emu_stop()

def my_sandbox(path, rootfs):
    ql = Qiling(path, rootfs, console=False, output="off")

    # hook 0x404e5a 
    # End of the stack string decryption loop so we can get all the previous decrypted strings
    ql.hook_address(get_dec_str, 0x404e5a)

    # Function for hash calculation
    ql.run(begin=0x404940, end=0x404e64)


if __name__ == "__main__":
    my_sandbox(["hahaha.exe"], "/home/lol/Desktop/qiling/examples/rootfs/x86_windows")

'''
"OleAut32.dll",
"Iphlpapi.dll",
"Kernel32.dll",
"Shell32.dll",
"Rstrtmgr.dll",
"Netapi32.dll",
"Advapi32.dll",
"Shlwapi.dll",
"ws2_32.dll",
"User32.dll",
"Ole32.dll",
'''
