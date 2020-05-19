with open("filename.bin", "rb") as f:
  contents = f.read()

for i in range(256):
  xored = ""
  for content in contents:
    xored += chr(ord(content) ^ i)

  if "Keywords" in xored: # Keyword here
    print("Key in decimal {}\nKey in hex {}".format(i, hex(i)))

    with open("xored.bin", "wb") as o:
      o.write(xored)

o.close()
f.close()

