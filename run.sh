#!/bin/bash
source bin/activate
export FLASK_APP=wsgi.py
export FLASK_ENV=development
flask run