FROM python:3.12-alpine as builder

ADD requirements.txt .
RUN apk add build-base linux-headers; pip install -r requirements.txt --no-deps

RUN mkdir /usr/src/models
WORKDIR /usr/src

ADD app/api.py app/manage.py ./
ADD app/templates/ ./templates

CMD ["flask", "--app", "api", "run"]
