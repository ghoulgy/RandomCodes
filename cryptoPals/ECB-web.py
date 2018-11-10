# ECB web solution 
import requests
import base64
import urllib

url='http://localhost/ECB-web/index.php?a=reg'

# determine the cipher block size
for i in range(1, 31):
  cookies = requests.post(url, data={'username': 'a'*i, 'password': '123'}, allow_redirects=False).cookies
  username = base64.b64encode(urllib.unquote(cookies['username']))
  print len('a'*i), len(username)

# Get Exploit ECB by determine the max block size and add the specific key into the next new block
# cookies = request.post(url, data={'username': 'aaaaaaaaaaaaaaaa4', 'password': '123'}, allow_redirects=False).cookies

# uid = urllib.quote_plus(base64.b64encode(username[16:]))

# r = request.get(url, cookies={'uid': uid, 'username': cookies['username']})
# print r.text