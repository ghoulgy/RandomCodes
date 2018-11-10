#!/usr/bin/python3
from pwn import *
from Crypto.Util.number import *
import binascii

ip = "challenge01.root-me.org"
port = 51031

r = remote(ip, port)
r.recv()

n = 456378902858290907415273676326459758501863587455889046415299414290812776158851091008643992243505529957417209835882169153356466939122622249355759661863573516345589069208441886191855002128064647429111920432377907516007825359999

e = 65537

c = 41662410494900335978865720133929900027297481493143223026704112339997247425350599249812554512606167456298217619549359408254657263874918458518753744624966096201608819511858664268685529336163181156329400702800322067190861310616

c2 = pow(2,e,n)

payload = c * c2

r.sendline(str(payload))

response = r.recvline()
response = r.recvline()

# The corresponding plaintext is: 

# python2
# p = long(response.split(" ")[-1])
# p = long_to_bytes(long(p) // 2)

# python3
p = response.split()[-1]
p = int(p) // 2
p = hex(p)[2:]
p = bytearray.fromhex(p).decode('ascii')

print(p)
