#!/usr/bin/env python3
'''
' Output 746865206b696420646f6e277420706c6179
'''
import codecs

a = '1c0111001f010100061a024b53535009181c'
b = '686974207468652062756c6c277320657965'

def xor(a,b):
  aHex = int(a,16)
  bHex= int(b, 16)
  cHex = aHex ^ bHex
  return cHex


if __name__ == '__main__':
  xored = xor(a,b)
  output = hex(xored)
  print(codecs.decode(output[2:], 'hex'))