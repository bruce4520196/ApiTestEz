# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 14:26
# @Author  : bruce
# @desc    :
This module contains the default values for all project used by ApiTestEz.
"""
import time

# LOG
CONSOLE_LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] - %(message)s'
CONSOLE_LOG_LEVEL = 'INFO'

FILE_LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] - %(message)s'
FILE_LOG_LEVEL = 'DEBUG'
FILE_LOG_PATH = None

# REPORT
REPORT_DIR = None
REPORT_STYLE = 'br'
REPORT_FILE_NAME = f'{time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(int(time.time())))}.html'
REPORT_TITLE = 'ApiTestEz Report'
REPORT_DESC = 'This is an api-test report generated by ApiTestEz.'
BR_REPORT_THEME = 'theme_default'
