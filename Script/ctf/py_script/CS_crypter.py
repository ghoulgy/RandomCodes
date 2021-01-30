#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''              ,
                /|      ,
   ,--.________/ /-----/|-------------------------------------.._
  (    /_/_/_/_  |--------- DEATH TO ALL TABS ---------------<  _`>
   `--´        \ \-----\|-------------------------------------''´
                \|      '
'''#             '
assert __name__ == '__main__'
import sys
import os
def die(E):
    print(F'E:',E,file=sys.stderr)
    sys.exit(1)
T=lambda A,B,C,D,E,F,G,H,I:A*E*I+B*F*G+C*D*H-G*E*C-H*F*A-I*D*B&255

def U(K):
    R=pow(T(*K),-1,256)
    A,B,C,D,E,F,G,H,I=K
    return [R*V%256 for V in
     [E*I-F*H,C*H-B*I,B*F-C*E,F*G-D*I,A*I-C*G,C*D-A*F,D*H-E*G,B*G-A*H,A*E-B*D]]

def C(K,M):
    B=lambda A,B,C,D,E,F,G,H,I,X,Y,Z:bytes((A*X+B*Y+C*Z&0xFF,
        D*X+E*Y+F*Z&0xFF,G*X+H*Y+I*Z&0xFF))
    N=len(M)
    R=N%3
    R=R and 3-R
    M=M+R*B'\0'
    return B''.join(B(*K,*W) for W in zip(*[iter(M)]*3)).rstrip(B'\0')

Ms = "259F8D014A44C2BE8FC573EAD944BA63"

from itertools import permutations
if sys.argv[1].upper() == 'E':
    M=B'SPACEARMY'+bytes(M,'ascii')
    print(C(U(K),M).hex().upper())
else:
    # Basically Just Partial Decode the Encrypted Strings
    # By create a combination which consist of 3 printable string
    b = list(permutations("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 3))
    y = [''.join(i) for i in b]
    for ys in y:
        M=C(bytes(ys+"XXXXXX", "ascii"), bytes.fromhex(Ms))
        # M=C(bytes("XXX"+ys+"XXX", "ascii"), bytes.fromhex(Ms))
        # M=C(bytes("XXXXXX" + ys, "ascii"), bytes.fromhex(Ms))
        if M[:1]==b'S' and M[3:4]==b'C' and M[6:7]==b'R':
        # if M[1:2]==b'P' and M[4:5]==b'E' and M[7:8]==b'M':
        # if M[2:3]==b'A' and M[5:6]==b'A' and M[8:9]==b'Y':
            print("Found: " + ys)
        # elif M[3:4]==b'C':
        # elif M[6:7]==b'R'
    # M[:9]==B'SPACEARMY' or die('INVALID')
    # print(M[9:].decode('ascii'))

# Key
# SP4evaCES
