docker run -it --rm -e SONAR_HOST_URL="http://droid-sonar-1txszpmm6f4fr-1909480520.us-east-2.elb.amazonaws.com/" -e SONAR_LOGIN="e86d09d1e4a4fa9593cfc848ac6a62d0b1ee4e9d" -v "s:\tmp\ipfs-lite:/usr/src" sonarsource/sonar-scanner-cli -D sonar.projectKey=test -D sonar.login=admin -D sonar.password=P@$$word sonar.java.binaries=/usr/src/bin