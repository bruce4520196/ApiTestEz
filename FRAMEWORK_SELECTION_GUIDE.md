# ApiTestEz 框架选择使用指南

## 概述

ApiTestEz现在支持通过命令行参数选择测试框架，您可以选择使用传统的unittest框架或现代的pytest框架来运行测试。

## 命令行参数

### 框架选择参数
```bash
-fk, --framework {unittest,pytest}
```

- **unittest**: 传统的Python单元测试框架（默认）
- **pytest**: 现代化的Python测试框架，支持allure报告

## 使用方法

### 1. 使用unittest框架（默认）

```bash
# 默认使用unittest框架
ez run tests/test_example.py

# 显式指定unittest框架
ez run tests/test_example.py --framework unittest
ez run tests/test_example.py -fk unittest
```

**特点：**
- 使用传统的unittest测试类
- 支持BeautifulReport和HTML报告
- 兼容现有的所有测试用例

### 2. 使用pytest框架

```bash
# 使用pytest框架
ez run tests/test_example.py --framework pytest
ez run tests/test_example.py -fk pytest
```

**特点：**
- 使用现代化的pytest框架
- 自动生成allure报告和HTML报告
- 支持丰富的pytest插件生态
- 更好的测试发现和参数化支持

## 测试用例编写

### unittest框架测试用例

```python
# test_unittest_example.py
import unittest
from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame

class TestUserAPI(UnitHttpFrame):
    
    def setUp(self):
        self.base_url = "https://api.example.com"
    
    def test_get_user(self):
        """测试获取用户信息"""
        # 设置请求
        self.initRequest("test_get_user")
        # 执行测试逻辑
        self.assertTrue(True)
```

### pytest框架测试用例

```python
# test_pytest_example.py
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase

@allure.feature("用户管理API")
class TestUserAPI(BaseCase):
    
    def setup_class(self):
        self.base_url = "https://api.example.com"
    
    @allure.story("获取用户信息")
    @pytest.mark.api
    def test_get_user(self):
        """测试获取用户信息"""
        self._request.set({
            "url": f"{self.base_url}/users/1",
            "method": "GET"
        })
        response = self.do_request()
        self.assert_status_code(200)
```

## 报告生成

### unittest框架报告

使用unittest框架时，会根据`--report-style`参数生成相应报告：

```bash
# 生成BeautifulReport报告
ez run tests/ --framework unittest --report-style br

# 生成HTML报告
ez run tests/ --framework unittest --report-style html
```

### pytest框架报告

使用pytest框架时，会自动生成多种报告：

```bash
ez run tests/ --framework pytest
```

生成的报告包括：
- **HTML报告**: `reports/pytest_report.html`
- **Allure结果**: `reports/allure-results/`
- **Allure报告**: `reports/allure-report/index.html`（如果安装了allure命令行工具）

## 完整命令示例

### 基础使用

```bash
# 运行单个测试文件（unittest）
ez run tests/test_api.py

# 运行单个测试文件（pytest）
ez run tests/test_api.py --framework pytest

# 运行测试目录（unittest）
ez run tests/ --framework unittest

# 运行测试目录（pytest）
ez run tests/ --framework pytest
```

### 带报告配置

```bash
# unittest + BeautifulReport
ez run tests/ \
    --framework unittest \
    --report-style br \
    --report-file reports/beautiful_report.html \
    --tester "测试工程师"

# unittest + HTML报告
ez run tests/ \
    --framework unittest \
    --report-style html \
    --report-file reports/html_report.html

# pytest + 自动报告
ez run tests/ \
    --framework pytest \
    --report-file reports/pytest_results
```

### 带配置参数

```bash
# 使用配置文件
ez run tests/ \
    --framework pytest \
    --config-file config/test.cfg

# 使用命令行配置
ez run tests/ \
    --framework pytest \
    --config host=127.0.0.1 \
    --config timeout=30
```

## 框架对比

| 特性 | unittest | pytest |
|------|----------|--------|
| 学习曲线 | 简单 | 中等 |
| 报告功能 | BeautifulReport/HTML | Allure/HTML |
| 插件生态 | 有限 | 丰富 |
| 参数化测试 | 基础支持 | 强大支持 |
| 并行执行 | 不支持 | 支持 |
| 断言方式 | self.assert* | assert语句 |
| 测试发现 | 基础 | 智能 |
| 兼容性 | 完全兼容现有代码 | 需要适配 |

## 迁移指南

### 从unittest迁移到pytest

1. **修改测试类继承**：
   ```python
   # 原来
   from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame
   class TestAPI(UnitHttpFrame):
   
   # 现在
   from api_test_ez.core.case.frame.frame_pytest import BaseCase
   class TestAPI(BaseCase):
   ```

2. **修改生命周期方法**：
   ```python
   # 原来
   def setUp(self):
   def tearDown(self):
   
   # 现在
   def setup_method(self, method):
   def teardown_method(self, method):
   ```

3. **修改断言方式**：
   ```python
   # 原来
   self.assertEqual(response.status_code, 200)
   
   # 现在
   self.assert_status_code(200)
   # 或者
   assert response.status_code == 200
   ```

4. **添加allure注解**：
   ```python
   @allure.feature("API功能")
   @allure.story("用户管理")
   @pytest.mark.api
   def test_example(self):
   ```

## 故障排除

### 常见问题

1. **pytest未安装**
   ```bash
   pip install pytest allure-pytest pytest-html
   ```

2. **allure命令行工具未安装**
   - 安装Java 8+
   - 下载allure命令行工具
   - 添加到PATH环境变量

3. **测试用例不兼容**
   - 检查测试类继承是否正确
   - 确认导入的模块是否正确

### 调试技巧

1. **查看详细输出**：
   ```bash
   ez run tests/ --framework pytest -v
   ```

2. **检查pytest配置**：
   ```bash
   pytest --collect-only tests/
   ```

3. **验证框架功能**：
   ```bash
   python test_cmd_framework.py
   ```

## 最佳实践

1. **新项目建议使用pytest框架**，享受现代化的测试体验
2. **现有项目可以继续使用unittest框架**，保持稳定性
3. **逐步迁移**：可以在同一个项目中混合使用两种框架
4. **充分利用allure报告**：使用pytest框架时添加丰富的注解
5. **合理使用标记**：使用pytest.mark对测试进行分类

## 总结

ApiTestEz现在提供了灵活的框架选择功能，您可以根据项目需求和团队偏好选择合适的测试框架。无论选择哪种框架，都能享受到ApiTestEz提供的强大API测试能力。