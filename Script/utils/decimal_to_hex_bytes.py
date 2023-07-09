"""
' Convert array of decimal value into a hex dump file.
"""

decimal_array= []
z = ""
nbits = 16

with open("out_hex_bytes.bin", "wb") as f:
    for decimal in decimal_array:
        # Convert any negative number to hex byte e.g. -41
        # nbits = 16 bits since it is hex number (base 16)
        decimal = decimal & ((1 << nbits)-1) # ((1 << nbits) - 1) == 0xFFFF
        hex_str = f"{decimal:X}"

        # Remove any converted decimal value that contains double hex bytes and remove the first FF byte if there is any 
        # e.g. FFC6 -> C6
        if len(hex_str) == 4 and hex_str.startswith("FF"):
            hex_str = hex_str.replace("FF", "", 1)

        # Append 0 to single hex value so it can be process further by bytes.fromhex()
        # e.g. C -> 0C
        if len(hex_str) == 1:
            hex_str = "0" + str(hex_str)

        f.write(bytes.fromhex(hex_str))

f.close()
