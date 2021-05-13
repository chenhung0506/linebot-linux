# FROM python:3.7-alpine
FROM chenhung0506/python-with-chrome:latest
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV TZ=Asia/Taipei
# RUN mkdir -p /usr/local/bin
# ADD ./module/linux_chromedriver/chromedriver /usr/local/bin
# RUN apk add chromium chromium-chromedriver
# ARG testArg=$(pwd)
# RUN echo "testArg: $testArg"
# RUN apk add bash
# RUN pip install -r /usr/src/app/requirements.txt
# ADD dev.env /usr/src/app
RUN pip install redis
ADD ./module /usr/src/app
# RUN apk add -U tzdata
# RUN dpkg-reconfigure tzdata
# RUN echo "Asia/Taipei" > /etc/timezone
RUN ls /usr/src/app
# HEALTHCHECK --interval=5s --timeout=5s --retries=5 CMD curl -f "http://localhost:${PORT}/healthcheck" || exit 1 
CMD ["python", "app.py"]
# ENTRYPOINT [ "/code/test.py" ]