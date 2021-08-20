import idc
import ida_bytes
import idautils
import struct


def decode_modname(stacked_bytes):
	dec_bytes = ""
	idx = 0

	try:
		for sb in stacked_bytes:
			if sb == 0x00:
				continue

			tmp_sb = sb + (0xff89 - idx)

			if tmp_sb > 0xff:
				dec_bytes += chr(tmp_sb - 0x10000)
			else:
				dec_bytes += chr(tmp_sb)

			idx += 1
	except:
		return f"[-] {stacked_bytes} stack error"

	return dec_bytes


def decode_fnname(stacked_bytes):
	dec_bytes = ""
	idx = 0
	for sb in stacked_bytes:
		tmp_sb = sb + (0x89 - idx)

		if tmp_sb > 0xff:
			dec_bytes += chr(tmp_sb - 0x100)
		else:
			dec_bytes += chr(tmp_sb)

		idx += 1

	return dec_bytes


def get_stacked_bytes(dec_func_addr):
	func_stacked_bytes_addr_dict = {}
	xrefs = idautils.CodeRefsTo(dec_func_addr, 0)

	for xref in xrefs:
		prev_addr = idc.prev_head(xref)
		prev_addr_2 = idc.prev_head(prev_addr)

		if idc.print_insn_mnem(prev_addr_2) == "call":
			func_name = idc.print_operand(prev_addr_2, 0)
			func_addr = idc.get_name_ea_simple(func_name)
			func_stacked_bytes_addr_dict[xref] = func_addr


	# enc_mod_addr = list(set(enc_mod_addr)) # [Debug] Get unique functions only  

	for xref, stacked_bytes_addr in func_stacked_bytes_addr_dict.items():
		print(f"Address: {hex(stacked_bytes_addr)}")
		func_ea = idc.get_func_attr(stacked_bytes_addr, idc.FUNCATTR_START)
		bytes_collected = bytearray()       # Collected stack string store here


		for ins in idautils.FuncItems(func_ea):
			if ida_bytes.is_code(ida_bytes.get_full_flags(ins)):
				if idc.print_insn_mnem(ins) == "mov":
					if idc.get_operand_type(ins, 1) == idc.o_imm:
						# disasm = idc.GetDisasm(ins) # [Debug]
						hex_str_len = len(idc.print_operand(ins, 1).lstrip("0").rstrip("h"))
						const_hex_byte = idc.print_operand(ins, 1).lstrip("0").rstrip("h")
						
						if hex_str_len != 8: # Skip if const hex byte less than 8
							append_zero = "0" * (8 - hex_str_len)
							const_hex_byte = append_zero + const_hex_byte
							# print(struct.pack("<I", int(const_hex_byte, 16))) # [Debug]

						# else:
							# print(struct.pack("<I", int(const_hex_byte, 16))) # [Debug]
						bytes_collected += struct.pack("<I", int(const_hex_byte, 16))

		if len(bytes_collected) >= 1:
			cmt_str = ""
			if dec_func_addr == 0x10001253: # fn_name_addr
				print(f"{decode_fnname(bytes_collected[4:])}")
				cmt_str = decode_fnname(bytes_collected[4:])
			elif dec_func_addr == 0x1000122B: # mod_name_addr
				print(f"{decode_modname(bytes_collected[4:])}")
				cmt_str = decode_modname(bytes_collected[4:])
			idc.set_cmt(xref, cmt_str, 1) # Comment near xref decoder function
		else:
			print(f"[-] {hex(stacked_bytes_addr)} addr error")

fn_name_dec_addr = 0x10001253
mod_name_dec_addr = 0x1000122B

get_stacked_bytes(fn_name_dec_addr)
get_stacked_bytes(mod_name_dec_addr)
# for fn_stacked_bytes in get_stacked_bytes(fn_name_addr):
# 	print(fn_stacked_bytes)
# 	print(decode_fnname(fn_stacked_bytes))

# for mod_stacked_bytes in get_stacked_bytes(mod_name_addr):
# 	print(mod_stacked_bytes)
# 	print(decode_modname(mod_stacked_bytes))