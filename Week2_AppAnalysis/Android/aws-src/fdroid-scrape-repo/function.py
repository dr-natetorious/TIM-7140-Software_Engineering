#!/usr/bin/python
from json import dumps
from os import environ, path, listdir
import pathlib
import boto3
import requests

"""
Initialize the function.
"""
s3 = boto3.resource('s3')
base_url='https://f-droid.org'
base_outdir = environ.get('EFS_MOUNT')
if base_outdir == None:
  raise ValueError('EFS_MOUNT not specified')

def process_repo(suffix):
  """
  Process one repository
  """
  if suffix == None:
    return

  # Determine output locations
  repo_path = path.join(base_outdir,path.basename(suffix))
  pathlib.Path(repo_path).mkdir(parents=True,exist_ok=True)
  project_htm = path.join(repo_path,'project.htm')

  # Download the file if missing...
  if not path.exists(project_htm):
    url = base_url+suffix
    download_file(url,project_htm)

def download_file(url, project_htm):
  headers = {'Accept-Encoding':'identity'}
  print(url)
  r = requests.get(url, headers=headers)
  
  with open(project_htm, 'w+') as f:
    f.write(r.text)

def handle_event(request, handler):
  """
  Entry point for Lambda function
  """
  print(dumps(request))
  print(listdir(base_outdir))
  bucket = request['tasks'][0]['s3BucketArn'].split(':')[-1]
  key = request['tasks'][0]['s3Key']

  response = s3.Object(bucket_name=bucket, key=key).get()
  content = response['Body'].read().decode("utf-8")

  for suffix in content.split('\n'):
    process_repo(suffix)

  return {
    "invocationSchemaVersion": "1.0",
    "treatMissingKeysAs" : "PermanentFailure",
    "invocationId" : request['invocationId'],
    "results": [
      {
        "taskId": request['tasks'][0]['taskId'],
        "resultCode": "Succeeded",
        "resultString": "[No errors]"
      }
    ]
  }
