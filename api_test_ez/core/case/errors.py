# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""


class HttpRequestException(Exception):
    def __init__(self, err):
        Exception.__init__(self, err)


class CaseFileNotFoundException(Exception):
    def __init__(self, err):
        Exception.__init__(self, err)
