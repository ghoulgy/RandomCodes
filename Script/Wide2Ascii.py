# Convert Wide Char to Ascii (E.g W.I.D.E -> WIDE)
import binascii
import re

with open(sys.argv[1], "rb") as inf:
  content = inf.readline()
inf.close()

hex_content = binascii.hexlify(content)

ascii_hex_content = re.sub(b"00", b'', hex_content)
byte_content = binascii.unhexlify(ascii_hex_content) # So it can write as byte into file alter 

with open(f"{sys.argv[1]}_write.bin", "wb") as of:
  of.write(byte_content)
of.close()