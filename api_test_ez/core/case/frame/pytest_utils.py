# -*- coding: utf-8 -*-
"""
Pytest测试工具类
提供常用的测试辅助功能
"""
import json
import os
import time
import random
import string
from typing import Dict, Any, List, Optional
import allure


class TestDataHelper:
    """测试数据辅助类"""
    
    @staticmethod
    def load_json_data(filename: str, data_dir: str = "data") -> List[Dict]:
        """加载JSON测试数据文件"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上查找tests目录
        tests_dir = current_dir
        while tests_dir and not tests_dir.endswith('tests'):
            tests_dir = os.path.dirname(tests_dir)
            if tests_dir == os.path.dirname(tests_dir):  # 到达根目录
                tests_dir = os.path.join(os.getcwd(), 'tests')
                break
        
        data_path = os.path.join(tests_dir, data_dir, filename)
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"测试数据文件不存在: {data_path}")
        
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_email() -> str:
        """生成随机邮箱"""
        username = TestDataHelper.generate_random_string(8)
        domain = random.choice(['example.com', 'test.com', 'demo.org'])
        return f"{username}@{domain}"
    
    @staticmethod
    def generate_random_phone() -> str:
        """生成随机手机号"""
        prefixes = ['138', '139', '150', '151', '152', '188', '189']
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{suffix}"
    
    @staticmethod
    def generate_test_user(name_prefix: str = "测试用户") -> Dict[str, Any]:
        """生成测试用户数据"""
        random_suffix = TestDataHelper.generate_random_string(4)
        return {
            "name": f"{name_prefix}_{random_suffix}",
            "username": f"user_{random_suffix.lower()}",
            "email": TestDataHelper.generate_random_email(),
            "phone": TestDataHelper.generate_random_phone()
        }


class AllureHelper:
    """Allure报告辅助类"""
    
    @staticmethod
    def attach_request_info(request_data: Dict[str, Any]):
        """附加请求信息到allure报告"""
        allure.attach(
            json.dumps(request_data, ensure_ascii=False, indent=2),
            name="请求信息",
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def attach_response_info(response_data: Dict[str, Any]):
        """附加响应信息到allure报告"""
        allure.attach(
            json.dumps(response_data, ensure_ascii=False, indent=2),
            name="响应信息",
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def attach_text(content: str, name: str = "附加信息"):
        """附加文本信息到allure报告"""
        allure.attach(
            content,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    def step(description: str):
        """创建allure测试步骤"""
        return allure.step(description)


class AssertHelper:
    """断言辅助类"""
    
    @staticmethod
    def assert_json_structure(actual_data: Dict, expected_structure: Dict, path: str = "root"):
        """断言JSON结构匹配"""
        for key, expected_type in expected_structure.items():
            assert key in actual_data, f"路径 {path}.{key} 缺少必需字段"
            
            actual_value = actual_data[key]
            
            if isinstance(expected_type, dict):
                # 嵌套对象
                assert isinstance(actual_value, dict), f"路径 {path}.{key} 应该是对象类型"
                AssertHelper.assert_json_structure(actual_value, expected_type, f"{path}.{key}")
            elif isinstance(expected_type, list):
                # 数组类型
                assert isinstance(actual_value, list), f"路径 {path}.{key} 应该是数组类型"
                if expected_type and isinstance(expected_type[0], dict):
                    # 对象数组
                    for i, item in enumerate(actual_value):
                        AssertHelper.assert_json_structure(item, expected_type[0], f"{path}.{key}[{i}]")
            else:
                # 基本类型
                assert isinstance(actual_value, expected_type), \
                    f"路径 {path}.{key} 类型错误，期望 {expected_type.__name__}，实际 {type(actual_value).__name__}"
    
    @staticmethod
    def assert_response_time(response, max_time_ms: int, message: str = ""):
        """断言响应时间"""
        actual_time_ms = response.elapsed.total_seconds() * 1000
        assert actual_time_ms <= max_time_ms, \
            f"{message} 响应时间超时，期望 <={max_time_ms}ms，实际 {actual_time_ms:.2f}ms"
    
    @staticmethod
    def assert_status_code_in(response, valid_codes: List[int], message: str = ""):
        """断言状态码在指定范围内"""
        actual_code = response.status_code
        assert actual_code in valid_codes, \
            f"{message} 状态码不在有效范围内，期望 {valid_codes}，实际 {actual_code}"
    
    @staticmethod
    def assert_headers_contain(response, expected_headers: Dict[str, str], message: str = ""):
        """断言响应头包含指定内容"""
        actual_headers = dict(response.headers)
        for key, expected_value in expected_headers.items():
            assert key in actual_headers, f"{message} 响应头缺少字段: {key}"
            assert actual_headers[key] == expected_value, \
                f"{message} 响应头 {key} 值不匹配，期望: {expected_value}，实际: {actual_headers[key]}"


class PerformanceHelper:
    """性能测试辅助类"""
    
    @staticmethod
    def measure_time(func):
        """测量函数执行时间的装饰器"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            AllureHelper.attach_text(
                f"执行时间: {execution_time:.2f}ms",
                "性能指标"
            )
            
            return result, execution_time
        return wrapper
    
    @staticmethod
    def benchmark_request(test_case, request_func, iterations: int = 10):
        """基准测试请求性能"""
        times = []
        
        with allure.step(f"执行{iterations}次性能测试"):
            for i in range(iterations):
                start_time = time.time()
                response = request_func()
                end_time = time.time()
                
                execution_time = (end_time - start_time) * 1000
                times.append(execution_time)
                
                # 验证每次请求都成功
                assert response.status_code == 200, f"第{i+1}次请求失败"
        
        # 计算性能指标
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        performance_report = {
            "迭代次数": iterations,
            "平均响应时间": f"{avg_time:.2f}ms",
            "最小响应时间": f"{min_time:.2f}ms",
            "最大响应时间": f"{max_time:.2f}ms",
            "所有响应时间": [f"{t:.2f}ms" for t in times]
        }
        
        AllureHelper.attach_response_info(performance_report)
        
        return {
            "avg": avg_time,
            "min": min_time,
            "max": max_time,
            "times": times
        }


