FROM python:3.7-alpine
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN apk add bash && apk add curl
RUN apk add chromium chromium-chromedriver
RUN apk add -U tzdata
RUN apk add redis
ADD ./requirements.txt /usr/src/app
RUN pip install -r /usr/src/app/requirements.txt