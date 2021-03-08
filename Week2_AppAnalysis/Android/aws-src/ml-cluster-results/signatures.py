#!/usr/bin/python3

from os import path
from json import dumps, loads
from typing import List

base_path = path.dirname(__file__)

def get_keyword_list()-> List[str]:
  with open(path.join(base_path,'./tfidf.json'),'r', encoding='utf8') as f:
    keyword_list= loads(f.read())
    return keyword_list

def get_signature(text):
  x =set(get_keyword_list())
  y =set(text.lower().split(' '))
  return ' '.join(list(x & y))

if __name__ == '__main__':
  """
  Generate the dependent files
  """
  # Open the sample files
  from sklearn.feature_extraction.text import TfidfVectorizer
  f = open(path.join(base_path,'./sanitized-messages.txt'))
  corpus = f.readlines()
  f.close()    

  # Calculate the tf-idf
  tfidf_vectorizer = TfidfVectorizer(stop_words='english',smooth_idf=True,norm='l2')
  tfidf_vector = tfidf_vectorizer.fit_transform(corpus)

  # Persist the keywords
  keywords = tfidf_vector.get_feature_names()
  with open(path.join(base_path,'./tfidf.json'),'w', encoding='utf8') as f:
    f.write(dumps(keywords))

