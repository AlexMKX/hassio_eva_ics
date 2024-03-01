#!/usr/bin/env python3
from __future__ import annotations

import os.path
import logging
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from eva_ics import hassio_config

import config


def module_main():
    import os
    try:
        config_path = os.path.join(os.environ.get('HA_EVA_CONFIG', ''), 'modbus2mqtt.yml')
        logging.info(f'loading config from {config_path}')
        config.CONFIG = config.AppConfig.load(config_path)
        config.CONFIG.apply_plugins()
    except Exception as e:
        logging.error(f'Failed to load config: {e}')
        return
    if hassio_config() is not None:
        logging.info('Home assistant detected')

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
    logging.info(f'Using {config.CONFIG.eva_deploy_dir} as deployment target')
    os.makedirs(os.path.join(config.CONFIG.eva_deploy_dir, 'discovery'), exist_ok=True)
    import shutil
    shutil.rmtree(os.path.join(config.CONFIG.eva_deploy_dir, 'discovery'))
    os.makedirs(os.path.join(config.CONFIG.eva_deploy_dir, 'discovery'), exist_ok=True)
    import yaml, json
    for k, v in config.CONFIG.modbus.items():
        deploy_modbus['content'][0]['svcs'].append(v.get_svc_config())
        for dk, dv in v.devices.items():
            if dv.allow_discovery:
                d = dv.discovery
                with open(os.path.join(config.CONFIG.eva_deploy_dir, 'discovery', f'{dv.eva_id}.json'), 'w') as f:
                    f.write(json.dumps(d, indent=4))

    for k, v in config.CONFIG.mqtt.items():
        deploy_mqtt['content'][0]['svcs'].append(v.get_svc_config())

    with open(os.path.join(config.CONFIG.eva_deploy_dir, 'init-0-modbus-0.yml'), 'w') as f:
        #logging.info(yaml.dump(deploy_modbus))
        f.write(yaml.dump(deploy_modbus))
    with open(os.path.join(config.CONFIG.eva_deploy_dir, 'init-1-mqtt-0.yml'), 'w') as f:
        #logging.info(yaml.dump(deploy_mqtt))
        f.write(yaml.dump(deploy_mqtt))
