from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import sys

extracted = open("extracted.txt",'w', encoding="utf-8")

final_results = []

html = urllib.request.urlopen('https://www.theregister.co.uk/2017/08/02/banking_android_malware_in_uk/').read()
soup = BeautifulSoup(html, 'html.parser')
article_body = soup.find("div", {"id": "body"}).findAll("p")

for text in article_body:
	final_results.append(text.get_text())

p = " "

extracted.write(p.join(final_results))
extracted.close()
