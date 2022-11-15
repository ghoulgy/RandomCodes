import re
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
 
 
def hash_extract(s):
  str_length = len(s.rstrip())
  hash_match = False
  # print(s)
  # print("===")
  if str_length == 64:
    hash_match = re.search("[0-9A-z]{64}", s)
    
  elif str_length == 40:
    hash_match = re.search("[0-9A-z]{40}", s)
    
  elif str_length == 32: 
    hash_match = re.search("[0-9A-z]{32}", s)
 
  elif s.find('(', 0, 1) != -1: # Ahnlab format (md5 hash)
    hash_match = re.search("[0-9A-z]{32}", s)    
 
  if hash_match:
    return hash_match.group(0)
 
  else: 
    return None
 
 
def preprocess_1(s):
  hash_list = []
 
  for splited in s.split():
    if hash_extract(splited): # if return is not None
      hash_list.append(hash_extract(splited))
 
  if hash_list:
    return hash_list
  
  else:
    return None
 
 
def main_content_process(soup, preprocess_stage, tag):
  hash_list_str = ""
  hash_list_str_td = "" # welivesecurity
 
  for tag_item in soup.select(tag):
    # print(tag_item.get_text())
    # print("===")
    if preprocess_stage == 1:
      hash_list = preprocess_1(tag_item.get_text())
 
    else:
      hash_list = hash_extract(tag_item.get_text())
    
    if hash_list:
      if isinstance(hash_list, list):
        for hash_str in hash_list:
          hash_list_str += hash_str + "\n"
 
      elif tag == "td":
        hash_list_str_td += hash_list + "\n"
 
  if hash_list_str:
    return hash_list_str
 
  elif hash_list:
    return hash_list
 
  elif hash_list_str_td:
    return hash_list_str_td
 
  return None
 
 
async def web_page_download(session, url):
  try:
    async with session.get(url, ssl=False) as resp:
      assert resp,status == 200
      return await resp.read()
 
  except aiohttp.ClientConnectorSSLError as e:
    assert isinstance(e, ssl.SSLError)
 
 
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
async def main(url_list):
  async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
    tasks = []
 
    for url in url_list:
      tasks.append(asyncio.ensure_future(web_page_download(session, url.rstrip())))
 
    web_content_list = await asyncio.gather(*tasks)
 
    return zip(url_list, web_content_list)
 
 
def content_process(url, page):
    soup = BeautifulSoup(page, "html.parser")
 
    print(f"[+] {url}")
    if url.find("welivesecurity") != -1:
      print(main_content_process(soup, 0, "td"))
 
    elif url.find("securelist") != -1 or url.find("zscaler") != -1:
      print(main_content_process(soup, 1, "p"))
 
    elif url.find("abnormal") != -1:
      for strong_tag in soup.select('div.BodyText__content > p[dir="ltr"] > strong'): # Remove <strong>
        strong_tag.decompose()
 
      print(main_content_process(soup, 1, 'div.BodyText__content > p[dir="ltr"]'))
 
    elif url.find("talosintelligence") != -1:
      html_tag_1 = main_content_process(soup, 1, "span")
      html_tag_2 = main_content_process(soup, 1, "div.threat-roundup-content")
 
      if html_tag_1:
        print(html_tag_1)
 
      elif html_tag_2:
        print(html_tag_2)
 
    elif url.find("intezer") != -1:
      print(main_content_process(soup, 1, "pre.wp-block-prismatic-blocks"))
 
    elif url.find("symantec") != -1:
      print(main_content_process(soup, 1, "div > p"))
 
    elif url.find("paloaltonetworks") != -1:
      print(main_content_process(soup, 1, "p > span"))
 
    elif url.find("mandiant") != -1:
      print(main_content_process(soup, 1, "table > tbody > tr > td"))
      print(main_content_process(soup, 0, "span"))
 
    elif url.find("malwarebytes") != -1:
      print(main_content_process(soup, 0, "table > tbody > tr > td"))
 
    elif url.find("cyble") != -1:
      print(main_content_process(soup, 1, "figure.wp-block-table > table > tbody > tr > td"))
 
    elif url.find("ahnlab") != -1:
      print(main_content_process(soup, 1, "p"))
 
    elif url.find("vmware") != -1:
      print(main_content_process(soup, 1, "table > tbody > tr > td"))
 
    else:
      print("[-] Not in the list")
 
 
if __name__ == "__main__":
  with open("url.txt", "r") as f_url:
    url_list = f_url.readlines()
 
  url_content_list = asyncio.run(main(url_list))
  
  for url, content in url_content_list:
    content_process(url, content.decode())