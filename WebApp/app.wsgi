#! /usr/bin/python


import logging
import sys

sys.path.append("/var/www/apache-flask/app/WebApp")

logging.basicConfig(stream=sys.stderr)
from app import app as application