__doc__ = ''' Manage backups by backup date. 
            
            Date determined by timestamp in filename, not by file meta-data.
            Timestamp format 'YYYY-mm-DDTHH.MM.SS'.

            Times given in days.
            1. Keep all backups up to a given time.
            2. Keep daily backups up to a given time.
            3. Keep weekly backups up to a given time.
            4. Delete all backups older than the weekly backup range.
            
            '''

import json
from pathlib import Path
import os
import re

from icecream import ic
import pendulum

from ivy.wrapper import LoggerWrapper

TIMESTAMP_PAT = re.compile('\d{4}-\d{2}-\d{2}T\d{2}.\d{2}.\d{2}')

# ============================================================================
# Import and validate parameters.
with open('config.json', 'rb') as f:
    CONFIG = json.load(f)

lw = LoggerWrapper(
                    CONFIG['LOGGER_NAME'],
                    CONFIG['LOGGER_CONFIG'],
                    CONFIG['LOG_FILE']
                )

lw.logger.debug('Logger initialized.')

BACKUP_ROOT = CONFIG['BACKUP_ROOT']
KEEP_ALL = CONFIG['KEEP_ALL']
KEEP_DAILY = CONFIG['KEEP_DAILY']
KEEP_WEEKLY = CONFIG['KEEP_WEEKLY']

backup_path_root = Path(BACKUP_ROOT)

try:
    if not backup_path_root.exists():
        lw.logger.error('Backup root folder does not exist. Script will exit')
        exit()

    assert 0 < KEEP_ALL < 7, 'Keep all parameter not in valid range.'
    assert 0 < KEEP_DAILY < 32, 'Keep daily parameter not in valid range.'
    assert 0 < KEEP_WEEKLY < 366, 'Keep weekly parameter not in valid range.'

    assert KEEP_ALL < KEEP_DAILY < KEEP_WEEKLY, \
            'Keep all must less than keep daily value, '\
            'and keep daily must be less than keep weekly value.'
except AssertionError as e:
    lw.logger.error(f'Parameter validation failed:{e} Script will terminate.')
    exit()

def walk_root_dir(root):
    '''
    Walk the root directory, and return subfolders containing files.
    '''

    root_walk = []

    for root, dirs, files in os.walk(root):
        # Ignore dirs that don't contain files.
        if files:
            root_walk.append({
                            'root':root,
                            'dirs': dirs,
                            'files': files
                        })

    return root_walk

def expand_file_objects(timestamp_pattern, files):
    ''' Create a dict for each file. 
        Add attributes useful for sorting and managing the files.

        Attributes for each file:
        timestamp- Extract from file name.
        delta_days- Current time - timestamp.
        delete- Flag controlling deletion.

    '''
    assert isinstance(timestamp_pattern, re.Pattern) 

    current_time = pendulum.now()

    lod = []

    for file in files:
        ts = re.search(TIMESTAMP_PAT, file)
        if ts:
            delta = current_time - pendulum.parse(ts.group().replace('.', ':'))

            lod.append(
                    {'timestamp': ts.group(),
                        'name': file,
                        'days_ago': int(delta.total_days() // 1),
                        'delete': 0
                    }
                )
        else:
            lw.logger.debug(f'No valid timestamp in {file}.')

    lod.sort(
            key=lambda x: x['timestamp'],
            reverse=True
            )

    return lod 

def mark_daily(files, keep_all, keep_daily):
    ''' Mark files in the daily backup range for deletion.
    '''
    found_daily_backup = 0
    for file in files:
        if file['days_ago'] > keep_all:
            if file['days_ago'] > keep_daily:
                break
            else:
                # We already found a backup for this day.
                if file['days_ago'] == found_daily_backup:
                    file['delete'] = 1
                else:
                    found_daily_backup = file['days_ago']

    return files

def mark_weekly(files, keep_daily, keep_weekly):
    ''' Mark files in the weekly backup range for deletion.
    '''
    
    weekly_backup_table = []
    for i in range(keep_daily, keep_weekly, 7):
        weekly_backup_table.append({
                    'start': i,
                    'end': i + 6,
                    'found_backup_this_week': 0
                    })

    ic(weekly_backup_table)

    for file in files:
        if file['days_ago'] < keep_daily:
            continue
        
        if file['days_ago'] > keep_weekly:
            break

        for week in weekly_backup_table:
            ic(week['start'])
            if week['start'] <= file['days_ago'] <= week['end']:
                # We already found a file for this week.
                if week['found_backup_this_week']:
                    file['delete'] = 1
                else:
                    week['found_backup_this_week'] = 1

    return files

def mark_older_than_weekly(files, keep_weekly):
    ''' Mark files older than the weekly backup limit.
    '''
    for file in files:
        if file['days_ago'] > keep_weekly:
            file['delete'] = 1

    return files

def main():
    # ========================================================================
    # Get folders containing backup files.
    dirs_containing_backups = walk_root_dir(BACKUP_ROOT) 
   
    for backup_dir in dirs_containing_backups:
        backup_dir['files'] = expand_file_objects(
                                TIMESTAMP_PAT,
                                backup_dir['files']
                            )

    for backup_dir in dirs_containing_backups:
        lw.logger.debug(f"Found {len(backup_dir['files'])} "
                        f"files in {backup_dir['root']}."
                    )

    # ========================================================================
    # Mark files in the keep daily range for removal. 
    for backup_dir in dirs_containing_backups:
        backup_dir['files'] = mark_daily(
                                backup_dir['files'],
                                KEEP_ALL,
                                KEEP_DAILY
                            )

    # ========================================================================
    # Mark files for removal in the keep weekly range.
    for backup_dir in dirs_containing_backups:
        backup_dir['files'] = mark_weekly(
                                backup_dir['files'],
                                KEEP_DAILY,
                                KEEP_WEEKLY
                            )
    
    # ========================================================================
    # Mark files for removal older than the keep weekly range.
    for backup_dir in dirs_containing_backups:
        backup_dir['files'] = mark_older_than_weekly(
                                backup_dir['files'],
                                KEEP_WEEKLY
                            )

    ic(dirs_containing_backups)

    # ========================================================================
    # Delete files.
    for backup_dir in dirs_containing_backups:
        for file in backup_dir['files']:
            file_path = backup_dir['root'] + '/' + file['name']
            if file['delete']:
                try:
                    os.system(f'rm {file_path}')
                    lw.logger.info(f'Removed file:{file_path}')
                except FileNotFoundError:
                    lw.logger.error(f'File not found:{file_path}')
                except PermissionError:
                    lw.logger.error(f'Permissions error:{file_path}')
    

if __name__ == '__main__':
    main()

