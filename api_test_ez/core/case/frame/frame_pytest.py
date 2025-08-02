# -*- coding: utf-8 -*-
"""
# @Time    : 2025/8/1 15:41
# @Author  : wangfei
# @desc    : Pytest框架适配器，支持allure报告
"""
import json
from typing import Any, Dict, Optional

try:
    import pytest
    import allure
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # 创建mock对象以避免导入错误
    class MockAllure:
        @staticmethod
        def step(description):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def attach(*args, **kwargs):
            pass
        
        @staticmethod
        def dynamic():
            class Dynamic:
                @staticmethod
                def feature(name):
                    pass
                @staticmethod
                def story(name):
                    pass
            return Dynamic()
        
        attachment_type = type('AttachmentType', (), {
            'JSON': 'application/json',
            'TEXT': 'text/plain'
        })()
    
    allure = MockAllure()

from api_test_ez.core.case.http.request import Request
from api_test_ez.core.case.http.response import Response
from api_test_ez.ez import Http


class PytestHttpFrame:
    """Pytest HTTP测试框架基类"""
    
    def __init__(self):
        self._http = Http()
        self._request = None
        self._response = None
        self.__autoRequest__ = 'on'
    
    def setup_method(self, method):
        """每个测试方法执行前的设置"""
        self.init_request(method.__name__)
        self.before_request()
    
    def teardown_method(self, method):
        """每个测试方法执行后的清理"""
        self.after_request()
    
    def init_request(self, testmethod_name: str):
        """初始化请求"""
        self._request = Request(self._http)
        self._request.owner = testmethod_name
    
    def before_request(self):
        """请求前的准备工作"""
        pass
    
    def do_request(self, request: Optional[Request] = None) -> Response:
        """执行HTTP请求"""
        if request:
            self._request = request
        
        if not self._request:
            raise ValueError("请求对象未初始化")
        
        # 添加allure步骤记录
        with allure.step(f"执行HTTP请求: {self._request.method} {self._request.url}"):
            # 记录请求信息到allure
            allure.attach(
                json.dumps({
                    "url": self._request.url,
                    "method": self._request.method,
                    "headers": dict(self._request.http.headers) if self._request.http.headers else {},
                    "body": self._request.body
                }, ensure_ascii=False, indent=2),
                name="请求信息",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 执行请求
            if self._request.method.upper() == 'GET':
                response = self._http.get(
                    url=self._request.url,
                    params=self._request.body if self._request.body_type == 'params' else None
                )
            elif self._request.method.upper() == 'POST':
                if self._request.body_type == 'json':
                    response = self._http.post(
                        url=self._request.url,
                        json=self._request.body
                    )
                elif self._request.body_type == 'data':
                    response = self._http.post(
                        url=self._request.url,
                        data=self._request.body
                    )
                elif self._request.body_type == 'files':
                    response = self._http.post(
                        url=self._request.url,
                        files=self._request.files,
                        data=self._request.body
                    )
                else:
                    response = self._http.post(
                        url=self._request.url,
                        data=self._request.body
                    )
            elif self._request.method.upper() == 'PUT':
                if self._request.body_type == 'json':
                    response = self._http.put(
                        url=self._request.url,
                        json=self._request.body
                    )
                else:
                    response = self._http.put(
                        url=self._request.url,
                        data=self._request.body
                    )
            elif self._request.method.upper() == 'DELETE':
                response = self._http.delete(
                    url=self._request.url,
                    params=self._request.body if self._request.body_type == 'params' else None
                )
            elif self._request.method.upper() == 'PATCH':
                if self._request.body_type == 'json':
                    response = self._http.patch(
                        url=self._request.url,
                        json=self._request.body
                    )
                else:
                    response = self._http.patch(
                        url=self._request.url,
                        data=self._request.body
                    )
            else:
                raise ValueError(f"不支持的HTTP方法: {self._request.method}")
            
            # 创建响应对象
            self._response = Response(response)
            
            # 记录响应信息到allure
            allure.attach(
                json.dumps({
                    "status_code": self._response.status_code,
                    "headers": dict(self._response.headers),
                    "body": self._response.text
                }, ensure_ascii=False, indent=2),
                name="响应信息",
                attachment_type=allure.attachment_type.JSON
            )
            
            return self._response
    
    def after_request(self):
        """请求后的处理"""
        pass
    
    @property
    def request(self) -> Request:
        """获取请求对象"""
        return self._request
    
    @property
    def response(self) -> Response:
        """获取响应对象"""
        return self._response
    
    def assert_status_code(self, expected_code: int, message: str = ""):
        """断言状态码"""
        with allure.step(f"断言状态码为 {expected_code}"):
            actual_code = self._response.status_code
            assert actual_code == expected_code, \
                f"{message} 期望状态码: {expected_code}, 实际状态码: {actual_code}"
    
    def assert_json_contains(self, expected_data: Dict[str, Any], message: str = ""):
        """断言JSON响应包含指定数据"""
        with allure.step(f"断言JSON包含数据: {expected_data}"):
            response_json = self._response.json()
            for key, value in expected_data.items():
                assert key in response_json, f"{message} 响应JSON中缺少字段: {key}"
                assert response_json[key] == value, \
                    f"{message} 字段 {key} 值不匹配, 期望: {value}, 实际: {response_json[key]}"
    
    def assert_json_schema(self, schema: Dict[str, Any], message: str = ""):
        """断言JSON响应符合指定schema"""
        with allure.step("断言JSON Schema"):
            # 这里可以集成jsonschema库进行验证
            pass
    
    def assert_response_time(self, max_time: float, message: str = ""):
        """断言响应时间"""
        with allure.step(f"断言响应时间小于 {max_time}ms"):
            actual_time = self._response.elapsed.total_seconds() * 1000
            assert actual_time <= max_time, \
                f"{message} 响应时间超时, 期望: <={max_time}ms, 实际: {actual_time}ms"


class BaseCase(PytestHttpFrame):
    """基础测试用例类，继承自PytestHttpFrame"""
    pass


# Pytest插件钩子函数
def pytest_configure(config):
    """Pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "api: 标记API测试用例"
    )
    config.addinivalue_line(
        "markers", "smoke: 标记冒烟测试用例"
    )
    config.addinivalue_line(
        "markers", "regression: 标记回归测试用例"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试用例收集"""
    for item in items:
        # 为所有测试用例添加allure标签
        if hasattr(item, 'cls') and item.cls and issubclass(item.cls, PytestHttpFrame):
            # 添加allure特性标签
            if not hasattr(item, '_allure_feature'):
                allure.dynamic.feature("API测试")
            if not hasattr(item, '_allure_story'):
                allure.dynamic.story(item.cls.__name__)


@pytest.fixture(scope="session")
def api_test_config():
    """API测试配置fixture"""
    return {
        "base_url": "http://localhost:8080",
        "timeout": 30,
        "retry": 3
    }


@pytest.fixture(scope="function")
def http_client():
    """HTTP客户端fixture"""
    return Http()