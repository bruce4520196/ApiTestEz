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
    cfg.read(file_path)
    return cfg


if __name__ == '__main__':
    import os
    print(os.path.basename(r'E:\PyCharmWorker\ApiTestEz\api_test_ez\project\configs\default_configs.cfg'))
    print(type(get_config(r'E:\PyCharmWorker\ApiTestEz\api_test_ez\project\configs\default_configs.cfg')))
    for k, v in get_config(r'E:\PyCharmWorker\ApiTestEz\api_test_ez\project\configs\default_configs.cfg').items():
        print(k, list(v.values()))

        if k == 'HTTP':
            print(dir(v))
            print(v)
            print(v.get('headers'))
            print(v.get('auto_request'))
            print(list(v.values()))
