#!/bin/sh

uwsgi -H `dirname $0`/venv --gevent 100 --gevent-monkey-patch --http :8000 --module prod:app
