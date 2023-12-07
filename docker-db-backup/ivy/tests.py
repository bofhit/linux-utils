import unittest

from wrapper import LoggerWrapper

class TestLoggerWrapper(unittest.TestCase):

    def setUp(self):
        self.lw = LoggerWrapper(
                    'test_logger',
                    'config.json',
                    'C:/io/io.log'
                )

    def test_invalid_logging_level(self):
        with self.assertRaises(AttributeError):
            self.lw.logger.invalid('This a is debug message.')

    def test_debug_message(self):
        self.lw.logger.debug('This is a debug message.')

    def test_info_message(self):
        self.lw.logger.info('This is an info message.')

    def test_warning_message(self):
        self.lw.logger.warning('This is a warning message.')

    def test_error_message(self):
        self.lw.logger.error('This is an error message.')

    def test_critical_message(self):
        self.lw.logger.critical('This is a critical message.')

    def test_exception_message(self):
        try:
            7 / 0
        except ZeroDivisionError:
            self.lw.logger.exception('This is an exception message.')

