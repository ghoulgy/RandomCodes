f = open('sleepb64d', 'rb')
ofile = open('sleepPic', 'w+b')
byte = f.read(1)

# key = [0x89, 0x50 ,0x4e, 0x47 ,0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d]
# i = 0

# while byte != '':
#   byte = ord(byte) ^ key[i%len(key)]
#   ofile.write('%c'%byte)
#   i += 1
#   byte = f.read(1)

# ofile.close()

key = ['W', 'o', 'A', 'h', '_', 'A', '_', 'K', 'e', 'y', '!', '?']
i = 0

while byte != '':
  byte = ord(byte) ^ ord(key[i%len(key)])
  ofile.write('%c'%byte)
  i += 1
  byte = f.read(1)

ofile.close()