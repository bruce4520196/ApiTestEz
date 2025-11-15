# -*- coding: utf-8 -*-
"""
# @Time    : 2025/3/4 15:41
# @Author  : wangfei
# @desc    :
"""


class PytestHttpFrame(object):

    def __deepcopy__(self, memo):
        return self

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def initRequest(self, testmethod_name):
        pass

    def beforeRequest(self):
        pass

    def doRequest(self, request=None):
        pass
    def afterRequest(self):
        pass
