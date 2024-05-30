FROM python:alpine3.19

RUN apk update && apk upgrade

RUN apk add chromium

WORKDIR /app
COPY src .

COPY entry.sh /entry.sh

COPY crontab /crontab
RUN crontab /crontab

RUN mkdir -p /logs

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/bin/sh", "/entry.sh" ]