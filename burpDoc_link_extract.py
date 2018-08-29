'''
'	Simple Burp link extract and remove the redundancy
'	if the redundancy count > 2, its IMPORTANT because
'	it is > 2!
'
'	By: CYJ
'	Signature: Its too LOL when writing this script
'	Weakness: Only For redundancy count > 2 will merge
'	Able to alter the redundancy count but condition will
'	increase and GL hv edit
'''

import re
import urllib.request
from bs4 import BeautifulSoup

url = ""
regex_num = r"([0-9]+\.)+"
i = 0
ary_split_str = []
n = 0
merge = 0
# page = urllib.request.urlopen(url)
# content = BeautifulSoup(page.read())

# print(content)
# page.close()

with open(url, encoding="utf-8") as file:
	data = file.read()
	soup = BeautifulSoup(data, 'html.parser')
	# Remove: "a", "#4.x"
	for tag in soup.find_all("p", class_=["TOCH1", "TOCH0"]):
		raw_strings = tag.find("a").get_text()
		m1 = re.match(regex_num, raw_strings)

		if m1:
			filtered_str = re.sub(regex_num, "", raw_strings)
			splited_str = filtered_str.split("/")
			ary_split_str.append(splited_str)					# To make it in 2D-array form
file.close()

main_ary = []
main_num = 0
final_ary = []

# print("/".join(ary_split_str[4][-4:-2]))

# Calculate the total number of the main finding's name
for i in range(len(ary_split_str)):
	if i == len(ary_split_str):
		break
	if len(ary_split_str[i]) == 1:
		# print(ary_split_str[i][0])
		main_num += 1

# Create an empty array in the main_ary according the num of main_num get eg: main_num=7: [[],[],[],[],[],[],[]]
for i in range(main_num):
	main_ary.append([])
	final_ary.append([])

# Time to insert the urls in each finding into respectively set of array eg: urls in 3th group into 3th sub array
main_num_2 = 0
title_ary = []
for i in range(len(ary_split_str)):
	# Seperate the main findings and its url using following condition
	# Condition 1.1 (If is urls)
	if len(ary_split_str[i]) > 1:						# If the cur gt 1 
		try:
			main_ary[main_num_2].append(ary_split_str[i])		# Append the urls into the cur index of ary
		except:
			print("GGWP")
	# Condition 1.2 (If is main findings)
	else:
		title_ary.append("".join(ary_split_str[i]))				# Insert the title into the ary
		# Two situation to insert new ary: 1) Next findings name is findings name. 2) Next findings name pos+1/pos-1 is url
		if i != len(ary_split_str)-1:					# If the i is eq len of ary
			if len(ary_split_str[i+1]) <= 1:		#	If the len of cur+1 le 1 
				main_num_2 += 1
			elif len(ary_split_str[i]) != len(ary_split_str[i-1]) and len(ary_split_str[i]) != len(ary_split_str[i+1]):		# If the len of cur ary not eq prev and next
				main_num_2 += 1
		# print("".join(ary_split_str[i]))		# Print all the main header name out

# print(main_num_2, len(main_ary), len(title_ary))		# main_ary outcome eg: [[],[],[],[['http:', '', 'www.google.com', '']], [], [], [], []]

