FROM alpine:3.6

ENV PYTHONBUFFERED 1

ARG APP_PATH=/hack-store

RUN apk --update add python3 python3-dev build-base linux-headers

COPY requirements.txt $APP_PATH/requirements.txt
RUN pip3 install -r $APP_PATH/requirements.txt

COPY . $APP_PATH

WORKDIR $APP_PATH

ENV GEVENT_N 100

CMD ["uwsgi", "--gevent", "echo ${GEVENT_N}", "--gevent-monkey-patch", "--http", ":8000", "--module", "prod:app"]

