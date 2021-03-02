#!/usr/bin/python
from datetime import datetime
from json import dumps, loads
from os import environ, path, listdir, system
import pathlib
import boto3
import requests
from time import sleep
from aws_xray_sdk.core import xray_recorder

"""
Initialize the function.
"""
cc = boto3.client('codecommit')
cg = boto3.client('codeguru-reviewer')

@xray_recorder.capture('cache_associations')
def cache_associations() -> dict:
  cache = {}

  response =cg.list_repository_associations(MaxResults=100)
  for item in response['RepositoryAssociationSummaries']:
    name = item['Name']
    cache[name] = item

  while('NextToken' in response):
    response = cg.list_repository_associations(
      MaxResults=100,
      NextToken=response['NextToken'])

    for item in response['RepositoryAssociationSummaries']:
      name = item['Name']
      cache[name] = item

  return cache

associations = cache_associations()

@xray_recorder.capture('process-event')
def process_event(e:dict):
  repository_name = e['repository_name']
  xray_recorder.current_subsegment().put_metadata('repository_name',repository_name)

  association = associations[repository_name]
  
  # Find all branches...
  branches=[]
  response = cc.list_branches(
    repositoryName=repository_name)
  branches.extend(response['branches'])
  
  while("NextToken" in response):
    response = cc.list_branches(
      repositoryName=repository_name,
      nextToken = response['NextToken'])

    branches.extend(response['branches'])

  # Process each branch...
  xray_recorder.current_subsegment().put_metadata('branches',str(branches))  
  for branch in branches:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    response = cg.create_code_review(
      Name='Analyze-{}'.format(timestamp),
      RepositoryAssociationArn= association['AssociationArn'],
      Type={
        "RepositoryAnalysis":{
          "RepositoryHead":{
            "BranchName":branch
          }
        }
      })

  print(dumps({
    "repository_name": repository_name,
    "branches": branches
  }))

# https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
def handle_event(request, context):
  """
  Entry point for Lambda function
  """
  print(dumps(request))
  for record in request['Records']:
    body = record['body']
    print(body)

    e = loads(body)
    process_event(e)

if __name__ == "__main__":
  base_path = path.dirname(__file__)
  with open(path.join(base_path, 'example-payload.json'),'r', encoding='utf8') as f:
    request = loads(f.read())
    handle_event(request, None)
