FROM debian:stretch
LABEL Maintainer="Nate Bachmeier"
RUN apt-get -y update
RUN apt-get -y install curl awscli

WORKDIR /app
COPY . /app
ENTRYPOINT [ "/app/download.sh", "${BUCKET_NAME}" ]