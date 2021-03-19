$bucket = "droidanlyz-storagelayerandroidproducts4c17745e-1pwfyncc67j3e" 
$files = aws s3 ls --recursive s3://$bucket | findstr .list | %{ $_.substring("2021-03-01 13:13:19        747 ".length) }
$files | %{ "${bucket},$_"} | Out-File -FilePath "full_run.csv" -Encoding utf8

aws s3 cp .\full_run.csv s3://$bucket/fdroid-scrape-repo.csv