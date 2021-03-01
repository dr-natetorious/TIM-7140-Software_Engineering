#!/bin/bash

bucket=$1
echo ============================
echo Bucket: $bucket
echo ============================

###
# Iterate through all pages
###

if [ -z $bucket ]; then
  echo 'ERR: No bucket specified'
  return -1
fi

for category in `cat categories.txt`; do
  for ix in `seq 2 100`; do
    url=https://f-droid.org/en/categories/$category/$ix/index.html
    echo "Downloading: $url"
    http_status=`curl -s -o /tmp/raw.htm -w "%{http_code}" $url`
    
    # Did we reach the end?
    if [ "$http_status" -ne "200" ]; then
      echo "Received $http_status != 200"
      break
    fi

    cat /tmp/raw.htm | grep 'package-header' | grep en | tr -d ' ' | cut -d '=' -f 3 | tr -d '">' > /tmp/download.$category.$ix.list
    aws s3 cp /tmp/download.$category.$ix.list s3://$bucket/$category/$ix.list
  done
done
