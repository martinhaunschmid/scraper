FROM python:alpine3.19

RUN apk update && apk upgrade

WORKDIR /app
COPY src .

COPY crontab /crontab
RUN crontab /crontab

RUN mkdir -p /logs

RUN pip3 install -r requirements.txt

CMD ["crond", "-f"]