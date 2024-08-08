import argparse

import docker 
from icecream import ic
import pandas as pd

def main(**kwargs):

    if 'sort_container_port' in kwargs:
        sort_container_port = True
    else:
        sort_container_port = False

    if 'sort_host_port' in kwargs:
        sort_host_port = True
    else:
        sort_host_port = False

    client = docker.from_env()

    containers = client.containers.list()

    ports = []

    for c in containers:
        for p in c.ports:
            tmp = {}  
            tmp['Container'] = c.name
            tmp['Container Port'] = p
            if ic(c.ports[p]):
                for host_item in ic(c.ports[p]):
                    tmp['Host Port'] = host_item['HostPort']
                    tmp['Host IP'] = host_item['HostIp']
                ports.append(tmp)
            else:
                tmp['Host Port'] = ''
                tmp['Host IP'] = ''
                ports.append(tmp)

    df = pd.DataFrame(ports)

    if sort_container_port:
        df = df.sort_values('Container Port')

    if sort_host_port:
        df = df.sort_values('Host Port')

    return df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
   
    parser.add_argument('--sort_container_port', action='store_true')
    parser.add_argument('--sort_host_port', action='store_true')


    args = parser.parse_args()

    kwargs = {}
    if args.sort_container_port:
        kwargs['sort_container_port'] = args.sort_container_port

    if args.sort_host_port:
        kwargs['sort_host_port'] = args.sort_host_port

    res = main(
       **kwargs 
    )  

    print(res)  
    
