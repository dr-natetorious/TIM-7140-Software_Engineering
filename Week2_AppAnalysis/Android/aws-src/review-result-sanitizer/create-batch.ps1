$bucket="droidanlyz-storagelayerandroidproducts4c17745e-1pwfyncc67j3e"
$files = aws s3 ls --recursive s3://$bucket/codeguru/raw | %{ $_.substring("2021-03-02 15:50:09       1119 ".length)}
$files | %{"$bucket,$_" } | out-file -filepath "batch.csv" -Encoding utf8

aws s3 cp batch.csv s3://$bucket/review-result-sanitizer.csv
