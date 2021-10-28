

import logging
import sys

sys.path.insert(0,  '/home/pi/SmartThermostat/.venv/lib/python3.7/site-packages')


logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/pi/SmartThermostat/WebDev/')
from app import app as application