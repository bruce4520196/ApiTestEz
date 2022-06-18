# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 19:31
# @Author  : bruce
# @desc    :
"""
import ast
import os
import sys

if sys.version_info[:2] >= (3, 8):
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping
from api_test_ez.ez import get_config

CONFIG_PRIORITIES = {
    'default': 0,
    'command': 10,
    'project': 20,
    'package': 30,
    'module': 40,
    'case': 50,
}


def get_config_priority(priority):
    """
    Small helper function that looks up a given string priority
    """
    return CONFIG_PRIORITIES[priority]


class BaseConfigs(MutableMapping):
    """
    Instances of this class behave like dictionaries,
    store with their ``(key, value)`` pairs.
    but values will store as a list order by ``priority``.
    when you want ``get`` value, it will return the value of the highest priority (maybe now is enough).
    """
    def __init__(self, *args, **kwargs):

        self.attributes = {}
        self.update(*args, **kwargs)

    def __delitem__(self, name) -> None:
        del self.attributes[name]

    def __getitem__(self, name):
        if name not in self:
            return None
        return self.attributes[name].value

    def __len__(self) -> int:
        return len(self.attributes)

    def __iter__(self):
        return iter(self.attributes)

    def __setitem__(self, name, value):
        self.set(name, value)

    def __contains__(self, name):
        return name in self.attributes

    def set_config(self, config_path, priority='default'):
        """
        Store project from a module.

        :param config_path: the config file path
        :type config_path: string

        :param priority: the priority of the configs.
        :type priority: string
        """
        cfg = get_config(config_path)
        for title, selection in cfg.items():
            for key, value in selection.items():
                try:
                    value = ast.literal_eval(value)
                except SyntaxError:
                    pass
                self.set(key.lower(), value, priority=priority)

    def set(self, name, value, priority='default'):
        """
        Store a key/value attribute with a given priority.

        :param name: the setting name
        :type name: string

        :param value: the value to associate with the setting
        :type value: any

        :param priority: the priority of the setting. Should be a key of
            CONFIG_PRIORITIES or an integer
        :type priority: string or int
        """
        priority = get_config_priority(priority)
        if name not in self:
            if isinstance(value, ConfigAttribute):
                self.attributes[name] = value
            else:
                self.attributes[name] = ConfigAttribute(value, priority)
        else:
            self.attributes[name].set(value, priority)

    def get(self, name, default=None):
        """
        Get a config value without affecting its original type.

        :param name: the setting name
        :type name: string

        :param default: the value to return if no setting is found
        :type default: any
        """
        return self[name] if self[name] is not None else default

    def pop(self, name, default=None):
        """
        Pop a config value from `name` and delete key in config.
        :param name:
        :param default:
        :return:
        """
        value = self[name] if self[name] is not None else default
        if self.attributes.get(name):
            del self.attributes[name]
        return value

    def to_dict(self):
        """
        Change `Config` to `dict`.
        :return:
        """
        return {k: v for k, v in self.items()}


class ConfigAttribute(object):
    """
    Class for storing data related to configs attributes.

    This class is intended for internal usage, you should try Configs class
    for setting configurations, not this one.
    """
    def __init__(self, value, priority):
        self.value = value
        self.priority = priority

    def set(self, value, priority):
        """Sets value if priority is higher or equal than current priority."""
        if priority >= self.priority:
            self.value = value
            self.priority = priority

    def __str__(self):
        return "<ConfigAttribute value={self.value!r} " \
               "priority={self.priority}>".format(self=self)

    __repr__ = __str__


class Configs(BaseConfigs):
    """
    This object stores ApiTestEz project for the configuration of internal
    components, and can be used for any further customization.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_config(os.path.join(os.path.dirname(__file__), "default_configs.cfg"))
