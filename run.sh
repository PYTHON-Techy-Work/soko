#!/bin/bash
export SOKO_SECRET='something-really-secret'
export FLASK_APP=`pwd`/autoapp.py
export FLASK_DEBUG=1

flask run