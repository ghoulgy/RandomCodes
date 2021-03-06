rol = lambda val, r_bits, max_bits: \
    (val << r_bits % max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits % max_bits)))

ror = lambda val, r_bits, max_bits: \
 ((val & (2**max_bits-1)) >> r_bits % max_bits) | \
 (val << (max_bits-(r_bits % max_bits)) & (2**max_bits-1))


def get_byte(dw):
    return dw & 0xff


def add_cl_eax(ecx, eax):
    return (ecx - get_byte(ecx)) + ((get_byte(ecx) + eax) & 0xff)


def rs():
    cs_byte = [0xb8,0x04,0x00,0x00,0x00,0xbb,0x01,0x00,0x00,0x00,0xb9,0xa1,0x91,0x04,0x08,0xba,0x26,0x00,0x00,0x00,0xcd,0x80,0xb8,0x03,0x00,0x00,0x00,0x31,0xdb,0xb9,0x88,0x91,0x04,0x08,0xba,0x33,0x00,0x00,0x00,0xcd,0x80,0x31,0xc9,0xb8,0x80,0x80,0x04,0x08,0xbb,0x23,0x81,0x04,0x08,0xe8,0x5b,0x00,0x00,0x00,0x89,0xca,0xb9,0x19,0x00,0x00,0x00,0xb8,0x55,0x91,0x04,0x08,0xbb,0x88,0x91,0x04,0x08,0xd1,0xca,0x8a,0x44,0x08,0xff,0x8a,0x5c,0x0b,0xff,0x30,0xd8,0x30,0xd0,0x75,0x1b,0x49,0x75,0xe3,0xb8,0x04,0x00,0x00,0x00,0xbb,0x01,0x00,0x00,0x00,0xb9,0x24,0x91,0x04,0x08,0xba,0x26,0x00,0x00,0x00,0xcd,0x80,0xeb,0x16,0xb8,0x04,0x00,0x00,0x00,0xbb,0x01,0x00,0x00,0x00,0xb9,0x4a,0x91,0x04,0x08,0xba,0x0b,0x00,0x00,0x00,0xcd,0x80,0xb8,0x01,0x00,0x00,0x00,0x31,0xdb,0xcd,0x80,0x29,0xc3,0x31,0xc9,0x02,0x08,0xc1,0xc1,0x03,0x40,0x4b,0x75,0xf7,0xc3]
    rotated = 0
    for i in range(0, len(cs_byte)):
        rotated = add_cl_eax(rotated, cs_byte[i])
        rotated = rol(rotated, 3, 32) & 0xffffffff

    return rotated


checksum = rs()
xor_strings = [0x1E,0xCD,0x2A,0xD5,0x34,0x87,0xFC,0x78,0x64,0x35,0x9D,0xEC,0xDE,0x15,0xAC,0x97,0x99,0xAF,0x96,0xDA,0x79,0x26,0x4F,0x32,0xE0]

flag = ''
# for i in range(25):
#     checksum = ror(checksum, 1, 32)
#     asd = checksum & 0xff
#     flag += str(chr(asd ^ xor_strings[i]))

length = 24

while (length >= 0):
    checksum = ror(checksum, 1, 32)
    asd = checksum & 0xff
    flag += str(chr(asd ^ xor_strings[length]))
    length -= 1

print "flag: " + flag[::-1]

# print hex(a)
# r = 0x5c4000L - get_byte(0x5c4000L)
# r = (0x5c4000L - get_byte(0x5c4000L)) + ((get_byte(0x5c4000L) + 0xbb) & 0xff)
# r = rol((0x5c4000L - get_byte(0x5c4000L)) + ((get_byte(0x5c4000L) + 0xbb) & 0xff),3,32)
# print hex(r)
# hex((0x5c0L - (0x5c0L & 0x5c0L)) + (((0x5c0L & 0xff) + 0x04) & 0xff))
# 0x2e20L
# 0x17100L
# 0xb8800L
# 0x5c4000L
# 0x2e205d8L
# 0x17102ec8L