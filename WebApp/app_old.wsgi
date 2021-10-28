#! /usr/bin/python

from app import app as application
import logging
import sys

sys.path.insert(0,  '/home/pi/SmartThermostat/.venv/lib/python3.7/site-packages')
sys.path.insert(0, '/home/pi/SmartThermostat/WebDev/')

logging.basicConfig(stream=sys.stderr)

