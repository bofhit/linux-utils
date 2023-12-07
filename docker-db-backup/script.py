__doc__ = ''' Dump Docker databases to a local directory.'''

#TODO: Backup mongo db containers.

from icecream import ic
import json
import os
import subprocess

from ivy.wrapper import LoggerWrapper

SUBPROCESS_KWARGS = {
        'capture_output':True,
        'encoding':'utf-8'
        }

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

lw = LoggerWrapper(
        CONFIG['LOGGER_NAME'],
        CONFIG['LOGGING_CONFIG'],
        CONFIG['LOG_FILE'],
        )

def dump_docker_mysql(container, backup_root):
    ''' Dump a Docker MySQL Database. '''
    lw.logger.info(f'Initializing dump for container:{container}')

    args = f'docker exec {container} env'.split(' ')
    res = subprocess.run(args, **SUBPROCESS_KWARGS) 
    
    if res.returncode!= 0:
        return None

    arr = res.stdout.split()

    MYSQL_DATABASE=''
    MYSQL_ROOT_PASSWORD=''

    for item in arr:
        splt = item.split('=')
        if splt[0] == 'MYSQL_DATABASE':
            MYSQL_DATABASE = splt[1]
        elif splt[0] == 'MYSQL_ROOT_PASSWORD':
            MYSQL_PWD = splt[1]
    
    assert len(MYSQL_DATABASE) > 0
    assert len(MYSQL_PWD) > 0

    args = (
            f'docker exec -e MYSQL_DATABASE={MYSQL_DATABASE} '
            f'-e MYSQL_PWD={MYSQL_PWD} '
            f'{container} /usr/bin/mysqldump '
            f'-u root {MYSQL_DATABASE} '
            f'| gzip > {backup_root}/{container}-{MYSQL_DATABASE}-'
            '$(date +"%Y-%m-%dT%H.%M.%S").sql.gz'
            )
    res = os.system(args)

    if not res:
        lw.logger.info('Dump command completed successfully.')
    else:
        lw.logger.error(f'Dump command failed with exit code:{res}.')

def get_container(app, db):
    ''' Get the container name, given an app name and database type.

    Returns the container name as a string if exactly one container matching 
    the inputs is found, otherwise returns None.
    Args:
        app(str):: App name.
        db(str):: Valid database name.
    Returns:
        Returns a string or None
    '''

    lw.logger.debug(f'Initializng backup process for Docker app:{app}, Database:{db}.')

    app = app.lower()
    db = db.lower()
    assert db in ('mariadb,' 'mongodb','mysql')
    
    args = "docker ps --format {{.Names}}::{{.Image}}".split(' ')
    res = subprocess.run(args, **SUBPROCESS_KWARGS) 
    
    arr = res.stdout.split('\n')

    matching_containers = []

    for item in arr:
        splt = item.split('::')
        if app in splt[0] and db in splt[1]:
            matching_containers.append(splt[0])

    if len(matching_containers) == 1:
       return matching_containers[0]    
    else:
        lw.logger.error('Failed to find a container matching:'\
                        'app:{app}: database type:{db}.')
        return None

def main():
    ''' Execute backups. '''

    for backup in CONFIG['BACKUPS']:
        container = get_container(backup['APP'], backup['DATABASE'])

        if not container:
            lw.logger.info('No container found. Moving to next backup.')
            continue
        
        # Create backup.
        if backup['DATABASE'].lower() in ['mysql', 'mariadb']:
            dump_docker_mysql(container, backup['BACKUP_ROOT'])

if __name__ == '__main__':
    main()
