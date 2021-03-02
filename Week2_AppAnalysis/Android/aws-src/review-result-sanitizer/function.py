#!/usr/bin/python
from models import CodeReview
from datetime import datetime
from json import dumps, loads
from sanitizer import sanitize_code_review
from os import environ, path, listdir, system
import pathlib
import boto3
import requests
from time import sleep
#from aws_xray_sdk.core import xray_recorder

s3 = boto3.resource('s3')

def process_file(json:dict):
  code_review = CodeReview(json)
  sanitize_code_review(code_review)

  with open('scratch.json','w+') as f:
    f.write(dumps(code_review.json, indent=True))

def handle_event(request, handler):
  """
  Entry point for Lambda function
  """
  print(dumps(request))
  #print(listdir(base_outdir))
  bucket = request['tasks'][0]['s3BucketArn'].split(':')[-1]
  key = request['tasks'][0]['s3Key']

  response = s3.Object(bucket_name=bucket, key=key).get()
  content = response['Body'].read().decode("utf-8")

  process_file(loads(content))

  return {
    "invocationSchemaVersion": "1.0",
    "treatMissingKeysAs" : "TemporaryFailure",
    "invocationId" : request['invocationId'],
    "results": [
      {
        "taskId": request['tasks'][0]['taskId'],
        "resultCode": "Succeeded",
        "resultString": "[No errors]"
      }
    ]
  }

if __name__ == '__main__':
  base_path = path.join(path.dirname(__file__),'Payloads')
  with open(path.join(base_path,'r3.9.rec.json'),'r',encoding='utf8') as f:
    process_file(loads(f.read()))
