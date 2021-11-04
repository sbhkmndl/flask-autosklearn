#!/usr/bin/env bash
gunicorn -w 1 --timeout 2000 -b 0.0.0.0:9094 wsgi:app