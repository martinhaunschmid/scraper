FROM python:alpine

RUN apk update && apk upgrade

WORKDIR /app
COPY src .
RUN pip3 install -r requirements.txt

COPY entry.sh /entry.sh

COPY crontab /crontab
RUN crontab /crontab

RUN mkdir -p /logs

ENTRYPOINT [ "/bin/sh", "/entry.sh" ]