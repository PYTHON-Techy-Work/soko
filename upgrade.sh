#!/usr/bin/env bash
FLASK_DEBUG=1 FLASK_APP=`pwd`/autoapp.py flask db migrate
FLASK_DEBUG=1 FLASK_APP=`pwd`/autoapp.py flask db upgrade