FROM python:3.12-alpine as builder

ADD requirements.txt .
RUN apk add build-base linux-headers; pip install -r requirements.txt --no-deps

RUN mkdir /usr/src/models
WORKDIR /usr/src

ADD app/api.py app/manage.py ./
ADD app/templates/ ./templates

RUN pip install gunicorn

EXPOSE 8690

RUN addgroup -S mgl869 && adduser -S mgl869 -G mgl869 && chown mgl869:mgl869 /usr/src/models
USER mgl869

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8690", "api:app"]
