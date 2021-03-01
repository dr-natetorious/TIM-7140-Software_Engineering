#!/usr/bin/python
from json import dumps
from os import environ, path, listdir
import pathlib
import boto3
import requests
from bs4 import BeautifulSoup
from aws_xray_sdk.core import xray_recorder

"""
Initialize the function.
"""
s3 = boto3.resource('s3')
base_url='https://f-droid.org'
base_outdir = environ.get('EFS_MOUNT')
if base_outdir == None:
  raise ValueError('EFS_MOUNT not specified')

@xray_recorder.capture('Process-Repo')
def process_repo(suffix):
  """
  Process one repository
  """
  xray_recorder.current_subsegment().put_metadata('suffix',suffix)
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

  # Next download the references...
  download_refs(project_htm)

@xray_recorder.capture('Download-ProjectFile')
def download_file(url, project_htm):
  xray_recorder.current_subsegment().put_metadata('project_htm',project_htm)

  headers = {'Accept-Encoding':'identity'}
  print(url)
  r = requests.get(url, headers=headers)
  
  with open(project_htm, 'w+') as f:
    f.write(r.text)

@xray_recorder.capture('Download-References')
def download_refs(project_htm):
  xray_recorder.current_subsegment().put_metadata('project_htm',project_htm)

  with open(project_htm, 'r', encoding='utf8') as f:
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
        download_apk(project_htm, href)
      elif "Source" in text:
        print("Source: "+href)

@xray_recorder.capture('Download-APK')
def download_apk(project_htm, apk_href):
  xray_recorder.current_subsegment().put_metadata('apk_href',apk_href)
  
  outdir = path.dirname(project_htm)
  outfile = path.join(outdir, path.basename(apk_href))

  if path.exists(outfile):
    return

  r = requests.get(apk_href)
  with open(outfile,'wb') as f:
    f.write(r.content)

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
