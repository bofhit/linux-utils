import argparse
import json

import docker

from ivy.wrapper import LoggerWrapper
'''
I am making the following assumptions:
* All the target containers are in a running state.
* All the target containers are able listen for http and https connections.
'''
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

lw = LoggerWrapper(
        CONFIG['LOGGER_NAME'],
        CONFIG['LOGGING_CONFIG'],
        CONFIG['LOG_FILE'],
    )

def is_port_open(port:int, container_ports:dict) -> int:
    port_str = str(port)
    for port_list in container_ports.values():
        host_ports = [k['HostPort'] for k in port_list]
        if port_str in host_ports:
            return True
    return False

def main(
        container_name:str,
        http_port:int,
        https_port:int,
        lets_encrypt_volume:str
    ) -> int:

    lw.logger.debug(f'Param container_name={container_name}')
    lw.logger.debug(f'Param http_port={http_port}')
    lw.logger.debug(f'Param https_port={https_port}')
    lw.logger.debug(f'Param lets_encrypt_volume={lets_encrypt_volume}')


    client = docker.from_env()

    # ========================================================================
    # PRE-RUN CHECKS

    try:
        http_port = int(http_port)
        https_port = int(https_port)
    except Exception as e:
        lw.logger.exception(e)
        return 1

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

    try:
        container_ports = client.containers.get(container_name).ports
        if not is_port_open(http_port, container_ports):
            lw.logger.error(f'Port {http_port} not open on {container_name}.')
            return 1
        if not is_port_open(https_port, container_ports):
            lw.logger.error(f'Port {https_port} not open on {container_name}.')
            return 1
    except Exception as e:
        lw.logger.exception(e)


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