class DatabaseHelper:
    """数据库辅助类（示例）"""
    
    @staticmethod
    def cleanup_test_data(table_name: str, condition: str):
        """清理测试数据（需要根据实际数据库实现）"""
        # 这里只是示例，实际使用时需要根据具体数据库实现
        with allure.step(f"清理测试数据: {table_name}"):
            # 实际的数据库清理逻辑
            pass
    
    @staticmethod
    def verify_database_state(expected_state: Dict[str, Any]):
        """验证数据库状态（需要根据实际数据库实现）"""
        # 这里只是示例，实际使用时需要根据具体数据库实现
        with allure.step("验证数据库状态"):
            # 实际的数据库验证逻辑
            pass


class ConfigHelper:
    """配置辅助类"""
    
    @staticmethod
    def get_env_config(env: str = "test") -> Dict[str, Any]:
        """获取环境配置"""
        configs = {
            "test": {
                "base_url": "https://jsonplaceholder.typicode.com",
                "timeout": 30,
                "retry": 3
            },
            "staging": {
                "base_url": "https://staging-api.example.com",
                "timeout": 30,
                "retry": 3
            },
            "prod": {
                "base_url": "https://api.example.com",
                "timeout": 10,
                "retry": 1
            }
        }
        
        return configs.get(env, configs["test"])
    
    @staticmethod
    def get_test_user_credentials(user_type: str = "normal") -> Dict[str, str]:
        """获取测试用户凭据"""
        credentials = {
            "normal": {
                "username": "test_user",
                "password": "test_password"
            },
            "admin": {
                "username": "admin_user",
                "password": "admin_password"
            },
            "readonly": {
                "username": "readonly_user",
                "password": "readonly_password"
            }
        }
        
        return credentials.get(user_type, credentials["normal"])


# 常用的测试装饰器
def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        AllureHelper.attach_text(
                            f"第{attempt + 1}次尝试失败，{delay}秒后重试: {str(e)}",
                            "重试信息"
                        )
                        time.sleep(delay)
                    else:
                        AllureHelper.attach_text(
                            f"所有{max_retries}次尝试都失败了",
                            "重试结果"
                        )
            
            raise last_exception
        return wrapper
    return decorator


def skip_if_env(env_var: str, skip_value: str = "true"):
    """根据环境变量跳过测试"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if os.environ.get(env_var, "").lower() == skip_value.lower():
                import pytest
                pytest.skip(f"由于环境变量 {env_var}={skip_value} 跳过测试")
            return func(*args, **kwargs)
        return wrapper
    return decorator