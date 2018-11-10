#!/usr/bin/env python3
import codecs

a = '1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736'


def englishScore(input):

  character_frequencies = {
      'a': .08167, 'b': .01492, 'c': .02782, 'd': .04253,
      'e': .12702, 'f': .02228, 'g': .02015, 'h': .06094,
      'i': .06094, 'j': .00153, 'k': .00772, 'l': .04025,
      'm': .02406, 'n': .06749, 'o': .07507, 'p': .01929,
      'q': .00095, 'r': .05987, 's': .06327, 't': .09056,
      'u': .02758, 'v': .00978, 'w': .02360, 'x': .00150,
      'y': .01974, 'z': .00074, ' ': .13000
  }
  score = []

  for byte in input:
    s = character_frequencies.get(chr(byte), 0)
    score.append(s)

  return sum(score)


def xor(input, char_val):
  out_bytes = b''

  for byte in input:
    out_bytes += bytes([byte ^ char_val])
  
  return out_bytes


def bruteHex(input):
  for i in range(256):
    xored = xor(input, i)
    score = englishScore(xored)
    data = {
      'score': score,
      'xored': xored,
      'key': i
    }
    scoreList.append(data)
  
  return sorted(scoreList, key=lambda x: x['score'], reverse=True)[0]


if __name__ == '__main__':

  contents = open('cryptoPal4.txt', 'r').read().splitlines()
  scoreList = []
  for content in contents:
    dehex = codecs.decode(content, 'hex')
    scores = bruteHex(dehex)
    scoreList.append(scores)
  scores = sorted(scoreList, key=lambda x: x['score'], reverse=True)[0]
  for item in scores:
    print("{},{}".format(item.title(), scores[item]))
  # for item in bestScore:
  #   print("{},{}".format(item.title(), bestScore[item]))
