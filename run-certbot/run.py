__doc__ = ''' Run certbot script for multiple containers. '''

import json

from icecream import ic

from ivy.wrapper import LoggerWrapper   
from script import main


with open('containers.json', 'r') as f:
    CONTAINERS = json.load(f)

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

TEST_CERT = CONFIG['TEST_CERT']

lw = LoggerWrapper(
        CONFIG['LOGGER_NAME'],
        CONFIG['LOGGING_CONFIG'],
        CONFIG['LOG_FILE'],
    )

for container in CONTAINERS:
    try:
        main(
                container['CONTAINER_NAME'],
                container['DOMAIN'],
                container['HOST_PORT'],
                container['CONTAINER_PORT'],
                container['LETSENCRYPT_VOL'],
                TEST_CERT
                )
    except Exception as e:
        lw.logger.exception(e)

ic(CONTAINERS)
