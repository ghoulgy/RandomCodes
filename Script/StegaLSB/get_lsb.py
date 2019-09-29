# Python2
import base64
import binascii
import codecs
from PIL import Image
outputfile = open('lsb_hehe', 'w+b')
image = Image.open("hehe.bmp")

extracted = ''

pixels = image.load()

for x in range(0, image.width):
  for y in range(0, image.height):
    r, g, b = pixels[x, y]
    # Store LSB of each color channel of each pixel
    # print(bin(r), bin(g), bin(b))
    # print(r, g, b)

    # Debug purpose
    # if x==0:
    #   if y<1:
    #     print(bin(r), bin(g), bin(b))
    #     extracted += format(b, '08b')[-2:]
    #     extracted += format(g, '08b')[-3:]
    #     extracted += format(r, '08b')[-3:]
    #     print(extracted)

    extracted += format(b, '08b')[-2:]
    extracted += format(g, '08b')[-3:]
    extracted += format(r, '08b')[-3:]

# print(extracted)

chars = []
for i in range(0, int(len(extracted)/8)):
  byte = extracted[i*8:(i+1)*8]
  # print(int(''.join([str(bit) for bit in byte]),2))
  # a = int(''.join([str(bit) for bit in byte]), 2)
  # print(hex(a)[2:], end="")
  byte = int(''.join([str(bit) for bit in byte]), 2)
  # print byte
  outputfile.write('%c' % byte)
  # byte = inputfile.read(1)

outputfile.close()

  # outputfile.write(hex(a)[2:].encode())
  # chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))