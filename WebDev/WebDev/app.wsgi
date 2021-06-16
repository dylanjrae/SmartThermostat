#! /usr/bin/python3.7

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/pi/Documents/SmartThermostat/WebDev/WebDev')
from app import app as application
# application.secret_key = 'pmwpmwpmw'
