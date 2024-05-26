from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import AppConfig

from TrackedSettings import TrackedSettings
from typing import Union, Any, Dict, Optional
from pydantic import Field
import eva_ics


class MqttConfig(TrackedSettings):
    eva: Optional[Dict[str, Any]] = Field(default=None)
    base_topic: str
    discovery_topic: Optional[str] = Field(default=None, description="The discovery topic for MQTT")

    @classmethod
    def hassio_default(cls) -> Union[dict[str, Any], None]:
        """
        Returns the default configuration for HomeAssistant environment.
        :return:
        """
        cfg = eva_ics.hassio_config()
        if cfg is None:
            return None
        rv = {
            "eva": {
                "input_cache_sec": 3600,
                "pubsub": {
                    "proto": "mqtt",
                    "ca_certs": None,
                    "host": [f"{cfg['mqtt']['host']}:{cfg['mqtt']['port']}"],
                    "cluster_hosts_randomize": False,
                    "username": f"{cfg['mqtt']['username']}",
                    "password": f"{cfg['mqtt']['password']}",
                    "ping_interval": 10,
                    "queue_size": 1024,
                    "qos": 1
                }},
            "base_topic": "eva_ics"
        }
        return rv

    def get_discovery_topic(self) -> str:
        """
        returns discovery topic, either explicitly defined or default at AppConfig.
        :return: discovery topic
        """
        if self.discovery_topic is None:
            from config import CONFIG
            return CONFIG.discovery_topic
        return self.discovery_topic

    @property
    def eva_id(self) -> str:
        """
        Generates the EVA ID for the MQTT service.
        :return: Eva controller ID
        """
        return f'eva.controller.{self.id}'

    def get_svc_config(self) -> dict[str, Any]:
        """
        Returns the Eva's service configuration for the MQTT service.
        :return: Configuration according to the Eva's service format as described in
        `PubSub controller <https://info.bma.ai/en/actual/eva4/svc/eva-controller-pubsub.html?highlight=mqtt#setup>`_
        """
        rv = {
            'id': f'eva.controller.{self.id}',
            'params': {
                'command': 'svc/eva-controller-pubsub',
                'bus': {
                    'path': 'var/bus.ipc'
                },
                'config': self.eva
            }
        }
        if self.eva is None:
            rv['params']['config'] = self.get_hassio_config()
        rv['params']['config']['output'] = []
        rv['params']['config']['input'] = []
        for mk, mv in self.parent.modbus.items():
            for dk, dv in mv.devices.items():
                if dv.mqtt.id == self.id:
                    rv['params']['config']['output'].extend(dv.output_config)
                    for k, v in dv.input_config.items():
                        ic = {
                            "topic": v['topic'],
                            "map": [{
                                "path": v['path'] if 'path' in v.keys() else "$.",
                                "oid": k,
                                "process": "action"}]
                        }
                        rv['params']['config']['input'].append(ic)
        return rv
