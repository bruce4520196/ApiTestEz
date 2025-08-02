# -*- coding: utf-8 -*-
"""
Pytest配置文件
包含全局fixtures和配置
"""
import pytest
import allure
import os
import json
from datetime import datetime
from api_test_ez.ez import Http
from api_test_ez.ez.config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """测试环境设置"""
    # 创建报告目录
    os.makedirs("reports/allure-results", exist_ok=True)
    os.makedirs("reports/html", exist_ok=True)
    os.makedirs("reports/logs", exist_ok=True)
    
    # 设置allure环境信息
    env_info = {
        "测试环境": "测试环境",
        "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Python版本": "3.8+",
        "框架版本": "ApiTestEz v1.0"
    }
    
    with open("reports/allure-results/environment.properties", "w", encoding="utf-8") as f:
        for key, value in env_info.items():
            f.write(f"{key}={value}\n")


@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return {
        "base_url": "https://jsonplaceholder.typicode.com",
        "timeout": 30,
        "retry": 3,
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "ApiTestEz/1.0"
        }
    }


@pytest.fixture(scope="function")
def http_client():
    """HTTP客户端fixture"""
    client = Http()
    client.timeout = 30
    client.retry = 3
    return client


@pytest.fixture(scope="function")
def api_base_url():
    """API基础URL fixture"""
    return "https://jsonplaceholder.typicode.com"


def pytest_configure(config):
    """Pytest配置钩子"""
    # 添加自定义标记
    markers = [
        "api: API接口测试",
        "smoke: 冒烟测试",
        "regression: 回归测试",
        "slow: 慢速测试",
        "unit: 单元测试",
        "integration: 集成测试",
        "e2e: 端到端测试",
        "critical: 关键测试用例"
    ]
    
    for marker in markers:
        config.addinivalue_line("markers", marker)


def pytest_collection_modifyitems(config, items):
    """修改测试用例收集"""
    for item in items:
        # 为没有标记的测试用例添加默认标记
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.api)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    
    # 为失败的测试用例添加截图或额外信息
    if rep.when == "call" and rep.failed:
        # 这里可以添加失败时的额外信息收集
        if hasattr(item.instance, '_response') and item.instance._response:
            # 将响应信息附加到allure报告
            allure.attach(
                json.dumps({
                    "status_code": item.instance._response.status_code,
                    "headers": dict(item.instance._response.headers),
                    "body": item.instance._response.text
                }, ensure_ascii=False, indent=2),
                name="失败时的响应信息",
                attachment_type=allure.attachment_type.JSON
            )


def pytest_html_report_title(report):
    """自定义HTML报告标题"""
    report.title = "ApiTestEz API测试报告"


def pytest_html_results_summary(prefix, summary, postfix):
    """自定义HTML报告摘要"""
    prefix.extend([
        "<h2>测试环境信息</h2>",
        "<p>测试框架: ApiTestEz</p>",
        f"<p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        "<p>测试环境: 测试环境</p>"
    ])


@pytest.fixture(autouse=True)
def add_allure_environment_property():
    """自动添加allure环境属性"""
    allure.environment(framework="ApiTestEz")
    allure.environment(language="Python")
    allure.environment(test_type="API测试")