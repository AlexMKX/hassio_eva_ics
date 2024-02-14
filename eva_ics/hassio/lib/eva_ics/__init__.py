import os
from typing import Union, Any
import requests
import logging

STREAM_FORMAT = '%(asctime)s\t%(levelname)s\t%(module)s:%(funcName)s\t%(name)s\t%(message)s'
logging.basicConfig(format=STREAM_FORMAT)


def init():
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.environ['PYEVA_ROOT'] = ROOT_DIR
    os.environ['PYEVA_CONFIG'] = os.path.join(ROOT_DIR, 'config')


def hassio_config() -> Union[dict[str, Any], None]:
    try:
        import os, json
        supervisor_token = os.environ['SUPERVISOR_TOKEN']
        # supervisor_token = '18c81ccf0c0afa64aa17e7f6bb77fde4ed0762f5a309206a9823ba64f461ce755a492d1cc27de96619191db4c15a72f00a4f5b091db42799'
        supervisor_host = 'supervisor'
        # supervisor_host = '172.30.32.2'
        headers = {
            "Authorization": f"Bearer {supervisor_token}",
            "Content-Type": "application/json"
        }

        url = f"http://{supervisor_host}/services/mqtt"
        response = json.loads(requests.get(url, headers=headers).text)
        return {
            'mqtt': response['data']
        }
    except Exception as e:
        return None


init()
