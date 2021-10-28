#! /usr/bin/python

from app import app as application
import logging
import sys

sys.path.append("/var/www/apache-flask/app)

logging.basicConfig(stream=sys.stderr)