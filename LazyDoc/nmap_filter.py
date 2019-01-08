'''
' Simple Nmap finding filter v1.0'
' By CYJ
' Reminder: Can turn into table form in word doc
'''

import re

fileName = "nmap_sSA.txt"

with open(fileName,'r') as f:
  contents = f.readlines()

line = ""
startRead = False
selectedLine = ""
regex1 = r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$"
regex2 = r"^[0-9]+/"

for content in contents:
  m = re.search(regex1, content)
  if m:
    ip = m.group(0)
    startRead = True
    # print(content)
    continue

  if startRead:
    m2 = re.search(regex2, content)
    selectedLine = content.split(None,4)
    if m2:
      try:
        # If print all details
        # print(ip + " " + m2.group(0) + " " + selectedLine[4][:-1])

        # Print details with ip, service and version only
        port = m2.group(0)[:-1]
        service = selectedLine[2]
        clearSpace = selectedLine[4].split(None, 2) 
        if len(clearSpace) == 3:
          if clearSpace[0] == "ttl":
            print(ip + "," + port + "," + service + "," + clearSpace[2][:-1])
          else:
            print(ip + "," + port + "," + service + "," + selectedLine[4][:-1])
        else:
          print(ip + "," + port + ","+ service)
      except IndexError:
        print(ip + "," + port + "," + service)
      # else:
        # print(ip + " " + m2.group(0))

      # Concatenate the http://<ip> or https://<ip>
      # if m2.group(0) == "80/":
      #   print("http://" + ip + " " + selectedLine[2])
      # elif m2.group(0) == "443/":
      #   print("https://" + ip + " " + selectedLine[2])
    else:
      continue 	

#   else:
#     print("Not Found")
#     break

# print(line)

f.close()
