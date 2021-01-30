'''
' crackme lolz-login-v2
' By: CYJ
'''

import binascii
encoded = ".-8.4.p"

flag = ""
for enc in encoded:
  flag += chr(int(binascii.hexlify(enc.encode()).decode(), 16) ^ 
    int(binascii.hexlify(b"B").decode(), 16))

print("Flag is {:s}".format(flag))
