# Emotet msg email password extractor
# Date: 9/2020 
# By: @ghoulgy
import binascii
import codecs
import sys 
import re

with open(sys.argv[1], "rb") as f:
  content = f.read()
f.close()

hex_content = binascii.hexlify(content).upper()

match_password_regex = re.compile(b"0D000A00D130B930EF30FC30C9301AFF5B(.*?)5D")
is_pwd = match_password_regex.search(hex_content)

if is_pwd:
  pwd_ascii = re.sub(b"00", b'', is_pwd.group(1))
  pwd_str = codecs.decode(pwd_ascii, 'hex').decode()
  print(f"{pwd_str}")
else:
  print("Pwd Not found")
