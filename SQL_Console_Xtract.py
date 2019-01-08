'''
' ! READ BEFORE RUN IT !
' Console SQL command results filter v1.0'
' By CYJ
' Usage: Extract the results the results of the console text file (SQL only).
' Make sure all is in SQL> SELECT if not Please do as following:
' Open your text editor, find (ctrl+F) ^SQL>.*\n.*SELECT with regex enabled.
' Then replace (ctrl+H) it with SQL> SELECT.
'''

from openpyxl import Workbook
import re

wb = Workbook()
dest_filename = 'empty.xlsx'
ws1 = wb.active
ws1.title = "memes" 

#re1 = r"^SQL>\n.*SELECT"
re2 = r"^SQL>.*SELECT "
re3 = r"^Disconnected"
re4 = r".*;.*"
re5 = r"^SQL>"

unlock = False
isEnd = True
f = open('filename.txt', 'r')

line = f.readline().strip()
arrayOut = []
i = 0
output = ''

while True:
	isEnd = re.search(re3, line) # re3 = r"^Disconnected"
	if isEnd:
		arrayOut.append(output)
		break
	# m1 = re.search(re1, line) # re1 = r"^SQL>\n.*SELECT"
	m2 = re.search(re2, line) # re2 = r"^SQL>.*SELECT "

	if unlock:
		output = output + line + '\n'
		# m2 = re.search(re1, line) 
		if m2:
			arrayOut.append(output)
			output = ''
			output = output + line + '\n'
			unlock = False

	if m2 and unlock is False:
		output = output + line + '\n'
		unlock = True

	line = f.readline().strip()

f.close()

arrayResults = []
unlock2 = False
results = ''
for elmt in arrayOut:
	splitted = elmt.split('\n')
	for line in splitted:
		if unlock2:
			m4 = re.search(re5, line) # re5 = r"^SQL>"
			if m4:
				arrayResults.append(results)
				results = ''
				unlock2 = False
				break
			results = results + line + '\n'

		m3 = re.search(re4, line) # re4 = r".*;.*"
		if m3:
			unlock2 = True

# Save it to the excel file
for row in range(1, len(arrayResults)+1):
	for col in range(1, 2):
		_ = ws1.cell(column=col, row=row, value="{}".format(arrayResults[i]))
		i = i + 1

wb.save(filename = dest_filename)

# Test before proceed to excel
# for i in range(len(arrayOut)):
# 	print("{0:s})".format(str(i)))
# 	print(arrayOut[i])