# Time for the merge things in
for sub_ary, c in zip(main_ary, range(len(main_ary))):
	if len(sub_ary) > 1:
		poops = 0														# Determine whether need to merge the url
		m = sub_ary
		for a in range(len(m)):											# Loop through sub_ary eg: ['http:', '', 'www.google.com', '']
			# print(m[a][-3:-1])
			try:
				# Condition 1.1
				if a == 0:												# 1st elmnt
					if m[a][-3:-1] == m[a+1][-3:-1]:					# If 1st elmnt eq to next
						poops += 1										# Poops increase by one
					elif m[a][-3:-1] != m[a+1][-3:-1]:					# If 1st elmnt not eq with next
						final_ary[c].append("/".join(m[a]))
						# print("/".join(m[a]))
				# Condition 1.2
				elif a == len(m)-1:										# Last elmnt
					if m[a][-3:-1] == m[a-1][-3:-1]:					# If the last elmnt is eq to prev elmnt
						poops += 1										# Poops increase by one
					# Here to decide the num of poops is gt 2 | le 2
					if poops > 2:										# If poops gt 2
						poops = 0										# Reset poops to 0
						final_ary[c].append("/".join(m[a][:-1]) + "/*")
						# print("/".join(m[a][:-1]) + "/*")
					elif poops <= 2:									# If poops le 2
						poops = 0										# Reset poops to 0
						final_ary[c].append("/".join(m[a]))
						# print("/".join(m[a]))
				# Condition 1.3
				else:													# If a not 1st and last elmnt
					if m[a][-3:-1] == m[a+1][-3:-1]:					# If the cur elmnt same with next elmnt
						poops += 1										# Poops increase by one
					if m[a][-3:-1] != m[a+1][-3:-1] and poops > 2:		# If the cur elmnt not eq to prev elmnt and poops gt 2
						poops = 0										# Rest poops to 0
						final_ary[c].append("/".join(m[a][:-1]) + "/*")
						# print("/".join(m[a][:-1]) + "/*")
					elif m[a][-3:-1] != m[a+1][-3:-1] and poops <= 2:	# If cur elmnt not eq next elmnt and poops le 2
						poops = 0										# Reset poops to 0
						final_ary[c].append("/".join(m[a]))
						# print("/".join(m[a]))
					elif m[a][-3:-1] != m[a-1][-3:-1] and m[a][-3:-1] == m[a+1][-3:-1] and poops <= 2:				# if the cur elmnt not eq prev and eq to next and poops gt 2			
						if(m[a][-1] == ""):																			# if the last elmnt is ""
							final_ary[c].append("/".join(m[a]))
							# print("/".join(m[a]))
							if m[a+1][-3:-1] == m[a+2][-3:-1] and m[a+2][-3:-1] != m[a+3][-3:-1]:					# 	if cur+1 eq cur+2 and cur+2 eq cur+3
								final_ary[c].append("/".join(m[a+1]))
								# print("/".join(m[a+1]))
						elif a+2 == len(m) or a+3 == len(m) or a+1 == len(m) and m[a][-3:-1] == m[a+1][-3:-1]:		# If cur+1/+2/+3 eq last index of ary and cur eq cur+1 
							final_ary[c].append("/".join(m[a]))
							# print("/".join(m[a]))
						elif m[a+1][-3:-1] == m[a+2][-3:-1] and m[a+2][-3:-1] != m[a+3][-3:-1]:						# If cur+1 eq cur+2 and cur+2 eq cur+3
							final_ary[c].append("/".join(m[a]))
							final_ary[c].append("/".join(m[a+1]))
							# print("/".join(m[a]))
							# print("/".join(m[a+1]))
						elif m[a+1][-3:-1] != m[a+2][-3:-1]:														# If cur+1 not eq cur+2
							final_ary[c].append("/".join(m[a]))
							# print("/".join(m[a]))
						elif m[a][-3:-1] == m[a-1][-3:-1] and m[a][-3:-1] == m[a+1][-3:-1] and m[a][-3:-1] != m[a+2][-3:-1]: # iF cur eq cur-1 and cur eq cur+1 and cur eq cur+2
							final_ary[c].append("/".join(m[a]))
							# print("/".join(m[a]))
			except:
				print("Error")		# Any exceptions print here
		final_ary[c].insert(0, title_ary[c])
		# print()									# Make space between each seperate finding
	else:
		final_ary[c].insert(0, title_ary[c])

# Finally print all the merged findings out
for ary in final_ary:
	for elmnt in ary:
		print(elmnt)
	print()

# For manual testing of each urls #
# print(main_ary[3][0][-3:-1])	# Debug
# print(main_ary[4])						# Debug
# poops = 0
# m = main_ary[5]		# Edit this array number
# for a in range(len(m)):
# 	# print(m[a][-3:-1])
# 	try:
# 		if a == 0:
# 			if m[a][-3:-1] == m[a+1][-3:-1]:
# 				poops += 1
# 			elif m[a][-3:-1] != m[a+1][-3:-1]:
# 				print("/".join(m[a]))
# 		elif a == len(m)-1:
# 			if m[a][-3:-1] == m[a-1][-3:-1]:
# 				poops += 1
# 			if poops > 2:
# 				poops = 0
# 				print("/".join(m[a][:-1]) + "/*")
# 			elif poops <= 2:
# 				poops = 0
# 				print("/".join(m[a]))
# 		else:
# 			if m[a][-3:-1] == m[a+1][-3:-1]:
# 				poops += 1
# 			if m[a][-3:-1] != m[a+1][-3:-1] and poops > 2:
# 				poops = 0
# 				print("/".join(m[a][:-1]) + "/*")
# 			elif m[a][-3:-1] != m[a+1][-3:-1] and poops <= 2:
# 				poops = 0
# 				print("/".join(m[a]))
# 			elif m[a][-3:-1] != m[a-1][-3:-1] and m[a][-3:-1] == m[a+1][-3:-1] and poops <= 2:
# 				if(m[a][-1] == ""):
# 					print("/".join(m[a]))
# 					if m[a+1][-3:-1] == m[a+2][-3:-1] and m[a+2][-3:-1] != m[a+3][-3:-1]:
# 						print("/".join(m[a+1]))
# 				elif a+2 == len(m) or a+3 == len(m) or a+1 == len(m) and m[a][-3:-1] == m[a+1][-3:-1]:
# 					print("/".join(m[a]))
# 				elif m[a+1][-3:-1] == m[a+2][-3:-1] and m[a+2][-3:-1] != m[a+3][-3:-1]:
# 					print("/".join(m[a]))
# 					print("/".join(m[a+1]))
# 				elif m[a+1][-3:-1] != m[a+2][-3:-1]:
# 					print("/".join(m[a]))
# 				elif m[a][-3:-1] == m[a-1][-3:-1] and m[a][-3:-1] == m[a+1][-3:-1] and m[a][-3:-1] != m[a+2][-3:-1]:
# 					print("/".join(m[a]))
# 	except:
# 		print("Error in 'i': " + a)