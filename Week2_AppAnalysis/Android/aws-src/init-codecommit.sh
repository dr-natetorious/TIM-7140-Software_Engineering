#!/bin/bash

ls | shuff | head -n 1000 > random.subset
for name in `cat random.subset`; do
  aws codecommit --region us-east-2 create-repository --repository-name $name
done

for name in `cat random.subset`; do
  aws codeguru-reviewer --region us-east-2 associate-repository --repository "CodeCommit={Name=${name}}"
done

for name in `cat random.subset`; do
  pushd $name/code
  git push https://git-codecommit.us-east-2.amazonaws.com/v1/repos/$name --all
  git push https://git-codecommit.us-east-2.amazonaws.com/v1/repos/$name --tags
  popd
done