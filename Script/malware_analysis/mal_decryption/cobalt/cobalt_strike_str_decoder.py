# Cobalt Strike stacked string decoder
# Decode 1
def decode_fnname():
	idx = 0
	dec_bytes = ""

	enc_bytes_list = [
						[0xBA, 0xEA, 0xDE, 0xDB, 0xEF, 0xE1, 0xD1, 0xE6, 0xF1, 0xE5, 0xE2, 0xE6, 0x83],
						[0xCD, 0xE1, 0xEB, 0xEE, 0xF0, 0xDD, 0xE9, 0xC4, 0xF1, 0xE5, 0xE6, 0x82]
					 ]

	for enc_bytes in enc_bytes_list:
		for enc_byte in enc_bytes:
			tmp_enc_byte = enc_byte + (0x89 - idx)
			if tmp_enc_byte > 0xff:
				dec_bytes += chr(tmp_enc_byte - 0x100)
			else:
				dec_bytes += chr(tmp_enc_byte)

			idx += 1

		print(dec_bytes)
		# Clean var
		dec_bytes = ""
		idx = 0

# Decode 2
def decode_modname():
	idx = 0
	dec_bytes = ""

	enc_bytes_list = [
						[0xc2, 0x00, 0xBD, 0x00, 0xCB, 0x00, 0xC8, 0x00, 0xC0, 0x00, 0xC8, 0x00, 0xB0, 0x00, 0xB0, 0x00]
					 ]

	for enc_bytes in enc_bytes_list:
		for enc_byte in enc_bytes:
			if enc_byte == 0x00:
				continue

			tmp_enc_byte = enc_byte + (0xff89 - idx)
			# print(hex(enc_byte))

			if tmp_enc_byte > 0xff:
				# print(hex(tmp_enc_byte))
				dec_bytes += chr(tmp_enc_byte - 0x10000)
			else:
				dec_bytes += chr(tmp_enc_byte)

			idx += 1

		print(dec_bytes)
 		# Clean var
		dec_bytes = ""
		idx = 0

decode_fnname()
decode_modname()
