EvaICS for HomeAssistant addon
==============================


This addon provides bridge between EvaICS SCADA and HomeAssistant.
It creates the :doc:`external/hassio/lib/modbus2mqtt/doc/index` to connect Modbus devices controlled by EvaICS with HomeAssistant.

Addon installation
==================
Navigate to the Addons section of HomeAssistant and add the following repository URL: `https://github.com/AlexMKX/hassio_eva_ics`

After store refresh you'll be able to install it. **Do not forget to turn on the watchdog and autostart**

Configuration
=============
The configuration files are located in the addons/eva_ics directory. The Modbus2MQTT configuration file is modbus2mqtt.yml.
The sample file will be created automatically after the first start of the addon. You can edit it to fit your needs. More info on configuration in :doc:`external/hassio/lib/modbus2mqtt/doc/configuration`

Adding new devices
==================
To add a new device addon, you can add the python code for building device configuration to the addons/eva_ics/modbus2mqtt/devices in to the subdirectory with the device name. Either in __init__.py or devicename.py file.
Example device configuration is in the :doc:`external/hassio/modbus2mqtt/devices/doc/examples`


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   external/hassio/lib/modbus2mqtt/doc/index