#!/usr/bin/python
from json import dumps
import boto3
import requests

def handle_event(request, handler):
  print(dumps(request))

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
