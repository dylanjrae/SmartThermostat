#! /usr/bin/python 3.7
#get venv working

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/pi/Documents/SmartThermostat/WebDev/')
from app import app as application