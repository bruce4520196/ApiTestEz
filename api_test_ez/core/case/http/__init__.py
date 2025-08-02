# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/4 20:28
# @Author  : bruce
# @desc    :
"""
try:
    from api_test_ez.core.case.frame.frame_pytest import BaseCase
except ImportError:
    # 如果pytest相关模块不可用，创建一个占位符
    BaseCase = None


class Case(BaseCase):
    pass
