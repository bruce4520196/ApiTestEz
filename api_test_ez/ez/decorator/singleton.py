# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""


def singleton(cls):
    _instance = {}

    def inner(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return inner
