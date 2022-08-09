# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""


class HttpRequestException(Exception):
    pass


class UrlNoneException(HttpRequestException):
    def __init__(self, err="`url` can not be None."):
        Exception.__init__(self, err)
