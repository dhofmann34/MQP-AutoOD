#!/bin/bash
source bin/activate
export FLASK_APP=application/wsgi.py
export FLASK_ENV=development
flask run