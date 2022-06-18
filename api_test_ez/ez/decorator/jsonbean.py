# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/3 15:43
# @Author  : bruce
# @desc    :
"""


class JsonBean(type):
    """
    # JsonBean类，具有以下特性：
    # 1、将json实例化为对象调用（OOP）
    # 2、为对象属性提供只读功能
    """
    def __new__(mcs, *args, **kwargs):
        if len(args) > 0:
            json = args[0]
            if not isinstance(json, dict):
                raise Exception('Json required!')
            else:
                for k, v in json.items():
                    if isinstance(v, dict):
                        json.update({k: JsonBean(v)})

                    elif isinstance(v, list):
                        new_v = []
                        for _v in v:
                            if isinstance(_v, dict):
                                new_v.append(JsonBean(_v))
                            else:
                                new_v.append(_v)
                        json.update({k: new_v})

                    else:
                        json.update({k: v})

                return super(JsonBean, mcs).__new__(mcs, mcs.__name__, (JsonBean,), json)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return None

    def __getattribute__(self, item):

        return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        raise Exception("It is read only!")


def json_bean(func):
    """
    JsonBean装饰器，将json数据转化为JsonBean对象
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        json = func(*args, **kwargs)
        return JsonBean(json)
    return wrapper
