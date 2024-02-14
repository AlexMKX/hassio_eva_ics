import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

import eva_ics

eva_ics.init()

import modbus2mqtt

modbus2mqtt.module_main()
