import argparse
import json

import docker

from ivy.wrapper import LoggerWrapper

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

lw = LoggerWrapper(
        CONFIG['LOGGER_NAME'],
        CONFIG['LOGGING_CONFIG'],
        CONFIG['LOG_FILE'],
    )

def main(
        container_name:str,
        http_port:int,
        https_port:int,
        lets_encrypt_volume:str
    ) -> int:

    client = docker.from_env()

    # ========================================================================
    # PRE-RUN CHECKS
    if not container_name in [c.name for c in client.containers.list()]:
        lw.logger.error(
            f'Container {container_name} not found in docker environment.'
        )
        return 1

    if not lets_encrypt_volume in [c.name for c in client.volumes.list()]:
        lw.logger.error(
            f'Volume {lets_encrypt_volume} not found in docker environment.'
        )
        return 1

    # ========================================================================
    # SHUT DOWN PRODUCTION CONTAINER


    # ========================================================================
    # RUN LET'S ENCRYPT CONTAINER

    # ========================================================================
    # RESTART PRODUCTION CONTAINER

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('container_name', type=str, help='Target container name.')
    parser.add_argument('http_port', type=str, help='HTTP port.')
    parser.add_argument('https_port', type=str, help='HTTPS port.')
    parser.add_argument('lets_encrypt_volume', type=str)

    args = parser.parse_args()

    main(
        args.container_name,
        args.http_port,
        args.https_port,
        args.lets_encrypt_volume
    )
