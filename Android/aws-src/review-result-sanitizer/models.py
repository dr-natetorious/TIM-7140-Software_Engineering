from typing import List

class Recommendation:
  """
  Represent an individual recommendation
  """
  def __init__(self,json:dict):
    self.__json = json

  @property
  def json(self)->dict:
    return self.__json

  @property
  def filePath(self)->dict:
    return self.json['FilePath']

  @property
  def recommendationId(self)->str:
    return self.json['RecommendationId']

  @property
  def start_line(self)->int:
    return self.json['StartLine']

  @property
  def end_line(self)->int:
    return self.json['EndLine']

  @property
  def description(self)->str:
    return self.json['Description']

  def set_sanitized_descr(self,description:str)->None:
    self.json['Sanitized'] = description

class CodeReview:
  """
  Represents a code review
  """
  def __init__(self,json:dict):
    self.__json = json
    self.__rec = [Recommendation(x) for x in self.json['recommendations']]

  @property
  def json(self)->dict:
    return self.__json

  @property
  def arn(self)->str:
    return self.json['arn']

  @property
  def repository_name(self)->str:
    return self.json['repository_name']

  @property
  def branch(self)->str:
    return self.json['branch']

  @property
  def metrics(self)->dict:
    return self.json['metrics']

  @property
  def recommendations(self)-> List[Recommendation]:
    return self.__rec
