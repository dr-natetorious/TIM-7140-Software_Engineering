#!/usr/bin/python
from json import dumps, loads
from os import environ, path, listdir, system
import pathlib
import boto3
import requests
from aws_xray_sdk.core import xray_recorder

"""
Initialize the function.
"""
cc = boto3.client('codecommit')
cg = boto3.client('codeguru-reviewer')

def cache_associations() -> dict:
  cache = {}

  response =cg.list_repository_associations(MaxResults=1000)
  for item in response['RepositoryAssociationSummaries']:
    name = item['Name']
    cache[name] = item

  while('NextToken' in response):
    response = cg.list_repository_associations(
      MaxResults=1000,
      NextToken=response['NextToken'])

    for item in response['RepositoryAssociationSummaries']:
      name = item['Name']
      cache[name] = item

  return cache

associations = cache_associations()

def process_event(e:dict):
  repository_name = e['repository_name']
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
  for branch in branches:
    response = cg.create_code_review(
      Name='Analyze',
      RepositoryAssociationArn= association['AssociationArn'],
      Type={
        "RepositoryAnalysis":"RepositoryAnalysis",
        "RepositoryHead":"RepositoryHead",
        "BranchName":branch
      })

    print(response)

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
