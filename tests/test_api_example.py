# -*- coding: utf-8 -*-
"""
API测试示例
演示如何使用ApiTestEz的Pytest框架进行API测试
"""
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase


@allure.feature("用户管理API")
class TestUserAPI(BaseCase):
    """用户管理API测试类"""
    
    def setup_class(self):
        """类级别的设置"""
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_user_info(self):
        """测试获取用户信息接口"""
        with allure.step("准备测试数据"):
            user_id = 1
            
        with allure.step("设置请求参数"):
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
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(200, "获取用户信息应该返回200状态码")
            self.assert_json_contains({
                "id": user_id,
                "name": "Leanne Graham"
            }, "响应应该包含正确的用户信息")
    
    @allure.story("创建用户")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_create_user(self):
        """测试创建用户接口"""
        with allure.step("准备用户数据"):
            user_data = {
                "name": "测试用户",
                "username": "testuser",
                "email": "test@example.com"
            }
        
        with allure.step("设置请求参数"):
            self._request.set({
                "url": f"{self.base_url}/users",
                "method": "POST",
                "body": user_data,
                "body_type": "json",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(201, "创建用户应该返回201状态码")
            response_data = response.json()
            assert "id" in response_data, "响应应该包含用户ID"
            assert response_data["name"] == user_data["name"], "用户名应该匹配"
    
    @allure.story("更新用户信息")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_update_user(self):
        """测试更新用户信息接口"""
        with allure.step("准备测试数据"):
            user_id = 1
            update_data = {
                "name": "更新后的用户名",
                "email": "updated@example.com"
            }
        
        with allure.step("设置请求参数"):
            self._request.set({
                "url": f"{self.base_url}/users/{user_id}",
                "method": "PUT",
                "body": update_data,
                "body_type": "json",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(200, "更新用户应该返回200状态码")
            response_data = response.json()
            assert response_data["name"] == update_data["name"], "用户名应该已更新"
    
    @allure.story("删除用户")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_delete_user(self):
        """测试删除用户接口"""
        with allure.step("准备测试数据"):
            user_id = 1
        
        with allure.step("设置请求参数"):
            self._request.set({
                "url": f"{self.base_url}/users/{user_id}",
                "method": "DELETE",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(200, "删除用户应该返回200状态码")


@allure.feature("文章管理API")
class TestPostAPI(BaseCase):
    """文章管理API测试类"""
    
    def setup_class(self):
        """类级别的设置"""
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("获取文章列表")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.regression
    def test_get_posts(self):
        """测试获取文章列表接口"""
        with allure.step("设置请求参数"):
            self._request.set({
                "url": f"{self.base_url}/posts",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(200, "获取文章列表应该返回200状态码")
            posts = response.json()
            assert isinstance(posts, list), "响应应该是一个列表"
            assert len(posts) > 0, "文章列表不应该为空"
            
            # 验证第一篇文章的结构
            first_post = posts[0]
            required_fields = ["id", "title", "body", "userId"]
            for field in required_fields:
                assert field in first_post, f"文章对象应该包含字段: {field}"
    
    @allure.story("获取单篇文章")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_single_post(self):
        """测试获取单篇文章接口"""
        with allure.step("准备测试数据"):
            post_id = 1
        
        with allure.step("设置请求参数"):
            self._request.set({
                "url": f"{self.base_url}/posts/{post_id}",
                "method": "GET",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10,
                "cookies": None,
                "retry": 3,
                "proxies": None,
                "allow_redirects": True,
                "verify": True
            })
        
        with allure.step("执行请求"):
            response = self.do_request()
        
        with allure.step("验证响应"):
            self.assert_status_code(200, "获取文章应该返回200状态码")
            self.assert_response_time(2000, "响应时间应该小于2秒")
            
            post = response.json()
            assert post["id"] == post_id, f"文章ID应该是{post_id}"
            assert "title" in post, "文章应该有标题"
            assert "body" in post, "文章应该有内容"


# 参数化测试示例
@allure.feature("参数化测试")
class TestParametrized(BaseCase):
    """参数化测试示例"""
    
    def setup_class(self):
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("批量测试用户ID")
    @pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
    @pytest.mark.api
    def test_get_users_parametrized(self, user_id):
        """参数化测试获取不同用户信息"""
        with allure.step(f"测试用户ID: {user_id}"):
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
            self.assert_status_code(200)
            
            user = response.json()
            assert user["id"] == user_id, f"用户ID应该是{user_id}"