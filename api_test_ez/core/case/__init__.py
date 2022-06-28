# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/4 15:13
# @Author  : bruce
# @desc    :
"""
import copy
import json
import os

import tablib
import ast
from ddt import ddt, data, feed_data

from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame
from api_test_ez.core.case.http.request import Request
from api_test_ez.core.case.http.response import EzResponse

from api_test_ez.ez import Http
from api_test_ez.project import Project


def load_test_data(data_filename):
    if isinstance(data_filename, str):
        with open(data_filename, 'rb') as f:
            data_set = tablib.Dataset().load(f.read())
            return data_set.dict
    else:
        return []


def ez_ddt_setter(cls):
    """Set `%values` (`DATA_ATTR` from ddt) for testMethods.

    `ddt` will copy methods which have `DATA_ATTR` attribute.
    So we set it to all the testMethods (sometimes we need set some method exactly,
    it will be supported maybe next version).
    Then Unittest can run all of these cases."""
    DATA_ATTR = "%values"
    if hasattr(cls, "load_data"):
        load_func = getattr(cls, "load_data")
        values = getattr(load_func, DATA_ATTR)
        for name, func in list(cls.__dict__.items()):
            if name.startswith("test"):
                setattr(func, DATA_ATTR, values)
    return cls


DATA_HOLDER = "%data_holder"


class CaseMetaclass(type):
    """Mapping test method and ddt data.
    `ddt` only copy the method which is decorated by `data`,
    let's make test_method and ddt_data map."""
    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        # If a base class just call super new
        if name == 'UnitCase':
            return super_new(mcs, name, bases, attrs)

        for base_class in bases:

            if base_class is UnitCase:
                # Find data functions
                ddt_func_names = []
                for base_attr_name in dir(base_class):
                    if base_attr_name.startswith('load_data'):
                        ddt_func_names.append(base_attr_name)

                # If data function is None, let test run itself.
                if len(ddt_func_names) == 0:
                    return super_new(mcs, name, bases, attrs)

                new_attrs = {}
                # Mapping test methods and data functions
                for name, func in attrs.items():
                    if name.startswith('test'):
                        for ddt_func_name in ddt_func_names:
                            test_name = ddt_func_name.replace('load_data', name)
                            # Let's set a `%data_owner` attr to test function
                            # Then we can find the data later.

                            # We can not copy function directly, create it from `ddt.feed_data`.
                            _func = feed_data(func, test_name, func.__doc__)
                            setattr(_func, DATA_HOLDER, ddt_func_name)
                            new_attrs.update({test_name: _func})
                    else:
                        # other methods should be added without modified
                        new_attrs.update({name: func})

                return super_new(mcs, name, bases, new_attrs)

        return super_new(mcs, name, bases, attrs)


@ddt
class UnitCase(UnitHttpFrame, metaclass=CaseMetaclass):
    # env init
    case_path_dir = os.getcwd()
    ez_project = Project(ez_file_path=case_path_dir, env_name=os.path.basename(case_path_dir))
    configs = ez_project.configs
    logger = ez_project.logger
    # load test data
    __casefile__ = configs.get("case_filepath")
    data_set = load_test_data(__casefile__)
    # set request here, bcz the data in `ez.config` can not be load in again.

    __autoRequest__ = configs.get("auto_request")

    def __new__(cls, methodName, *args, **kwargs):
        # bcz of `__classcell__` error, copy config at here.
        cls.local_config = copy.deepcopy(cls.configs)
        return super(UnitHttpFrame, cls).__new__(cls, *args, **kwargs)

    def __init__(self, methodName):
        self.request = Request(http=Http())
        self.response = EzResponse(logger=self.logger)
        self.request.owner = methodName
        self.response.owner = methodName
        self.initRequest(methodName)
        super(UnitCase, self).__init__(methodName)

    @data(*data_set)
    def load_data(self, case_data: dict):
        for key, value in case_data.items():
            self.local_config.set(key, value, priority="case")

    def initRequest(self, testmethod_name):
        # Find my ddt data holder via testmethod_name.
        if hasattr(self, testmethod_name):
            test_func = getattr(self, testmethod_name)
            if hasattr(test_func, DATA_HOLDER):
                data_holder = getattr(test_func, DATA_HOLDER)
                if hasattr(self, data_holder):
                    _ddt_data_func = getattr(self, data_holder)
                    _ddt_data_func()
        self.request.set(self.local_config)
        self.logger.debug(repr(self.request))
        return self.request

    def doRequest(self, request=None):
        if request:
            self.request.set(request)
        # Prepare request
        body_type = "data"
        http = self.request.http
        url = self.request.url
        method = self.request.method.lower()

        body = self.request.body
        if body:
            try:
                body = json.loads(body)
                body_type = "json"
            except json.JSONDecodeError:
                pass

        # Request start
        if url and hasattr(http, method):
            do = getattr(http, method)
            self.response.set(do(url=url, **{body_type: body}))
            self.logger.debug(repr(self.response))
