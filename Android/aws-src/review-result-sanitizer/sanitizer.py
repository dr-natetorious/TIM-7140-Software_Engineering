from models import CodeReview, Recommendation

def sanitize_code_review(code_review:CodeReview):
  for rec in code_review.recommendations:
    sanitize_recommendation(rec)

def sanitize_recommendation(rec:Recommendation):
  description = rec.description
  description = description.replace('\n',' ')
  tokens= []
  
  for word in description.split(' '):    
    if is_symbol_name(word):
      tokens.append('{term}')
    elif word.endswith('%'):
      tokens.append('{per}')
    elif is_url(word):
      tokens.append(word)
    elif has_path(word):
      tokens.append('{path}')
    elif is_methodname(word):
      tokens.append('{method}')
    elif is_num(word):
      tokens.append('{num}')
    else:
      tokens.append(word)

  sanitized = ' '.join(tokens)
  rec.set_sanitized_descr(sanitized)

def is_symbol_name(word):
  for prefix in ['*','`','"',"'"]:
    if word.startswith(prefix):
      return True
  return False

def has_path(word)->bool:
  return "/" in word

def is_url(token)->bool:
  if "http://" in token or "https://" in token:
    return True
  return False

def is_methodname(token)->bool:
  if "." in token and not token.endswith('.'):
    return True
  return False

def is_num(token):
  if len(token) == 0:
    return False
  
  _, ret = intTryParse(token)
  if ret == True:
    return True
  
  return token[0].isdigit() or token[-1].isdigit()

def intTryParse(value):
  try:
    return int(value), True
  except ValueError:
    return value, False