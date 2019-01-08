import re

fileName = "PPSB.txt"
# Regex for IP address
regex1 = r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$"
selectedLine = ""
test = ""
ifSame = True

with open(fileName,'r') as f:
  contents = f.readlines()

for content in contents:
	selectedLine = content.split(None, 2)
	portNum = selectedLine[2][1:-2].split("/")[0]
	protocol = selectedLine[2][1:-2].split("/")[1]
	ip = selectedLine[1]
	cmpIP = ip[-3:]
	print(ip + ","+ portNum + "," + protocol.upper())

# if prev = True:
#   lol = ip
#   print(ip)
#   prev = False
# else:
#   prev = True