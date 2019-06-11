'''
' Two Bytes Xored Script
' By CYJ
'''

bytesStr = "EE A2 DF EA DC A6 DB AD 9A A3 C9 EA C9 FB D7 BA D6 F9 8A A8 DC BF C9 A9 8E 9E 8B FA D4 8A D1 A3 D9 BE D7 EA 80 E3"
bytesArray = bytesStr.split()
key = "BACA"
flag = ""
for Sbytes in range(1, len(bytesArray), 2):
  Dbytes = bytesArray[Sbytes-1] + bytesArray[Sbytes]  # Dbytes 2 bytes e.g. EEA2
  # print(Dbytes)
  xored = int(key, 16) ^ int(Dbytes, 16)
  hexStr = hex(xored)[2:]
  # print(e)
  f = bytes.fromhex(hexStr).decode('utf-8')
  flag += f

print(flag)

# Another Example
hexValsStr = "275223102F46714238432453"
hexVals = [hexValsStr[i: i+2] for i in range(0, len(hexValsStr), 2)]
# Swap odd / even position
# for i in range(0, len(hexVals), 2):
#     tmp_odd = hexVals[i+1]
#     hexVals[i+1] = hexVals[i]
#     hexVals[i] = tmp_odd
# print(hexVals)
flag = ""
for i in range(0, len(hexVals), 1):
  if (i % 2 == 0):
    flag += chr(int(hexVals[i], 16) ^ int("41", 16))
  elif (i % 2 != 0):
    flag += chr(int(hexVals[i], 16) ^ int("21", 16))

print("Flag: {:s}".format(flag))
