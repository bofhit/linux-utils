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

def is_port_open(host_port:int, container_port:int, container_ports:dict) -> int:
    host_port_str= str(host_port)
    container_port_str = str(container_port)
    for port, port_list in container_ports.items():
        if container_port_str in port:
            if host_port_str in [k['HostPort'] for k in port_list]:
                return True
    return False

def main(
        container_name:str,
        host_http:int,
        container_http:int,
        lets_encrypt_volume:str
    ) -> int:

    lw.logger.debug(f'Param container_name={container_name}')
    lw.logger.debug(f'Param host_http={host_http}')
    lw.logger.debug(f'Param container_http={container_http}')
    lw.logger.debug(f'Param lets_encrypt_volume={lets_encrypt_volume}')


    client = docker.from_env()

    # ========================================================================
    # PRE-RUN CHECKS

    try:
        host_http = int(host_http)
        container_http = int(container_http)
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
        if not is_port_open(host_http, container_http, container_ports):
            lw.logger.error(f'Port {host_http}:{container_http} not open on {container_name}.')
            return 1
    except Exception as e:
        lw.logger.exception(e)

    container = client.containers.get(container_name)

    # ========================================================================
    # SHUT DOWN PRODUCTION CONTAINER
    try:
        container.stop()
        lw.logger.debug(f'Successfully stopped container {container_name}.')
    except Exception as e:
        lw.logger.exception(e)

    # ========================================================================
    # RUN LET'S ENCRYPT CONTAINER

    # ========================================================================
    # RESTART PRODUCTION CONTAINER
    try:
        container.start()
        lw.logger.debug(f'Successfully restarted container {container_name}.')
    except Exception as e:
        lw.logger.exception(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('container_name', type=str, help='Target container name.')
    parser.add_argument('host_http', type=str, help='Host HTTP port.')
    parser.add_argument('container_http', type=str, help='Container HTTP port.')
    parser.add_argument('lets_encrypt_volume', type=str)

    args = parser.parse_args()

    main(
        args.container_name,
        args.host_http,
        args.container_http,
        args.lets_encrypt_volume
    )
