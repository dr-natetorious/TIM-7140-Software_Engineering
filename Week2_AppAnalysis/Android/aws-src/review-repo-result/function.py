#!/usr/bin/python
from datetime import datetime
from json import dumps, loads
from os import environ, path, listdir, system
import pathlib
import boto3
import requests
from time import sleep
#from aws_xray_sdk.core import xray_recorder

"""
Initialize the function.
"""
reviewer = boto3.client('codeguru-reviewer')

def list_code_reviews():
  """
  Find all code reviews
  """
  response = reviewer.list_code_reviews(
    Type='RepositoryAnalysis',
    States=['Completed'],
    MaxResults=100)

  for summary in response['CodeReviewSummaries']:
    process_code_findings(summary)

  while 'NextToken' in response:
    response = reviewer.list_code_reviews(
      Type='RepositoryAnalysis',
      States=['Completed'],
      NextToken=response['NextToken'],
      MaxResults=100)

    for summary in response['CodeReviewSummaries']:
      process_code_findings(summary)

def process_code_findings(summary:dict):
  """
  Process this specific entry
  """
  review_arn = summary['CodeReviewArn']
  metrics = summary['MetricsSummary']
  if metrics['FindingsCount'] == 0:
    print("No findings, skipping...")
    return

  description = reviewer.describe_code_review(CodeReviewArn=review_arn)['CodeReview']
  repository = description['RepositoryName']
  branch = description['SourceCodeType']['RepositoryHead']['BranchName']

  document = {
    "arn":review_arn,
    "repository_name":repository,
    "branch": branch,
    "issues": metrics['FindingsCount']
  }
  print(dumps(document))
  attach_recommendations(document)

def attach_recommendations(document:dict):
  """
  Download the 
  """
  recs = []
  response = reviewer.list_recommendations(CodeReviewArn=document['arn'])
  recs.extend(response['RecommendationSummaries'])

  while 'NextToken' in response:
    response = reviewer.list_recommendations(
      CodeReviewArn=document['arn'],
      NextToken=response['NextToken'])

    recs.extend(response['RecommendationSummaries'])

  document['recommendations'] = recs

if __name__ == "__main__":
  list_code_reviews()