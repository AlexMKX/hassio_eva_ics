#!/usr/bin/env python3
from __future__ import annotations

import os.path

from pydantic_settings import BaseSettings
from pydantic import PrivateAttr, field_validator
from typing import List, Any, Dict, Optional, Union
from pydantic import Field
import requests

import jinja2
import yaml
import logging

import eva_ics
from eva_ics import hassio_config

CONFIG: MySettings
HASSIO_CONFIG: dict
TEMPLATES_ROOTS: list[str] = [os.path.join(os.getenv('PYEVA_ROOT'), 'modbus2mqtt/templates')]


class TrackedSettings(BaseSettings):
    _id: str = PrivateAttr()
    _parent: TrackedSettings = PrivateAttr()

    def model_post_init(self, __context):
        for f in self.model_fields:
            x = getattr(self, f)
            if issubclass(x.__class__, dict):
                for k, v in x.items():
                    if issubclass(v.__class__, TrackedSettings):
                        v._id = k
                        v._parent = self
            elif issubclass(x.__class__, TrackedSettings):
                x._id = None
                x._parent = self

    @property
    def id(self):
        return f'{self._id}'

    @property
    def parent(self):
        return self._parent


class MqttConfig(TrackedSettings):
    eva: Optional[Dict[str, Any]] = Field(default=None)
    base_topic: str

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
        return rv


class MySettings(TrackedSettings):
    mqtt: Optional[Dict[str, MqttConfig]]
    modbus2mqtt: Dict[str, ModbusConfig]

    @field_validator('mqtt')
    def mqtt_validator(cls, v, values):
        if 'hassio' in v.keys():
            logging.error(f'The "hassio" key is reserved for auto-config')
            raise RuntimeError(f'The "hassio" key is reserved for auto-config')
        return v

    def model_post_init(self, __context):
        if eva_ics.hassio_config() is not None:
            d = MqttConfig(**(MqttConfig.hassio_default()))
            self.mqtt['hassio'] = d

    @classmethod
    def load(cls, filename_or_b64: str):
        config = yaml.load(open(filename_or_b64, 'r'), Loader=yaml.FullLoader)
        return cls(**config)


class ModbusConfig(TrackedSettings):
    mqtt: str
    eva: Dict[str, Any]
    devices: Dict[str, DeviceSettings]

    def get_svc_config(self):
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
        return rv

    def _get_pullers(self) -> List[Dict[str, Any]]:
        rv = []
        for d in self.devices.values():
            rv.extend(d.puller_config)
        return rv


class DeviceSettings(TrackedSettings):
    kind: str
    slave: int
    _from_modbus: PrivateAttr(jinja2.Template)
    _to_mqtt: PrivateAttr(jinja2.Template)

    def model_post_init(self, __context):
        global TEMPLATES_ROOTS
        configured = False
        for r in TEMPLATES_ROOTS:
            try:
                fld = os.path.join(r, self.kind)
                env = jinja2.Environment(loader=jinja2.FileSystemLoader(fld), undefined=jinja2.StrictUndefined)
                self._from_modbus = env.get_template('from-modbus.yml.j2')
                self._to_mqtt = env.get_template('to-mqtt.yml.j2')
                configured = True
                logging.info(f'Configured {self.kind} from {fld}')
            except Exception as e:
                pass
        if not configured:
            raise Exception(f'No working templates found for {self.kind}')

    @property
    def eva_id(self):
        return f'{self.parent.id}.{self.id}'

    @property
    def mqtt(self) -> MqttConfig:
        return CONFIG.mqtt[self.parent.mqtt]

    @property
    def puller_config(self) -> List[Dict[str, Any]]:
        return yaml.safe_load(self._from_modbus.render(item=self, id=self.eva_id))

    @property
    def output_config(self) -> List[Dict[str, Any]]:
        return yaml.safe_load(self._to_mqtt.render(item=self, id=self.eva_id))


def module_main():
    import os
    global CONFIG
    global TEMPLATES_ROOTS
    try:
        CONFIG = MySettings.load(os.path.join(os.environ.get('PYEVA_CONFIG', ''), 'modbus2mqtt.yml'))
    except Exception as e:
        logging.error(f'Failed to load config: {e}')
        return
    if hassio_config() is not None:
        logging.info('Home assistant detected')
        f = "/homeassistant/addons/eva_ics/modbus2mqtt/templates"
        os.makedirs(f, exist_ok=True)
        TEMPLATES_ROOTS.insert(0, "/homeassistant/addons/eva_ics/modbus2mqtt/templates")

    deploy_modbus = {
        'version': 4,
        'content': [
            {
                'node': '.local',
                'svcs': []
            }
        ]

    }
    deploy_mqtt = {
        'version': 4,
        'content': [
            {
                'node': '.local',
                'svcs': []
            }
        ]

    }

    for k, v in CONFIG.modbus2mqtt.items():
        deploy_modbus['content'][0]['svcs'].append(v.get_svc_config())
    for k, v in CONFIG.mqtt.items():
        deploy_mqtt['content'][0]['svcs'].append(v.get_svc_config())

    with open('/mnt/init/init-0-modbus-0.yml', 'w') as f:
        f.write(yaml.dump(deploy_modbus))
    with open('/mnt/init/init-1-mqtt-0.yml', 'w') as f:
        f.write(yaml.dump(deploy_mqtt))
