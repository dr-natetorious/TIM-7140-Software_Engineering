#!/bin/bash
repo_url=$1
bucket=$2

tmp_page=/tmp/page.htm
curl -o $tmp_page $1 #https://f-droid.org/en/packages/de.storchp.fdroidbuildstatus/
git_repo= `cat $tmp_page  | grep '<a' | grep Source | cut -d '"' -f 2`
apks_releases= `cat $tmp_page | grep '.apk"'|cut -d '"' -f 2 | grep -v F-Droid.apk`

# Upload each milestone APK
for apk in $apks_releases; do
  apk_file="/tmp/`basename $apk`"
  curl -o $apk_file $apk
  aws s3 cp $apk_file s3://$bucket/apk/$apk_file
  rm $apk_file
done
