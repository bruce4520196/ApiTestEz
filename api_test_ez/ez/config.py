# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 17:00
# @Author  : bruce
# @desc    :
"""
from configparser import ConfigParser


def get_config(file_path):
    """Get Ez config file as a ConfigParser"""
    cfg = ConfigParser()
    cfg.read(file_path, encoding='utf-8')
    return cfg
