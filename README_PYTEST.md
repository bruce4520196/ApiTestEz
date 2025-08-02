# ApiTestEz Pytest框架使用指南

## 概述

ApiTestEz现已完全支持Pytest框架，并集成了allure测试报告功能。本文档将指导您如何使用这些功能进行API测试。

## 功能特性

- ✅ 完整的Pytest框架适配
- ✅ Allure测试报告集成
- ✅ 自动化HTTP请求处理
- ✅ 丰富的断言方法
- ✅ 参数化测试支持
- ✅ 并行测试执行
- ✅ 详细的测试日志
- ✅ HTML和Allure双重报告

## 安装依赖

### 方法1：使用脚本安装
```bash
python run_tests.py --install
```

### 方法2：手动安装
```bash
pip install -r requirements.txt
```

### 安装Allure命令行工具
1. 安装Java 8或更高版本
2. 下载Allure命令行工具：https://github.com/allure-framework/allure2/releases
3. 解压并将`allure/bin`目录添加到PATH环境变量

## 快速开始

### 1. 创建测试用例

```python
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase

@allure.feature("用户管理API")
class TestUserAPI(BaseCase):
    
    def setup_class(self):
        self.base_url = "https://api.example.com"
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_get_user(self):
        # 设置请求参数
        self._request.set({
            "url": f"{self.base_url}/users/1",
            "method": "GET",
            "headers": {"Content-Type": "application/json"},
            "timeout": 10,
            "cookies": None,
            "retry": 3,
            "proxies": None,
            "allow_redirects": True,
            "verify": True
        })
        
        # 执行请求
        response = self.do_request()
        
        # 断言验证
        self.assert_status_code(200)
        self.assert_json_contains({"id": 1})
```

### 2. 运行测试

#### 基本运行
```bash
# 运行所有测试
python run_tests.py

# 运行指定目录的测试
python run_tests.py --test tests/api

# 运行指定标记的测试
python run_tests.py --markers smoke

# 并行运行测试
python run_tests.py --parallel
```

#### 使用pytest命令
```bash
# 基本运行
pytest tests/

# 运行指定标记
pytest -m "smoke" tests/

# 并行运行
pytest -n auto tests/

# 生成allure结果
pytest --alluredir=reports/allure-results tests/
```

### 3. 生成和查看报告

```bash
# 生成allure报告
python run_tests.py --report-only

# 启动allure报告服务
python run_tests.py --serve

# 清理报告目录
python run_tests.py --clean
```

## 核心功能详解

### 1. BaseCase基类

`BaseCase`是所有测试用例的基类，提供了以下功能：

- **自动HTTP请求处理**：继承后自动获得HTTP请求能力
- **Allure集成**：自动记录请求和响应信息到allure报告
- **丰富的断言方法**：提供多种断言方法简化验证

### 2. 请求设置

使用`self._request.set()`方法设置请求参数：

```python
self._request.set({
    "url": "https://api.example.com/users",
    "method": "POST",
    "body": {"name": "测试用户"},
    "body_type": "json",  # json, data, params, files
    "headers": {"Content-Type": "application/json"},
    "timeout": 30,
    "cookies": None,
    "retry": 3,
    "proxies": None,
    "allow_redirects": True,
    "verify": True
})
```

### 3. 支持的HTTP方法

- GET
- POST
- PUT
- DELETE
- PATCH

### 4. 断言方法

```python
# 状态码断言
self.assert_status_code(200, "应该返回200状态码")

# JSON内容断言
self.assert_json_contains({"id": 1, "name": "测试"})

# 响应时间断言
self.assert_response_time(2000, "响应时间应该小于2秒")
```

### 5. Allure注解

```python
@allure.feature("功能模块")
@allure.story("用户故事")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("测试描述")
@allure.link("https://example.com", name="相关链接")
@allure.issue("ISSUE-123", "问题链接")
@allure.testcase("TC-456", "测试用例链接")
```

### 6. Pytest标记

```python
@pytest.mark.api          # API测试
@pytest.mark.smoke        # 冒烟测试
@pytest.mark.regression   # 回归测试
@pytest.mark.slow         # 慢速测试
@pytest.mark.critical     # 关键测试
```

### 7. 参数化测试

```python
@pytest.mark.parametrize("user_id", [1, 2, 3, 4, 5])
def test_get_user_parametrized(self, user_id):
    self._request.set({
        "url": f"{self.base_url}/users/{user_id}",
        "method": "GET"
    })
    response = self.do_request()
    self.assert_status_code(200)
```

## 配置文件

### pytest.ini
Pytest的主配置文件，包含：
- 测试发现规则
- 命令行选项
- 标记定义
- 日志配置

### allure.properties
Allure报告配置文件，包含：
- 结果目录配置
- 链接模式配置

### conftest.py
Pytest的配置和fixture文件，包含：
- 全局fixture
- 钩子函数
- 环境设置

## 报告功能

### HTML报告
- 位置：`reports/html/report.html`
- 包含测试结果统计、失败详情、日志等

### Allure报告
- 位置：`reports/allure-report/index.html`
- 包含详细的测试步骤、附件、趋势图等

## 最佳实践

### 1. 测试组织
```
tests/
├── conftest.py          # 全局配置
├── api/
│   ├── test_user.py     # 用户相关API测试
│   ├── test_order.py    # 订单相关API测试
│   └── test_product.py  # 产品相关API测试
└── integration/
    └── test_workflow.py # 集成测试
```

### 2. 命名规范
- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试方法：`test_*`

### 3. 标记使用
```python
@pytest.mark.smoke      # 冒烟测试，快速验证核心功能
@pytest.mark.regression # 回归测试，全面验证功能
@pytest.mark.api        # API接口测试
@pytest.mark.slow       # 耗时较长的测试
```

### 4. 数据驱动测试
```python
# 使用外部数据文件
@pytest.mark.parametrize("test_data", load_test_data("user_data.json"))
def test_create_user(self, test_data):
    # 测试逻辑
    pass
```

## 故障排除

### 1. 常见问题

**Q: Allure命令未找到**
A: 请确保已安装Java和Allure命令行工具，并添加到PATH

**Q: 测试运行失败**
A: 检查依赖是否完整安装，运行`python run_tests.py --install`

**Q: 报告生成失败**
A: 确保`reports`目录有写权限，运行`python run_tests.py --clean`清理后重试

### 2. 调试技巧

```python
# 在测试中添加调试信息
def test_debug_example(self):
    response = self.do_request()
    
    # 打印响应信息用于调试
    print(f"状态码: {response.status_code}")
    print(f"响应体: {response.text}")
    
    # 添加到allure报告
    allure.attach(response.text, "调试信息", allure.attachment_type.TEXT)
```

## 示例项目

查看`tests/test_api_example.py`文件获取完整的使用示例。

## 更多信息

- [Pytest官方文档](https://docs.pytest.org/)
- [Allure官方文档](https://docs.qameta.io/allure/)
- [ApiTestEz项目地址](https://github.com/bruce4520196/ApiTestEz)