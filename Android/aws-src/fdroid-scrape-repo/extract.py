import os
from bs4 import BeautifulSoup

base_path = os.path.dirname(__file__)

with open(os.path.join(base_path,'./project.htm'), 'r', encoding='utf8') as f:
  content = f.read()
  html = BeautifulSoup(markup=content)
  for link in html.find_all('a'):
    if 'href' not in link.attrs:
      continue

    href = str(link.attrs['href'])
    text = str(link.text)
    
    if href.endswith('F-Droid.apk'):
      continue
    elif href.endswith('.apk'):
      print(href)
    elif "Source" in text:
      print("Source: "+href)