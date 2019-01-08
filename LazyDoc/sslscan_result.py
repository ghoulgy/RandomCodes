'''
' Simple ssl_scan_result filter v1.0
' By CYJ
' Signature Algorithm:
' RSA Key Strength:
' Subject:
' Issuer:
' Not valid before:
' Not valid after:
'''
import re

fileName = "sslscan_result.txt"
regex1 = r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})"
regex2 = r":[ ]{1,}.*"
regex3 = r".*:[ ]{1,}"
readBelowSSLCert = False
selectedLine = ""

with open(fileName,'r') as f:
  next(f)
  contents = f.readlines()

for content in contents:
  m = re.search(regex1, content)
  m2 = re.search(regex2, content)
  m3 = re.sub(regex3, '', content)

  if m:
  	ip = m.group(0)
  	port = content.split(None,6)[6]
  	continue

  if m2:
    str_m3 = m3[:-1]
    if str_m3 in m2.group(0):
      print(ip + "," + str_m3)