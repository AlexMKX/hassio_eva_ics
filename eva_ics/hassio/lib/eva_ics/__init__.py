import os
from typing import Union, Any
import requests
import logging

STREAM_FORMAT = '%(asctime)s\t%(levelname)s\t%(module)s:%(funcName)s\t%(name)s\t%(message)s'
logging.basicConfig(format=STREAM_FORMAT)
logging.getLogger().setLevel(logging.INFO)


def init():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.environ['HA_EVA_ROOT'] = root_dir
    if hassio_config() is not None:
        os.environ['HA_EVA_CONFIG'] = '/homeassistant/addons/eva_ics'


def hassio_config() -> Union[dict[str, Any], None]:
    try:
        import os, json
        supervisor_token = os.environ['SUPERVISOR_TOKEN']
        supervisor_host = 'supervisor'
        headers = {
            "Authorization": f"Bearer {supervisor_token}",
            "Content-Type": "application/json"
        }

        if supervisor_token is not None:
            f = "/homeassistant/addons/eva_ics/"
            os.makedirs(f, exist_ok=True)
        url = f"http://{supervisor_host}/services/mqtt"
        response = json.loads(requests.get(url, headers=headers).text)
        return {
            'mqtt': response['data']
        }
    except Exception as e:
        return None


init()
