#!/bin/bash

outfile=/mnt/efs/sanitized-messages.txt
rm -f $outfile

for x in `find /mnt/efs/review-result-sanitizer | grep code_review.json`; do
  cat $x | jq '.recommendations[].Sanitized' >> $outfile
done  