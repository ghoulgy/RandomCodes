from boilerpipe.extract import Extractor
import sys

try:
  with open("sites.txt", "r", encoding="utf-8") as fr:
    links = fr.readlines()
except IOError:
  print("File not found!")

filename = "article_"
print("Total Links: {:d} ".format(len(links)))

for i, link in enumerate(links):
  try:
    extractor = Extractor(extractor='ArticleExtractor', url=link.strip())
  except Exception:
    print("404 Page Skip")
    continue
  extracted_text = extractor.getText().encode("utf-8")
  article = open(filename + str(i+1) + ".txt", "wb")
  article.write(extracted_text)
  close = article.close()
  print("{:s}.txt : OK! out of {:d}.\n".format((filename+str(i+1)), len(links)))
  # sys.stdout.write(filename + str(i+1) + ".txt : OK!\n")

fr.close()

# link = "http://wordfakk.com/mobilnyj-bankovskij-trojan-asacub-nachal-masshtabnye-ataki/"
# try:
#   extractor = Extractor(extractor='ArticleExtractor', url=link)
# except Exception:
#   print("404")
# extracted_text = extractor.getText().encode("utf-8")
# article = open(filename + str(2) + "_test.txt", "wb")
# article.write(extracted_text)
# article.close()

# print(extracted_text)
