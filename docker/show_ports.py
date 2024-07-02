import docker 
from icecream import ic

client = docker.from_env()

containers = client.containers.list()

ports = [c.ports for c in containers]

ic(ports)

