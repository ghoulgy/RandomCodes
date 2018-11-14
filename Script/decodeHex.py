inputfile = open('ch3.bmp','rb')
outputfile = open('decoded_file','w+b')
byte = inputfile.read(1)

# If to xor all bytes
# while byte != "":
#     byte = ord(byte)
#     byte = byte ^ 0x47
#     outputfile.write('%c' % byte)
#     byte = inputfile.read(1)

# If to xor file with keys
i = 0
key = ['f', 'a', 'l', 'l', 'e', 'n']
while byte != "":
  byte = ord(byte)
  byte = byte ^ ord(key[i % len(key)])
  outputfile.write('%c' % byte)
  i += 1
  byte = inputfile.read(1)

outputfile.close()
