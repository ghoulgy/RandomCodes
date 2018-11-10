rol = lambda val, r_bits, max_bits: \
    (val << r_bits % max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits % max_bits)))

ror = lambda val, r_bits, max_bits: \
 ((val & (2**max_bits-1)) >> r_bits % max_bits) | \
 (val << (max_bits-(r_bits % max_bits)) & (2**max_bits-1))

# FA 5A 32 8A 32 E3 52 82 40 BA 5A 32 48 52 5A 12 02 42 70 42 32 D2 FA

a = [0xFA, 0x5A, 0x32, 0x8A, 0x32, 0xE3, 0x52, 0x82, 0x40, 0xBA, 0x5A, 0x32, 0x48, 0x52, 0x5A, 0x12, 0x02, 0x42, 0x70, 0x42, 0x32, 0xD2, 0xFA]


def getByte(b):
    return b & 0xff


flag = ''
for i in a:
    rol5 = rol(i, 5, 8)
    print hex(rol5)
    char = rol5 ^ 0x23
    # print char
    flag += str(chr(char))

print flag
