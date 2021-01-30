enc_str = "773032205849207A3831326F1351202E3B306B7D1E5A3B33252B382454173735266C3D3B53163735222D393B475C7A37222D7F38421B6A66643032205849206477303220584920643D2223725C503A3F39636C725F5C237A082C383C7950223F65023F3D5F4039353E3079755F5F666E1134141F5C4C64377A1B671F565A1B2C7F7B101F42700D1F39331717161574213F2B2337505D27606B712C7B0A543D342E317F214558262E636A6A6E1E4A37282233256C"

def extract_hex(s):
  s_len = len(s)
  arr = []
  for i in range(0, s_len, 2):
    arr.append(int(int(s[i], 16) << 4) + int(s[i+1], 16) & 0xFF)
  return arr


def hex_xor(sa):
  key = [75, 67, 81, 82, 49, 57, 84, 90]
  decoded = []
  for i in range(len(sa)):
    decoded.append(chr(sa[i] ^ key[i % len(key)]))
  return decoded


hex_arr = extract_hex(enc_str)
hex_xor = hex_xor(hex_arr)
[print(w, end="") for w in hex_xor]