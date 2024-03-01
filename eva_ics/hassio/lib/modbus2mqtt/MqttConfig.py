from TrackedSettings import TrackedSettings
from typing import List, Any, Dict, Optional
from pydantic import Field
import eva_ics


class MqttConfig(TrackedSettings):
    eva: Optional[Dict[str, Any]] = Field(default=None)
    base_topic: str
    discovery_topic: str = Field(default="homeassistant")

    @classmethod
    def hassio_default(cls) -> dict[str, Any]:
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
            "base_topic": "lab/test"
        }
        return rv

    @property
    def eva_id(self) -> str:
        return f'eva.controller.{self.id}'

    def get_svc_config(self) -> dict[str, Any]:

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
        for mk, mv in self.parent.modbus.items():
            for dk, dv in mv.devices.items():
                if dv.mqtt.id == self.id:
                    rv['params']['config']['output'].extend(dv.output_config)
                    rv['params']['config']['input'] = []
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
