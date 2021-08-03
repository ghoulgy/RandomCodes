import os
import struct
import shutil

dll_loaded_addr_dict = {
	"iphlpapi.dll": "000007FEFB720000",
	"kernelbase.dll": "000007FEFDC90000",
	"advapi32.dll": "000007FEFDFB0000",
	"bcrypt.dll": "000007FEFD4F0000",
	"crypt32.dll": "000007FEFDDE0000",
	"gdi32.dll": "000007FEFFDA0000",
	"imm32.dll": "000007FEFFD70000",
	"kernel32.dll": "0000000077A70000",
	"lpk.dll": "000007FEFFA60000",
	"msasn1.dll": "000007FEFDC80000",
	"msctf.dll": "000007FEFFC10000",
	"msvcrt.dll": "000007FEFE7C0000",
	"ncrypt.dll": "000007FEFD5D0000",
	"nsi.dll": "000007FEFF850000",
	"ntdll.dll": "0000000077C90000",
	"ole32.dll": "000007FEFE470000",
	"oleaut32.dll": "000007FEFFB30000",
	"profapi.dll": "000007FEFDBE0000",
	"rpcrt4.dll": "000007FEFF860000",
	"sechost.dll": "000007FEFE680000",
	"shell32.dll": "000007FEFEAC0000",
	"shlwapi.dll": "000007FEFEA40000",
	"user32.dll": "0000000077B90000",
	"userenv.dll": "000007FEFCF30000",
	"usp10.dll": "000007FEFF990000",
	"webio.dll": "000007FEFADF0000",
	"wer.dll": "000007FEF66D0000",
	"winhttp.dll": "000007FEFAE70000",
	"winnsi.dll": "000007FEFB710000",
	"ws2_32.dll": "000007FEFFD20000",
}

def mod_pe_imagebase_addr(file, new_imagebase_addr):
	new_imagebase_addr = bytearray.fromhex(new_imagebase_addr)

	pe_binary_mod = open("modded_" + file, "wb")

	pe_binary = open(file ,"rb")
	pe_content = pe_binary.read()
	pe_byte_array = bytearray(pe_content)
	ptr_elfanew = pe_byte_array[0x3c:0x40]
	elfanew_val = struct.unpack("<I", ptr_elfanew)[0]
	print(f"[+] elfanew value: {hex(elfanew_val)}")
	ptr_imagebase = elfanew_val + 0x30
	print(f"[+] Imagebase value: {pe_byte_array[ptr_imagebase:ptr_imagebase + 0x8]}")
	print(f'[+] Before: {hex(struct.unpack("<q", pe_byte_array[ptr_imagebase:ptr_imagebase + 0x8])[0])}')
	new_imagebase_addr.reverse()
	pe_byte_array[ptr_imagebase:ptr_imagebase + 0x8] = new_imagebase_addr
	print(f'[+] After: {hex(struct.unpack("<q", pe_byte_array[ptr_imagebase:ptr_imagebase + 0x8])[0])}')

	pe_binary_mod.write(pe_byte_array)
	pe_binary_mod.close()
	pe_binary.close()

	return True


sys32_dll_list = dll_loaded_addr_dict.keys()
executor_file_path = os.path.dirname(os.path.realpath(__file__))

for dll_name, dll_loaded_addr in dll_loaded_addr_dict.items():	
	file_path = os.path.join("C:\\Windows\\System32", dll_name)

	if os.path.isfile(file_path):
		destination_file_path = os.path.join(executor_file_path, dll_name)
		if not os.path.isfile(destination_file_path):
			try:
				shutil.copyfile(file_path, destination_file_path)
			except PermissionError:
				print(f"{file_path} permission error!")
				continue
			except:
				print(f"{file_path} other error!")
				continue

		else:
			print(f"{destination_file_path} already exist!")

		if mod_pe_imagebase_addr(dll_name, dll_loaded_addr):
			print(f"[+] {destination_file_path} mod success")

		else:
			print(f"[+] {destination_file_path} mod error")

	else:
		print(f"{file_path} not found!")
