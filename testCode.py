import nltk
from nltk.tokenize import *
from nltk.corpus import stopwords
from string import punctuation
from nltk import ne_chunk
from nltk import conlltags2tree, tree2conlltags
from nltk.stem import PorterStemmer
from nltk.corpus import gutenberg

porter = PorterStemmer()

# word_list = open("word_list.txt",'w')

with open('extracted.txt', 'r') as f:
    content = f.readlines()

merge_sent = []
word_array = []
word_array_nopunct = []
a = ""
b = ""
c = []
d = []
# stopwords_en_withpunct = set(punctuation) # Remove Punctuation
stopwords_en = set(stopwords.words('english')) # Remove Common English Words
other_punct = {'``', '`', '“'}
final_punct = other_punct.union(set(punctuation))
stopwords_punct = stopwords_en.union(set(final_punct))
stopwords_en_withpunct = stopwords_en.union(stopwords_punct)

for line in content:
	a += line


# print(b)

# print(sent_tokenize(a))

for word in sent_tokenize(a):
	c += word_tokenize(word)

print(c)

# Stop words applied
# for word in c:
# 	if word not in stopwords_en_withpunct:
# 		d.append(word)

# print(d)

# With Porter Stemmer
# portered = []
# for s in d: 
# 	portered.append(porter.stem(s))

# print(portered)

# word_list.write(a)

# word_list.close()
f.close()