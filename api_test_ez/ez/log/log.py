# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/3 15:43
# @Author  : bruce
# @desc    :
"""

import os
import logging
from enum import Enum

from api_test_ez.ez.decorator import singleton

Log_Format = '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] - %(message)s'


class LogLevel(Enum):
    CRITICAL = 'CRITICAL'
    FATAL = 'FATAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


_logLevelName = ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']


class Log:
    def __init__(self, logger_name=None):
        self.default_log_level = "DEBUG"
        self.logger = logging.getLogger(logger_name)
        # default console format
        self._console_format = Log_Format
        # default file format
        self._file_format = Log_Format
        # set log level
        self._file_log_level = LogLevel.DEBUG.value
        self._console_log_level = LogLevel.INFO.value

    def init_logger(self, file_log_path=None):
        if file_log_path:
            # make dir
            dir_path = os.path.dirname(file_log_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            # file handler
            file_handler = self.build_file_handler(file_log_path)
            self.logger.addHandler(file_handler)

        # console handler
        console_handler = self.build_console_handler()
        self.logger.addHandler(console_handler)

        self.logger.setLevel(self.default_log_level)
        return self.logger

    @property
    def console_format(self):
        """
        log format
        :return:
        """
        return self._console_format

    @console_format.setter
    def console_format(self, log_format: str):
        """
        :param log_format:
        :return:
        """
        self._console_format = log_format

    @property
    def file_format(self):
        """
        log format
        :return:
        """
        return self._file_format

    @file_format.setter
    def file_format(self, log_format: str):
        """
        :param log_format:
        :return:
        """
        self._file_format = log_format

    @property
    def file_log_level(self):
        """
        :return:
        """
        return self._file_log_level

    @file_log_level.setter
    def file_log_level(self, level: str):
        """
        :param level: file log level in ['CRITICAL' | 'FATAL' | 'ERROR' | 'WARN' | 'WARNING' | 'INFO' | 'DEBUG']
        :return:
        """
        level = level.upper()
        if level in _logLevelName:
            self._file_log_level = level
        else:
            self.logger.error("Set log level error: unknown level name. Level name must in: "
                              "['CRITICAL' | 'FATAL' | 'ERROR' | 'WARN' | 'WARNING' | 'INFO' | 'DEBUG']")

    @property
    def console_log_level(self):
        """
        :return:
        """
        return self._console_log_level

    @console_log_level.setter
    def console_log_level(self, level: str):
        """
        :param level: file log level in ['CRITICAL' | 'FATAL' | 'ERROR' | 'WARN' | 'WARNING' | 'INFO' | 'DEBUG']
        :return:
        """
        level = level.upper()
        if level in _logLevelName:
            self._console_log_level = level
        else:
            self.logger.error("Set log level error: unknown level name. Level name must in: "
                              "['CRITICAL' | 'FATAL' | 'ERROR' | 'WARN' | 'WARNING' | 'INFO' | 'DEBUG']")

    def build_file_handler(self, file_log_path):
        """
        build file handler
        :param file_log_path:
        :return:
        """
        formatter = logging.Formatter(self._file_format)
        file_handler = logging.FileHandler(file_log_path, encoding='utf-8')
        file_handler.setLevel(self.file_log_level)          # set level
        file_handler.setFormatter(formatter)                # set format
        return file_handler

    def build_console_handler(self):
        """
        build console handler
        :return:
        """
        formatter = logging.Formatter(self._console_format)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.console_log_level)       # set level
        console_handler.setFormatter(formatter)                # set format
        return console_handler


if __name__ == '__main__':
    log = Log()
    log1 = Log()
    print(id(log))
    print(id(log1))
    # log.console_log_level = 'error'
    # log.file_log_level = 'info'
    # logger = log.init_logger(r'D:\PyWorker\ApiTestEz\tests\case\node\report\result')
    # # logger.setLevel('DEBUG')
    # logger.info('1111eeee')
