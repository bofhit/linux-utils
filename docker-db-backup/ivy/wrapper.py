__doc__ = """Wrapper for Python logger.
    Will pull values from a configuration file.
    Main logger has separate handers for console and file logging, logging levels 
    for them can be defined separately.
    Caller will need to provide a config file path and a destination path 
    for the file output."""

import json
import logging
import logging.config

import graypy

LOG_LEVELS = ('debug', 'info', 'warning', 'error', 'critical')

class LoggerWrapper():
    def __init__(self, name, config, log_file, file_log_level='info', console_log_level='debug'):
        """
        Attrs:
            name(str):: Logger name, will appear in log files.
            config(str):: Filepath for logger config.
            log_file(str):: Filepath where the logger file handler will write files.
            file_log_level(str):: Logging level for file output.
            console_log_level(str):: Logging level for console output.
        """
        assert file_log_level.lower() in LOG_LEVELS, f'{file_log_level} is not a valid logging level.'
        assert console_log_level.lower() in LOG_LEVELS, f'{file_log_level} is not a valid logging level.'

        file_log_level = self.recast_log_level(file_log_level)
        console_log_level= self.recast_log_level(console_log_level)

        with open(config) as f:
            json_obj = json.load(f)

        # Modify the filename for the file handler before creating the Logger instance.
        json_obj['handlers']['file_handler']['filename'] = log_file

        logging.config.dictConfig(json_obj)

        self.logger = logging.getLogger('main')
        self.logger.name = self.format_name(name)
        self.logger.level = logging.DEBUG       # Level for logger object.
        self.logger.handlers[1].filename = log_file

    def recast_log_level(self, string):
        """
        Convert a string to a logging module flag.
        """
        if string.lower() == 'debug':
            return logging.DEBUG
        elif string.lower() == 'info':
            return logging.INFO
        elif string.lower() == 'warning':
            return logging.WARNING
        elif string.lower() == 'error':
            return logging.ERROR
        elif string.lower() == 'critical':
            return logging.CRITICAL

    def format_name(self, name):
        """
        Pad name with spaces, for log readability.
        """
        return name.ljust(20)

if __name__ == '__main__':
    import sys

    lw = LoggerWrapper('myLogger',
                        'logging_config.json',
                        'C:/io/io3.log'
                        )


