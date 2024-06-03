FROM python:alpine

RUN apk update && apk upgrade

RUN apk add chromium-chromedriver
RUN apk add gcompat

ENV PATH="/usr/bin/chromedriver:${PATH}"

WORKDIR /app
COPY src .

COPY entry.sh /entry.sh

COPY crontab /crontab
RUN crontab /crontab

RUN mkdir -p /logs

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/bin/sh", "/entry.sh" ]