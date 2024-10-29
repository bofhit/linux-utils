import argparse
import json

import docker

from ivy.wrapper import LoggerWrapper

'''
I am making the following assumptions:
* All the target containers are running.
* All the target containers are able listen for http connections.
* Naming convention for volumes- letsencrypt-<container name>
'''
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

lw = LoggerWrapper(
        CONFIG['LOGGER_NAME'],
        CONFIG['LOGGING_CONFIG'],
        CONFIG['LOG_FILE'],
    )

def is_port_open(host_port:int, container_port:int, container_ports:dict) -> int:
    host_port_str = str(host_port)
    container_port_str = str(container_port)
    for port, port_list in container_ports.items():
        if container_port_str in port:
            if host_port_str in [k['HostPort'] for k in port_list]:
                return True
    return False

def main(
        container_name:str,
        domain:str,
        host_port:int,
        container_port:int,
        letsencrypt_vol:str,
        test_cert:bool
    ) -> int:

    lw.logger.debug(f'Param container_name={container_name}')
    lw.logger.debug(f'Param host_port={host_port}')
    lw.logger.debug(f'Param container_port={container_port}')
    lw.logger.debug(f'Param letsencrypt_vol={letsencrypt_vol}')


    client = docker.from_env()

    # ========================================================================
    # PRE-RUN CHECKS

    try:
        host_port = int(host_port)
        container_port = int(container_port)
    except Exception as e:
        lw.logger.exception(e)
        return 1

    if not container_name in [c.name for c in client.containers.list()]:
        lw.logger.error(
            f'Container {container_name} not found in docker environment.'
        )
        return 1

    if not letsencrypt_vol in [c.name for c in client.volumes.list()]:
        lw.logger.error(
            f'Volume {letsencrypt_vol} not found in docker environment.'
        )
        return 1

    # Verify the expected host-container port combo exists.
    try:
        container_ports = client.containers.get(container_name).ports
        if not is_port_open(host_port, container_port, container_ports):
            lw.logger.error(f'Port {host_port}:{container_port} not open on {container_name}.')
            return 1
    except Exception as e:
        lw.logger.exception(e)

    if 'certbot' in client.containers.list():
        try:
            container = client.containers.get('certbot')
            container.remove()
        except Exception as e:
            lw.logger.exception(e)

    container = client.containers.get(container_name)

    # ========================================================================
    # SHUT DOWN PRODUCTION CONTAINER
    try:
        container.stop()
        lw.logger.info(f'Successfully stopped container {container_name}.')
    except Exception as e:
        lw.logger.exception(e)
        return 1

    # ========================================================================
    # RUN LET'S ENCRYPT CONTAINER

    certbot_command = (
        'certonly '
        '--standalone '
        f'-d {domain} '
        '--non-interactive '
        '--agree-tos '
        '-m it@blessingsofhope.com '
    )

    lw.logger.info('Initializing LetsEncrypt container.')
    try:
        client.containers.run(
            'certbot/certbot:latest',
            command=certbot_command,
            name='certbot',
            volumes=[
                f'{letsencrypt_vol}:/etc/letsencrypt/live/{domain}',
            ],
            auto_remove=True
        )
        lw.logger.info('LetsEncrypt container exited with no exceptions.')
    except Exception as e:
        lw.logger.exception(e)
        lw.logger.info(f'Restarting {container_name} after certbot failure.')
        container.start()
        lw.logger.debug(f'Successfully restarted container {container_name}.')
        return 1


    # ========================================================================
    # RESTART PRODUCTION CONTAINER
    try:
        container.start()
        lw.logger.info(f'Successfully restarted container {container_name}.')
    except Exception as e:
        lw.logger.exception(e)
        return 1

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('container_name', type=str, help='Target container name.')
    parser.add_argument('domain', type=str, help='Domain to renew.')
    parser.add_argument('host_port', type=str, help='Host HTTP port.')
    parser.add_argument('container_port', type=str, help='Container HTTP port.')
    parser.add_argument('letsencrypt_vol', type=str)
    parser.add_argument('-t', '--test-cert',
            help='Obtain a test certificate from a staginig server.',
            action='store_true'
        )

    args = parser.parse_args()

    main(
        args.container_name,
        args.domain,
        args.host_port,
        args.container_port,
        args.letsencrypt_vol,
        args.test-cert
    )
