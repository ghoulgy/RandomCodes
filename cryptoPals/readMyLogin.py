import struct
from Crypto.Cipher import AES

file = 'mylogin.cnf'
mode = 'rb'
f = open(file, mode)

f.seek(4)
b = f.read(20)          
key = [0] * 16

for i in range(20):
  key[i % 16] ^= b[i]

key = struct.pack("16B", *key)
encrypt = AES.new(key, AES.MODE_ECB)

f.seek(24)

while True:
  b = f.read(4)
  print(b)
  # print(struct.unpack("<i", b))
  if len(b) < 4:
    break
  cipher_len = struct.unpack("<i", b)[0]
  b = f.read(cipher_len)
  # print(cipher_len)
  plain = encrypt.decrypt(b)
  # print(plain)
  print(plain[:-plain[-1]].decode("ascii"))

plain = encrypt.decrypt(b'\xA9\x7A\x87\x38\xEE\xDB\x3A\x4A\x57\x45\x86\xA2\x2F\xCD\x82\xE5')
print(plain)
f.close()

# print
# if data[:4] != b"\x00"*4:
#   print("GG not valid!")

# key = data[4:24]

# realKey = [0]*16
# for i in range(len(key)):
#   realKey[i % 16] ^= key[i]

# print("AES key: ", realKey)
# print(data[24:30])
# encrypt = AES.new(bytes(realKey), AES.MODE_ECB)
# decoded = b""

# i = 24
# while i < len(data):
#   length = struct.unpack("<i", data[i:i+4])[0]
#   print(length)
#   encrypted = data[i+4:i+4+length]
#   decoded += encrypt.decrypt(encrypted)
#   i = i+4+length

# print(decoded.decode("utf-8"))