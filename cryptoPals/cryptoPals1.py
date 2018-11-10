#!/usr/bin/env python3
'''
' Desire Output SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t
'''
import codecs, base64

a = '49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d'


def toHex(num):
  b = codecs.decode(num, 'hex')
  c = base64.b64encode(b)
  # c = codecs.encode(b, 'base64')
  return c

if __name__ == '__main__':
  print(codecs.decode(toHex(a), 'base64')) 