# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 17:58
# @Author  : bruce
# @desc    :
"""
from importlib import import_module

from api_test_ez.ez.decorator import singleton
from api_test_ez.project.settings import default_settings


class BaseSettings(dict):
    """
    Instances of this class behave like dictionaries,
    store with their ``(key, value)`` pairs.
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def set_module(self, module):
        """
        Store project from a module.

        :param module: the module or the path of the module
        :type module: module object or string
        """
        if isinstance(module, str):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def set(self, name, value):
        """
        Store a key/value attribute with a given priority.

        :param name: the setting name
        :type name: string

        :param value: the value to associate with the setting
        :type value: any
        """
        self.__setitem__(name, value)


@singleton
class Settings(BaseSettings):
    """
    This object stores ApiTestEz project for the configuration of internal
    components, and can be used for any further customization.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_module(default_settings)


def iter_default_settings():
    """Return the default project as an iterator of (name, value) tuples"""
    for name in dir(default_settings):
        if name.isupper():
            yield name, getattr(default_settings, name)


def overridden_settings(settings):
    """Return a dict of the project that have been overridden"""
    for name, def_value in iter_default_settings():
        value = settings[name]
        if not isinstance(def_value, dict) and value != def_value:
            yield name, value
