# -*- coding: utf-8 -*-
"""
高级功能测试示例
演示如何使用pytest_utils工具类进行复杂测试
"""
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase
from api_test_ez.core.case.frame.pytest_utils import (
    TestDataHelper, AllureHelper, AssertHelper, 
    PerformanceHelper, ConfigHelper, retry_on_failure
)


@allure.feature("高级测试功能")
class TestAdvancedFeatures(BaseCase):
    """高级功能测试类"""
    
    def setup_class(self):
        """类级别设置"""
        self.config = ConfigHelper.get_env_config("test")
        self.base_url = self.config["base_url"]
    
    @allure.story("使用工具类生成测试数据")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_with_generated_data(self):
        """使用工具类生成的测试数据"""
        
        with AllureHelper.step("生成随机用户数据"):
            user_data = TestDataHelper.generate_test_user("API测试用户")
            AllureHelper.attach_request_info(user_data)
        
        with AllureHelper.step("发送创建用户请求"):
            self._request.set({
                "url": f"{self.base_url}/users",
                "method": "POST",
                "body": user_data,
                "body_type": "json",
                "headers": {"Content-Type": "application/json"},
                "timeout": self.config["timeout"],
                "cookies": None,
                "retry": self.config["retry"],
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
        
        with AllureHelper.step("验证响应结构"):
            self.assert_status_code(201)
            
            # 使用AssertHelper验证JSON结构
            expected_structure = {
                "id": int,
                "name": str,
                "username": str,
                "email": str
            }
            
            response_data = response.json()
            AssertHelper.assert_json_structure(response_data, expected_structure)
            
            # 验证数据匹配
            assert response_data["name"] == user_data["name"]
            assert response_data["username"] == user_data["username"]
            assert response_data["email"] == user_data["email"]
    
    @allure.story("性能基准测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.slow
    def test_performance_benchmark(self):
        """API性能基准测试"""
        
        def make_request():
            """执行单次请求"""
            self._request.set({
                "url": f"{self.base_url}/users/1",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": self.config["timeout"],
                "cookies": None,
                "retry": 1,  # 性能测试时减少重试
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            return self.do_request()
        
        with AllureHelper.step("执行性能基准测试"):
            # 执行10次请求的基准测试
            performance_data = PerformanceHelper.benchmark_request(
                self, make_request, iterations=10
            )
            
            # 验证性能指标
            assert performance_data["avg"] < 3000, f"平均响应时间应小于3秒，实际: {performance_data['avg']:.2f}ms"
            assert performance_data["max"] < 5000, f"最大响应时间应小于5秒，实际: {performance_data['max']:.2f}ms"
    
    @allure.story("重试机制测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @retry_on_failure(max_retries=3, delay=1.0)
    def test_with_retry_mechanism(self):
        """带重试机制的测试"""
        
        with AllureHelper.step("执行可能失败的请求"):
            self._request.set({
                "url": f"{self.base_url}/users/1",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 5,  # 较短的超时时间，可能导致失败
                "cookies": None,
                "retry": 1,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            self.assert_status_code(200)
            
            # 验证响应时间
            AssertHelper.assert_response_time(response, 10000, "重试后的请求")
    
    @allure.story("复杂JSON结构验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_complex_json_structure(self):
        """复杂JSON结构验证测试"""
        
        with AllureHelper.step("获取用户详细信息"):
            self._request.set({
                "url": f"{self.base_url}/users/1",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": self.config["timeout"],
                "cookies": None,
                "retry": self.config["retry"],
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            self.assert_status_code(200)
        
        with AllureHelper.step("验证复杂JSON结构"):
            # 定义期望的JSON结构
            expected_structure = {
                "id": int,
                "name": str,
                "username": str,
                "email": str,
                "address": {
                    "street": str,
                    "suite": str,
                    "city": str,
                    "zipcode": str,
                    "geo": {
                        "lat": str,
                        "lng": str
                    }
                },
                "phone": str,
                "website": str,
                "company": {
                    "name": str,
                    "catchPhrase": str,
                    "bs": str
                }
            }
            
            response_data = response.json()
            AssertHelper.assert_json_structure(response_data, expected_structure)
            
            # 验证特定字段值
            assert "@" in response_data["email"], "邮箱应包含@符号"
            assert response_data["id"] == 1, "用户ID应该是1"
    
    @allure.story("多状态码验证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.parametrize("endpoint,valid_codes", [
        ("users", [200]),
        ("posts", [200]),
        ("albums", [200]),
        ("comments", [200])
    ])
    def test_multiple_status_codes(self, endpoint, valid_codes):
        """多状态码验证测试"""
        
        with AllureHelper.step(f"测试{endpoint}端点"):
            self._request.set({
                "url": f"{self.base_url}/{endpoint}",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": self.config["timeout"],
                "cookies": None,
                "retry": self.config["retry"],
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            
            # 使用AssertHelper验证状态码在有效范围内
            AssertHelper.assert_status_code_in(
                response, valid_codes, f"{endpoint}端点"
            )
            
            # 验证响应头
            expected_headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            AssertHelper.assert_headers_contain(
                response, expected_headers, f"{endpoint}端点"
            )
    
    @allure.story("数据清理测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_with_data_cleanup(self):
        """带数据清理的测试"""
        
        created_user_id = None
        
        try:
            with AllureHelper.step("创建测试用户"):
                user_data = TestDataHelper.generate_test_user("清理测试用户")
                
                self._request.set({
                    "url": f"{self.base_url}/users",
                    "method": "POST",
                    "body": user_data,
                    "body_type": "json",
                    "headers": {"Content-Type": "application/json"},
                    "timeout": self.config["timeout"],
                    "cookies": None,
                    "retry": self.config["retry"],
                    "proxies": None,
                    "allow_redirects": True,
                    "verify": True
                })
                
                response = self.do_request()
                self.assert_status_code(201)
                
                created_user_id = response.json().get("id")
                AllureHelper.attach_text(f"创建的用户ID: {created_user_id}", "用户信息")
            
            with AllureHelper.step("验证用户创建成功"):
                # 这里可以添加验证逻辑
                assert created_user_id is not None, "用户ID不应为空"
                
        finally:
            # 清理数据（在实际项目中，这里会调用删除API或数据库清理）
            if created_user_id:
                with AllureHelper.step("清理测试数据"):
                    AllureHelper.attach_text(
                        f"清理用户ID: {created_user_id}",
                        "数据清理"
                    )
                    # 实际的清理逻辑会在这里执行


@allure.feature("错误处理和边界测试")
class TestErrorHandling(BaseCase):
    """错误处理和边界测试"""
    
    def setup_class(self):
        self.config = ConfigHelper.get_env_config("test")
        self.base_url = self.config["base_url"]
    
    @allure.story("超时处理测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_timeout_handling(self):
        """超时处理测试"""
        
        with AllureHelper.step("设置极短超时时间"):
            self._request.set({
                "url": f"{self.base_url}/users",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 0.001,  # 极短的超时时间
                "cookies": None,
                "retry": 1,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            try:
                response = self.do_request()
                # 如果没有超时，验证响应
                self.assert_status_code(200)
            except Exception as e:
                # 验证是超时异常
                AllureHelper.attach_text(
                    f"捕获到预期的超时异常: {str(e)}",
                    "异常信息"
                )
                assert "timeout" in str(e).lower() or "time" in str(e).lower(), \
                    "应该是超时相关的异常"
    
    @allure.story("大数据量处理测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.slow
    def test_large_data_handling(self):
        """大数据量处理测试"""
        
        with AllureHelper.step("请求大量数据"):
            self._request.set({
                "url": f"{self.base_url}/comments",  # comments端点通常有大量数据
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 30,  # 增加超时时间
                "cookies": None,
                "retry": self.config["retry"],
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            response = self.do_request()
            self.assert_status_code(200)
            
            # 验证数据量
            comments = response.json()
            assert isinstance(comments, list), "响应应该是列表"
            assert len(comments) > 100, f"评论数量应该大于100，实际: {len(comments)}"
            
            # 验证响应时间
            AssertHelper.assert_response_time(response, 10000, "大数据量请求")
            
            AllureHelper.attach_text(
                f"获取到 {len(comments)} 条评论数据",
                "数据统计"
            )


@allure.feature("环境配置测试")
class TestEnvironmentConfig(BaseCase):
    """环境配置相关测试"""
    
    @allure.story("不同环境配置测试")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.parametrize("env", ["test", "staging"])
    def test_different_environments(self, env):
        """测试不同环境配置"""
        
        with AllureHelper.step(f"使用{env}环境配置"):
            config = ConfigHelper.get_env_config(env)
            AllureHelper.attach_request_info(config)
            
            self._request.set({
                "url": f"{config['base_url']}/users/1",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": config["timeout"],
                "cookies": None,
                "retry": config["retry"],
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
            
            # 只有test环境的URL是有效的，其他环境可能会失败
            if env == "test":
                response = self.do_request()
                self.assert_status_code(200)
            else:
                # 对于其他环境，我们只验证配置是否正确加载
                assert config["base_url"] is not None
                assert config["timeout"] > 0
                assert config["retry"] >= 0
                
                AllureHelper.attach_text(
                    f"环境 {env} 配置验证通过",
                    "配置验证"
                )