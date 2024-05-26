from __future__ import annotations

from pydantic import PrivateAttr, field_validator
from typing import List, Any, Dict, Optional, Union, LiteralString
from pydantic import Field
import yaml
import logging

import eva_ics
from MqttConfig import MqttConfig
from TrackedSettings import TrackedSettings
from ModbusConfig import ModbusConfig


class AppConfig(TrackedSettings):
    mqtt: Optional[Dict[str, MqttConfig]] = Field(default={})
    modbus: Dict[str, ModbusConfig]
    eva_deploy_dir: Optional[str] = Field(default='/mnt/init')
    discovery_topic: Optional[str] = Field(default="homeassistant")
    config_dump_path: Optional[str] = Field(default=None, description="Path to dump config")
    @field_validator('mqtt')
    def mqtt_validator(cls, v, values):
        """
        Validates the MQTT configuration. Checks that hassio is not used as a key because
        it reserved for auto-config for running in HomeAssistant environment.

        :param v: The MQTT configuration dictionary.
        :param values: Other configuration values.
        :return: The validated MQTT configuration.
        """
        if v is None:
            v = {}
        if 'hassio' in v.keys():
            logging.error(f'The "hassio" key is reserved for auto-config')
            raise RuntimeError(f'The "hassio" key is reserved for auto-config')
        return v

    @property
    def plugin_paths(self) -> List[str]:
        """
        Returns a list of plugin paths.
        if runs in HomeAssistant environment, the path to the user's plugin directory is added first.
        :return: A list of strings representing the paths to the plugins.
        :rtype: List[str]
        """
        import os
        rv = []
        if eva_ics.hassio_config() is not None:
            os.makedirs('/homeassistant/addons/eva_ics/modbus2mqtt/devices', exist_ok=True)
            rv.append('/homeassistant/addons/eva_ics/modbus2mqtt/devices')
        rv.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'modbus2mqtt', 'devices')))
        return rv

    def model_post_init(self, __context):
        """
        Post-initialization hook. Adding default MQTT configuration for HomeAssistant environment.
        :param __context:
        """
        if eva_ics.hassio_config() is not None:
            d = MqttConfig(**(MqttConfig.hassio_default()))
            self.mqtt['hassio'] = d
        super().model_post_init(__context)

    def apply_plugins(self):
        """
        Load the devices plugins
        """
        for m in self.modbus.values():
            m.apply_plugins(self)

    @classmethod
    def load(cls, filename: str):
        """
        Loads the configuration from a file.
        :param filename:
        :return:
        """
        try:
            config = yaml.load(open(filename, 'r'), Loader=yaml.FullLoader)
        except FileNotFoundError as e:
            import os, shutil
            logging.warning(f'Failed to load config: {e}, creating sample one')
            directory = os.path.dirname(__file__)

            # Source file path (relative to __file__)
            source_file = os.path.join(directory, 'doc/modbus2mqtt_minimal.yml')

            # Resolve the relative file path
            source_file = os.path.normpath(source_file)
            target_fld = os.path.dirname(filename)
            os.makedirs(target_fld, exist_ok=True)
            # Copy the file from source to destination
            shutil.copy(source_file, filename)

        return cls(**config)


CONFIG: AppConfig
