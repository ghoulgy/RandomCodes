import sys

with open("C:\\Users\\cyjien\\Desktop\\possible_conf.bin", "rb") as f:
  contents = f.read()

for i in range(256):
  xored = ""
  for content in contents:
    xored += chr(ord(content) ^ i)

  if "libgcj" in xored: # Keyword here
    print("Key in decimal {}\nKey in hex {}".format(i, hex(i)))

    with open("C:\\Users\\cyjien\\Desktop\\xored.bin", "wb") as o:
      o.write(xored)
      o.close()
    # sys.exit(0)

f.close()
print("End")