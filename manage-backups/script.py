__doc__ = ''' Manage backups by backup date. 
            
            Date determined by timestamp in filename, not by file meta-data.
            1. Keep all backups within a given time.
            2. Keep one backup per day within a given time.
            3. Keep one backup per week within a given time.
            
            '''

# Import and validate parameters.

# Get all files within root directory.

# Note any files that don't have a valid timestamp.

# Remove files in the keep daily range.

# Remove files in the keep weekly range.
