#!/bin/bash

bucket = $1

function run_script {
  ###
  # Iterate through all pages
  ###

  if [ -z $bucket ]; then
    echo 'ERR: No bucket specified'
    return -1
  else

  for category in `cat categories.txt`; do
    for ix in `seq 1 100`; do
      http_status=`curl -o raw.htm -w "%{http_code}" https://f-droid.org/en/categories/$category/$ix/index.html`
      
      # Did we reach the end?
      if [ $http_status -ne 200]; then
        break
      fi

      cat raw.htm | grep 'package-header' | grep en | tr -d ' ' | cut -d '=' -f 3 | tr -d '">' > download.$category.$ix.list
      aws s3 cp download.$category.$ix.list s3://$bucket/$category/$ix.list
    done
  done
}

# Main entry point
run_script
