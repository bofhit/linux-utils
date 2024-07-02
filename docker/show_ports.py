import docker 
from icecream import ic

client = docker.from_env()

containers = client.containers.list()

ports = {}

for c in containers:
    ports[c.name] = c.ports

ic(ports)

