# -*- coding: utf-8 -*-
"""
数据驱动测试示例
演示如何使用外部数据文件进行参数化测试
"""
import pytest
import allure
import json
import os
from api_test_ez.core.case.frame.frame_pytest import BaseCase


def load_test_data(filename):
    """加载测试数据"""
    data_path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@allure.feature("数据驱动测试")
class TestDataDriven(BaseCase):
    """数据驱动测试示例类"""
    
    def setup_class(self):
        """类级别设置"""
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("用户创建数据驱动测试")
    @pytest.mark.parametrize("test_case", load_test_data("user_test_data.json"))
    @pytest.mark.api
    def test_create_user_data_driven(self, test_case):
        """数据驱动的用户创建测试"""
        
        with allure.step(f"执行测试用例: {test_case['test_name']}"):
            # 设置请求参数
            self._request.set({
                "url": f"{self.base_url}/users",
                "method": "POST",
                "body": test_case["user_data"],
                "body_type": "json",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            # 添加测试数据到allure报告
            allure.attach(
                json.dumps(test_case["user_data"], ensure_ascii=False, indent=2),
                name="测试数据",
                attachment_type=allure.attachment_type.JSON
            )
            
            # 执行请求
            response = self.do_request()
            
            # 验证状态码
            expected_status = test_case.get("expected_status", 201)
            self.assert_status_code(expected_status, f"状态码应该是{expected_status}")
            
            # 根据期望状态码进行不同的验证
            if expected_status == 201:
                # 成功创建用户的验证
                response_data = response.json()
                
                # 验证必需字段存在
                expected_fields = test_case.get("expected_fields", [])
                for field in expected_fields:
                    assert field in response_data, f"响应中应该包含字段: {field}"
                
                # 验证用户数据匹配
                user_data = test_case["user_data"]
                for key, value in user_data.items():
                    if key in response_data:
                        assert response_data[key] == value, f"字段{key}的值应该匹配"
            
            else:
                # 错误情况的验证
                if "expected_error" in test_case:
                    # 这里可以验证错误信息
                    # 由于jsonplaceholder总是返回成功，这里只是示例
                    pass


@allure.feature("批量API测试")
class TestBatchAPI(BaseCase):
    """批量API测试示例"""
    
    def setup_class(self):
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("批量获取用户信息")
    @pytest.mark.parametrize("user_id,expected_name", [
        (1, "Leanne Graham"),
        (2, "Ervin Howell"),
        (3, "Clementine Bauch"),
        (4, "Patricia Lebsack"),
        (5, "Chelsey Dietrich")
    ])
    @pytest.mark.api
    @pytest.mark.regression
    def test_get_users_batch(self, user_id, expected_name):
        """批量测试获取用户信息"""
        
        with allure.step(f"获取用户ID {user_id} 的信息"):
            self._request.set({
                "url": f"{self.base_url}/users/{user_id}",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            
            # 验证响应
            self.assert_status_code(200)
            self.assert_json_contains({
                "id": user_id,
                "name": expected_name
            })
            
            # 验证响应时间
            self.assert_response_time(3000, "获取用户信息响应时间应该小于3秒")


@allure.feature("API错误处理测试")
class TestAPIErrorHandling(BaseCase):
    """API错误处理测试"""
    
    def setup_class(self):
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("测试不存在的资源")
    @pytest.mark.parametrize("resource_id", [999, 1000, 9999])
    @pytest.mark.api
    def test_nonexistent_resource(self, resource_id):
        """测试访问不存在的资源"""
        
        with allure.step(f"访问不存在的用户ID: {resource_id}"):
            self._request.set({
                "url": f"{self.base_url}/users/{resource_id}",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            
            # jsonplaceholder对于不存在的资源返回空对象而不是404
            # 这里只是演示如何处理这种情况
            self.assert_status_code(200)
            
            response_data = response.json()
            # 验证返回的是空对象或者包含错误信息
            if not response_data or response_data == {}:
                allure.attach("资源不存在，返回空对象", name="验证结果", attachment_type=allure.attachment_type.TEXT)
    
    @allure.story("测试无效的HTTP方法")
    @pytest.mark.parametrize("method", ["PATCH", "HEAD", "OPTIONS"])
    @pytest.mark.api
    def test_invalid_http_methods(self, method):
        """测试不支持的HTTP方法"""
        
        with allure.step(f"使用HTTP方法: {method}"):
            self._request.set({
                "url": f"{self.base_url}/users/1",
                "method": method,
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            try:
                response = self.do_request()
                # 如果请求成功，验证响应
                assert response.status_code in [200, 405, 501], f"HTTP方法{method}应该返回合适的状态码"
            except ValueError as e:
                # 如果框架不支持该方法，验证错误信息
                assert "不支持的HTTP方法" in str(e), f"应该提示不支持的HTTP方法: {method}"


# 动态生成测试用例的示例
def generate_test_cases():
    """动态生成测试用例"""
    base_cases = [
        {"endpoint": "users", "count": 10},
        {"endpoint": "posts", "count": 100},
        {"endpoint": "albums", "count": 100},
        {"endpoint": "comments", "count": 500}
    ]
    return base_cases


@allure.feature("动态测试用例")
class TestDynamicCases(BaseCase):
    """动态生成的测试用例"""
    
    def setup_class(self):
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("验证API端点数据量")
    @pytest.mark.parametrize("test_case", generate_test_cases())
    @pytest.mark.api
    @pytest.mark.slow
    def test_endpoint_data_count(self, test_case):
        """验证各个端点的数据量"""
        
        endpoint = test_case["endpoint"]
        expected_count = test_case["count"]
        
        with allure.step(f"验证{endpoint}端点的数据量"):
            self._request.set({
                "url": f"{self.base_url}/{endpoint}",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 30,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            
            self.assert_status_code(200)
            
            data = response.json()
            assert isinstance(data, list), f"{endpoint}应该返回列表"
            
            actual_count = len(data)
            assert actual_count >= expected_count, \
                f"{endpoint}数据量不足，期望至少{expected_count}条，实际{actual_count}条"
            
            allure.attach(
                f"端点: {endpoint}\n期望数量: {expected_count}\n实际数量: {actual_count}",
                name="数据量验证结果",
                attachment_type=allure.attachment_type.TEXT
            )