import logging

import json, os

try:
    for dirpath, dirnames, filenames in os.walk(config_dir):
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            with open(full_path, 'r') as f:
                data = json.load(f)
                for d in data:
                    rpc_call('pubsub.publish',
                             topic=d['topic'], payload=d['payload'], packer='json', _target=d['broker'])
except Exception as e:
    logging.exception(e)
