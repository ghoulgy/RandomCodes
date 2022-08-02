import os
from base64 import b64encode, b64decode
import requests

data = zip(["ct_1", "ct_2"], [b"\xa4\xc2\x4b\x93\xfd\x9b\x12\x71\x94\x00\xb6\x35\xaf\xa0\x72\x82", b"\x85\x9d\xe5\x4c\xf4\x7e\x64\x77\x4e\x3f\x83\x22\x27\x80\x6b\x95"], ["/home/challenge/notes/todo.txt.enc", "/home/challenge/notes/grocery.txt.enc"])
# user input test data
# nonce: todo.txt.enc
# tag: F0 4B 06 44 4F 67 FF 84 BB 25 87 CD 61 13 CC 53
# ctx_1: 4A F9 5C F3 81 A1 28 C5 02 BC 11 A6 91 1A 08 A1
# plaintext_1: a*16:

# todo.txt.enc in key.db
# nonce: 74 6F 64 6F 2E 74 78 74 2E 65 6E 63 todo.txt.enc
# tag: E7 52 8B 60 75 33 30 A0 BA 74 E2 4E 4D 2C EF 86 
# ctx_2: 8F 5A 76 01 1D 5B 5B D5 F7 DD C6 F2 5F DB 1B 42
# plaintext_2 (key): 1e 70 11 24 33 5d c5 30 2d 99 20 5e 5f a9 b6 70 \xa4\xc2\x4b\x93\xfd\x9b\x12\x71\x94\x00\xb6\x35\xaf\xa0\x72\x82

# Get plain key text 
# plaintext_2 = xor(ctx_1, xor(plaintext_1, ctx_2)) These are with same nonce e.g. "todo.txt.enc"

# Data format todo.txt.enc
# Nonce: CC 2D A2 4C FA 37 2D 8B 20 06 27 F5 47 00 D5 EB
# Ciphertext: D8 78 4F C6 FB D9 5E AE 4F D3 E0 C6 11 7D 30 92 25 AE 4B 64 C3 B5 B0 DE 1F BC A2 B9 AD 35 D9 A3 43 F0 FE 48 ED 36 4A F7 F4 74 8C 51 51 BA A2 96 E1 60 51 22 C0 44 F7 1D 3F F4 EB E0 BB A4 F3 39 66 81 D6 1A 19 24 72 F0 CC BF 9E 09 E2 43 31 8E E7 96 43 D7 F6 57 7C 8E 6F 2B 8F 73 44 7C DF C6 58 8F 44 9B 84 D4 11 BC 1A B4 6B CF EF 97 80 70 AA 0C 95 7B A3 58 4C AF 24 E8 66 E9 DD 5D B6 28 9F 08 1C 16 1F
# AuthTag: E5 C7 D3 A9 E8 20 1A 7E F9 03 EF ED EA 53 CE 35

# grocery key db test data
# nonce: cery.txt.enc
# auth: EE 2C 68 10 FC 11 36 BF 51 BB D2 01 FE D0 77 8E
# ctx: A1 56 10 E8 D9 BC A4 7C D2 7E 32 CD DE 56 EF F5
# plaintext: bbbbbbbbbbbbbbbb 
# keydb real data
# auth: B0 2F D2 31 39 E8 38 6D 2D D9 78 DD A7 44 22 6C
# ctx: 46 A9 97 C6 4F A0 A2 69 FE 23 D3 8D 9B B4 E6 02
# plaintext (key): \x85\x9d\xe5\x4c\xf4\x7e\x64\x77\x4e\x3f\x83\x22\x27\x80\x6b\x95

encoded_data = bytearray()
for _, key, path in data:
    print(key, path)
    encoded_data += len(key).to_bytes(4, byteorder='little')
    encoded_data += key
    encoded_data += b"\x00\x00\x00\x00"
    encoded_data += len(path).to_bytes(4, byteorder='little')
    encoded_data += f"{path}".encode()
    encoded_data += b"\x00\x00\x00\x00"

res = requests.post("http://116.202.161.100:57689/encrypt_db", data=b64encode(encoded_data))
respond = b64decode(res.text)

print(respond)

with open("keys_from_me.db", "wb") as h:
    h.write(respond)

h.close()