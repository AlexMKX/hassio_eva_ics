import logging

from TrackedSettings import TrackedSettings
from typing import List, Any, Dict, Optional
from pydantic import Field
from DeviceConfig import DeviceConfig

import config
import os


class ModbusConfig(TrackedSettings):
    mqtt: str = Field(default=os.environ.get('DEFAULT_MQTT', 'hassio'))
    eva: Dict[str, Any]
    devices: Dict[str, DeviceConfig]

    def get_svc_config(self):
        """
        Return the service configuration for the controller.

        :return: The service configuration dictionary.
        """
        rv = {
            'id': f'eva.controller.{self.id}',
            'params': {
                'command': 'svc/eva-controller-modbus',
                'bus': {
                    'path': 'var/bus.ipc'
                },
                'config': self.eva
            }
        }
        rv['params']['config']['pull'] = self._get_pullers()
        rv['params']['config']['action_map'] = self._get_action_maps()
        return rv

    def apply_plugins(self, __context):
        """
        Loads device plugins from the plugin paths.
        Load order: kind/__init__.py, kind/kind.py

        :param __context:
        :return: None
        """
        import DeviceConfig as ModDeviceConfig
        import os, sys
        sys.path.append(os.path.dirname(os.path.dirname(ModDeviceConfig.__file__)))
        import importlib.util
        to_remove = []
        for dk, dv in self.devices.items():
            paths = []
            loaded = False
            for plug_path in config.CONFIG.plugin_paths:
                paths.append(f"{plug_path}/{dv.kind}/__init__.py")
                paths.append(f"{plug_path}/{dv.kind}/{dv.kind}.py")
            for plug_path in paths:
                try:
                    logging.info(f'Loading plugin for {dv.kind} from {plug_path}')
                    os.stat(plug_path)
                    spec = importlib.util.spec_from_file_location(dv.kind, plug_path)
                    if spec is not None:
                        m = importlib.util.module_from_spec(spec)
                        z = spec.loader.exec_module(m)
                        self.devices[dk] = m.Device(**dv.model_dump())
                        loaded = True
                        break
                except Exception as e:
                    pass
            if not loaded:
                logging.warning(f'Failed to load plugin for {dv.kind}')
                to_remove.append(dk)
        for k in to_remove:
            logging.warning(f'Removing device {k}')
            self.devices.pop(k)
        self.propagate_children()

    def _get_action_maps(self) -> Dict[str, Any]:
        """
        Get all action maps from the devices.

        :return: A dictionary containing all the action maps from the devices.
        :rtype: Dict[str, Any]
        """
        rv = {}
        for d in self.devices.values():
            rv = {**rv, **d.action_map}
        return rv

    def _get_pullers(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dictionaries containing puller configurations.

        :return: A list of dictionaries representing puller configurations.
        :rtype: List[Dict[str, Any]]
        """
        rv = []
        for d in self.devices.values():
            rv.extend(d.puller_config)
        return rv
