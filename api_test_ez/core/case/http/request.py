# -*- coding: utf-8 -*-
"""
# @Time    : 2022/4/26 19:33
# @Author  : bruce
# @desc    :
"""
from api_test_ez.ez import Http
from api_test_ez.ez.decorator.jsonbean import json_bean


class Request(object):

    def __init__(self, http: Http):
        self._http = http
        self._http_data = {}
        self._meta_data = {}
        self._url = None
        self._host = None
        self._path = None
        self._method = None
        self._body = None
        self._owner = None
        self._body_type = None
        self._files = None

    def _filter_data(self, request_data):
        if request_data:
            self._url = request_data.pop("url", default=None)
            self._host = request_data.pop("host", default=None)
            self._path = request_data.pop("path", default=None)
            self._body_type = request_data.pop("body_type", default="data")
            if self._url is None and self._host:
                if not self._host.startswith('http'):
                    self._host = f'http://{self._host}'
                if self._path:
                    self._url = f'{self._host}{self._path}' \
                        if self._path.startswith('/') \
                        else f'{self._host}/{self._path}'
                else:
                    self._url = self._host

            self._method = request_data.pop("method")
            self._body = request_data.pop("body", default=None)
            self._files = request_data.pop("files", default=None)
            # http
            self._http_data = {
                "headers": request_data.pop("headers"),
                "timeout": request_data.pop("timeout"),
                "cookies": request_data.pop("cookies"),
                "retry": request_data.pop("retry"),
                "proxies": request_data.pop("proxies"),
                "allow_redirects": request_data.pop("allow_redirects"),
                "verify": request_data.pop("verify"),
            }

            # meta
            self._meta_data = request_data

    def set(self, request_data):
        self._filter_data(request_data)
        for key, value in self._http_data.items():
            if value:
                if hasattr(self._http, key):
                    setattr(self._http, key, value)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def body_type(self):
        return self._body_type

    @body_type.setter
    def body_type(self, value):
        self._body_type = value

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        self._files = value

    @property
    def http(self):
        return self._http

    @property
    def meta(self):
        return RequestMetaData(self._meta_data)

    def __str__(self):
        return f'<{self.__class__.__name__}> [{self.owner}]:\n' \
               f'url: {self._url!r}\n' \
               f'method: {self._method!r}\n' \
               f'body: {self._body!r}\n' \
               f'http_data: {self._http_data!r}\n' \
               f'meta: {self.meta.data!r}'

    __repr__ = __str__


class RequestMetaData:

    def __init__(self, meta_dict):
        self._meta_dict = meta_dict

    @property
    @json_bean
    def bean(self):
        return self._meta_dict.to_dict()

    @property
    def data(self):
        return self._meta_dict.to_dict()


if __name__ == '__main__':
    http = Http()
    request = Request(http)
    request.set(
        {
            "url": 0,
            "method": 11,
            "body": 12,
            "headers": 1,
            "timeout": 2,
            "cookies": 3,
            "retry": 4,
            "proxies": 5,
            "allow_redirects": 6,
            "verify": 7,
        }
    )
