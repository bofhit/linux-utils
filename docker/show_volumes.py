import argparse

from colorama import Fore
from colorama import Style

import docker
from icecream import ic

def main(**kwargs):
    
    if 'container_filter' in kwargs:
        container_filter = kwargs['container_filter']
    else:
        container_filter = None

    client = docker.from_env()

    containers = client.containers.list()

    for container in containers:
        print('=' * 79)
        print(f"{Fore.CYAN}Container Name{Style.RESET_ALL}:{container.name}")
        print('-' * 79)
        for m in container.attrs['Mounts']:
            if 'Name' in m:
                print(f"{Fore.GREEN}Volume Name{Style.RESET_ALL}:{m['Name']}")
            else:
                print(f"{Fore.GREEN}Volume Name{Style.RESET_ALL}:Anonymous")

            for k,v in sorted(m.items()):
                if k != 'Name':
                   print(f"{Fore.GREEN}{k}{Style.RESET_ALL}:{v}")
            print('-' * 79)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--container_filter',
        help='Container name filter.'
    ) 

    args = parser.parse_args()
    
    kwargs = {}
    if args.container_filter:
        kwargs['container_filter'] = args.container_filter  

    main(
        **kwargs
    )
