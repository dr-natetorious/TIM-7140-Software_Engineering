FROM debian
LABEL Maintainer="Nate Bachmeier"
LABEL Course="TIM-7140 Software Engineering"
LABEL Org="Northcentral University"
LABEL Source="github://dr-natetorious"

RUN apt-get -y update
RUN RUN apt-get -y install git zip sqlite

WORKDIR /git
RUN git clone --depth 1 https://github.com/AndroSec/AndroSecDatabases

