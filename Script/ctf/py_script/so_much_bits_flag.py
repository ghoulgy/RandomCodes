from Crypto.Cipher import AES

with open("/SoMuchBits/notes/todo.txt.enc", "rb") as f:
    content = f.read()

# with open("/SoMuchBits/notes/grocery.txt.enc", "rb") as fs:
#     content = fs.read()

secretKey = b"\xa4\xc2\x4b\x93\xfd\x9b\x12\x71\x94\x00\xb6\x35\xaf\xa0\x72\x82" # decryption key for todo.txt
# secretKey = b"\x85\x9d\xe5\x4c\xf4\x7e\x64\x77\x4e\x3f\x83\x22\x27\x80\x6b\x95" # decryption key for grocery.txt 
nonce = content[:12]
auth = content[12:28]
ciphertext = content[28:]

aes_c = AES.new(secretKey, AES.MODE_GCM, nonce=nonce)
decrypted_text = aes_c.decrypt(ciphertext) # decrypted_text = AES.new(secretKey, AES.MODE_GCM, nonce).decrypt_and_verify(ciphertext, auth)
print(decrypted_text)

with open("dec.txt", "wb") as h:
    h.write(decrypted_text)
h.close()