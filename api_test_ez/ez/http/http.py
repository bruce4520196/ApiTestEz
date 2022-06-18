# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/3 15:24
# @Author  : bruce
# @desc    :
"""
from enum import Enum

import requests
import urllib3
urllib3.disable_warnings()


class Method:
    GET = 'GET'
    POST = 'POST'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    DELETE = 'DELETE'
    PUT = 'PUT'
    PATCH = 'PATCH'


class Http:

    def __init__(self, headers=None, timeout=3, allow_redirects=False, verify=False, proxies=None, retry=1):
        """
        Http初始化
        :param headers: 请求头。
        :param timeout: 超时时间。
        :param with_session: 是否创建session，默认创建。
        :param allow_redirects: 是否允许重定向，默认否。
        :param verify: 是否进行https证书验证，默认否。
                       如果开启：verify='/<path>/<file_name>.pem'。
        :param retry: 请求重试次数。
        """
        self._headers = headers
        self._timeout = timeout
        self._session = requests.session()
        self._allow_redirects = allow_redirects
        self._verify = verify
        self._proxies = proxies
        self._retry = retry
        self._cookies = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def timeout(self):
        """
        获取超时时间
        :return:
        """
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        """
        设置超时时间
        :param value:
        :return:
        """
        self._timeout = value

    @property
    def headers(self):
        """
        获取请求头
        :return:
        """
        return self._headers

    @headers.setter
    def headers(self, value):
        """
        设置请求头
        :param value:
        :return:
        """
        self._headers = value

    @property
    def session(self):
        """
        获取session
        :param value:
        :return:
        """
        return self._session

    @session.setter
    def session(self, value):
        """
        设置session
        :param value:
        :return:
        """
        self._session = value

    @property
    def cookies(self):
        """
        :return:
        """
        return self._cookies

    @cookies.setter
    def cookies(self, value):
        """
        :return:
        """
        self._cookies = value

    @property
    def retry(self):
        """
        获取重试次数
        :return:
        """
        return self._retry

    @retry.setter
    def retry(self, value: int):
        """
        设置重试次数
        :return:
        """
        self._retry = value

    @property
    def proxies(self):
        """
        获取代理
        :return:
        """
        return self._proxies

    @proxies.setter
    def proxies(self, value):
        """
        设置代理
        :param value:
        :return:
        """
        self._proxies = value

    @property
    def allow_redirects(self):
        """
        获取是否允许重定向
        :return:
        """
        return self._allow_redirects

    @allow_redirects.setter
    def allow_redirects(self, value):
        """
        设置是否允许重定向
        :param value:
        :return:
        """
        self._allow_redirects = value

    @property
    def verify(self):
        """
        获取是否开启https认证
        :return:
        """
        return self._verify

    @verify.setter
    def verify(self, value):
        """
        设置是否开启https认证
        :param value:
        :return:
        """
        self._verify = value

    def close(self):
        if self._session:
            self._session.close()

    def m_request(self, method, url, **kwargs):
        for i in range(self._retry):
            try:
                return self.session.request(method=method, url=url, headers=self._headers, cookies=self._cookies,
                                            timeout=self._timeout, allow_redirects=self._allow_redirects,
                                            proxies=self._proxies, verify=self._verify, **kwargs)
            except Exception as e:
                print(e)
        else:
            return None

    def get(self, url, **kwargs):
        """发送 GET 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param **kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.m_request(method=Method.GET, url=url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """发送 POST 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return self.m_request(method=Method.POST, url=url, data=data, json=json, **kwargs)

    def options(self, url, **kwargs):
        """发送 OPTIONS 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', True)
        return self.m_request(method=Method.OPTIONS, url=url, **kwargs)

    def head(self, url, **kwargs):
        """发送 HEAD 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        kwargs.setdefault('allow_redirects', False)
        return self.m_request(method=Method.HEAD, url=url, **kwargs)

    def put(self, url, data=None, **kwargs):
        """发送 PUT 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.m_request(method=Method.PUT, url=url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """发送 PATCH 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.m_request(method=Method.PATCH, url=url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        """发送 DELETE 请求. Returns :class:`Response` 对象.

        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.m_request(method=Method.DELETE, url=url, **kwargs)
