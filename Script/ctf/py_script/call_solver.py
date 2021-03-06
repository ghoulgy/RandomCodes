from z3 import *

x = [BitVec('x' + str(_), 32) for _ in range(32)]
s = Solver()

s.add(
x[21] - x[14] == 40,
x[7] * x[15] == 5141, 
x[5] - x[11] == 1,
x[19] - x[1] == 44,
x[16] * x[28] == 2915,
x[10] * x[3] == 9603, 
x[11] * x[2] == 4998, 
x[23] - x[5] == 50,
x[18] - x[8] == 46,
x[8] * x[22] == 2754 ,
x[3] - x[17] == 42,
x[12] * x[23] == 5000 ,
x[6] * x[23] == 10000 ,
x[26] - x[25] == 48,
x[30] * x[5] == 2500 ,
x[9] * x[12] == 5050 ,
x[19] - x[31] == 43,
x[5] * x[27] == 4850 ,
x[15] - x[1] == 44,
x[27] * x[29] == 4947 ,
x[4] * x[15] == 5529 ,
x[23] - x[11] == 51,
x[8] * x[27] == 5238 ,
x[2] - x[26] == 3,
x[20] - x[1] == 47,
x[24] * x[28] == 3080 ,
x[14] - x[25] == 6,
x[6] * x[22] == 5100 ,
x[26] - x[13] == 43,
x[13] * x[10] == 5544 ,
x[7] * x[8] == 2862  ,
x[13] - x[25] == 5,
x[27] - x[18] == -3,
x[20] * x[5] == 5000,
x[0] * x[17] == 5335,
x[4] - x[17] == 2,
x[2] - x[28] == 47
)

if s.check():
  m = s.model()
  print("Key: " + "".join(chr(m.eval(x[_]).as_long()) for _ in range(32)))
