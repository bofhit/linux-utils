__doc__ = ''' Manage backups by backup date. 
            
            Date determined by timestamp in filename, not by file meta-data.
            Timestamp format 'YYYY-mm-DDTHH.MM.SS'.

            Times given in days.
            1. Keep all backups within a given time.
            2. Keep one backup per day within a given time.
            3. Keep one backup per week within a given time.
            
            '''

import json
from pathlib import Path
import re

from icecream import ic

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


def main():
    # ========================================================================
    # Get all files within root directory.
    files = list(backup_path_root.rglob('*'))

    files.sort(key=lambda x: re.search(TIMESTAMP_PAT, x.name).group())

    lw.logger.debug(f'Found {len(files)} files:')
    for file in files:
        lw.logger.debug(ic(file.name))

    # ========================================================================
    # Filter files with a valid timestamp.
    files_with_valid_timestamps = []
    for file in files:
        if re.search(TIMESTAMP_PAT, file.name):
            files_with_valid_timestamps.append(file)
        else:
            lw.logger.debug(f'No valid timestamp in {file.name}.')

# ============================================================================
# Remove files in the keep daily range.

# ============================================================================
# Remove files in the keep weekly range.

if __name__ == '__main__':
    main()

