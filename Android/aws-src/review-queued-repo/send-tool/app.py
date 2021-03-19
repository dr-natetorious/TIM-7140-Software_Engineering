import boto3
from json import dumps
from os import path
from time import sleep
sqs = boto3.client('sqs')

def send_message(repository_name):
  response = sqs.send_message(
    QueueUrl='https://sqs.us-east-2.amazonaws.com/581361757134/DroidAnlyz-ComputePendingReviewQueue27D4C065-OGTA0D5ULY6G',
    MessageBody=dumps({
      "repository_name": repository_name
    }))

  print(dumps(
    {
      "repo":repository_name,
      "status": response['ResponseMetadata']['HTTPStatusCode']
    }))

  sleep(15)

if __name__ == "__main__":
  basepath = path.dirname(__file__)
  with open(path.join(basepath,'random.subset'),'r', encoding='utf8') as f:
    for repo in f.readlines():
      repo = repo.replace('\n','')
      #print('Processing: {}'.format(repo))
      send_message(repo)
