#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ApiTestEz Pytest框架快速入门脚本
帮助用户快速开始使用Pytest进行API测试
"""
import os
import sys
import subprocess
import json


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    ApiTestEz Pytest框架                      ║
║                      快速入门向导                            ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("❌ Python版本过低，需要Python 3.6或更高版本")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False


def create_sample_test():
    """创建示例测试文件"""
    print("\n📝 创建示例测试文件...")
    
    sample_test = '''# -*- coding: utf-8 -*-
"""
我的第一个API测试
"""
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase


@allure.feature("我的第一个API测试")
class TestMyFirstAPI(BaseCase):
    """我的第一个API测试类"""
    
    def setup_class(self):
        """测试类初始化"""
        self.base_url = "https://jsonplaceholder.typicode.com"
    
    @allure.story("获取用户信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    @pytest.mark.smoke
    def test_get_user_info(self):
        """测试获取用户信息接口"""
        
        with allure.step("设置请求参数"):
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
        
        with allure.step("执行HTTP请求"):
            response = self.do_request()
        
        with allure.step("验证响应结果"):
            # 验证状态码
            self.assert_status_code(200, "应该返回200状态码")
            
            # 验证响应内容
            self.assert_json_contains({
                "id": 1,
                "name": "Leanne Graham"
            }, "响应应该包含正确的用户信息")
            
            # 验证响应时间
            self.assert_response_time(3000, "响应时间应该小于3秒")
    
    @allure.story("创建新用户")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_create_user(self):
        """测试创建用户接口"""
        
        with allure.step("准备用户数据"):
            user_data = {
                "name": "新用户",
                "username": "newuser",
                "email": "newuser@example.com"
            }
        
        with allure.step("发送创建用户请求"):
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
            
            response = self.do_request()
        
        with allure.step("验证创建结果"):
            self.assert_status_code(201, "创建用户应该返回201状态码")
            
            response_data = response.json()
            assert "id" in response_data, "响应应该包含用户ID"
            assert response_data["name"] == user_data["name"], "用户名应该匹配"
'''
    
    os.makedirs("my_tests", exist_ok=True)
    with open("my_tests/test_my_first_api.py", "w", encoding="utf-8") as f:
        f.write(sample_test)
    
    print("✅ 示例测试文件已创建: my_tests/test_my_first_api.py")


def run_sample_test():
    """运行示例测试"""
    print("\n🚀 运行示例测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "my_tests/test_my_first_api.py",
            "-v",
            "--alluredir=reports/allure-results",
            "--html=reports/html/my_first_report.html",
            "--self-contained-html"
        ], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 测试运行成功！")
            print("\n📊 测试报告:")
            print("   - HTML报告: reports/html/my_first_report.html")
            print("   - Allure结果: reports/allure-results/")
            return True
        else:
            print("❌ 测试运行失败")
            print("错误信息:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


def generate_allure_report():
    """生成Allure报告"""
    print("\n📈 生成Allure报告...")
    try:
        # 检查allure是否可用
        subprocess.run(["allure", "--version"], check=True, capture_output=True)
        
        # 生成报告
        subprocess.run([
            "allure", "generate", "reports/allure-results", 
            "-o", "reports/allure-report", "--clean"
        ], check=True, capture_output=True)
        
        print("✅ Allure报告生成成功: reports/allure-report/index.html")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Allure命令行工具未安装，跳过Allure报告生成")
        print("   如需使用Allure报告，请安装Allure命令行工具:")
        print("   1. 安装Java 8+")
        print("   2. 下载Allure: https://github.com/allure-framework/allure2/releases")
        print("   3. 将allure/bin添加到PATH环境变量")
        return False
    except Exception as e:
        print(f"❌ 生成Allure报告时出错: {e}")
        return False


def show_next_steps():
    """显示后续步骤"""
    print("\n🎉 恭喜！您已成功完成ApiTestEz Pytest框架的快速入门！")
    print("\n📚 后续步骤:")
    print("1. 查看生成的测试报告了解测试结果")
    print("2. 阅读 README_PYTEST.md 了解更多功能")
    print("3. 查看 tests/ 目录下的示例文件学习高级用法")
    print("4. 根据您的API创建自己的测试用例")
    
    print("\n🔧 常用命令:")
    print("   运行所有测试:     python run_tests.py")
    print("   运行指定标记:     python run_tests.py --markers smoke")
    print("   并行运行测试:     python run_tests.py --parallel")
    print("   生成Allure报告:   python run_tests.py --report-only")
    print("   启动报告服务:     python run_tests.py --serve")
    
    print("\n📖 学习资源:")
    print("   - 项目文档: README_PYTEST.md")
    print("   - 示例测试: tests/test_api_example.py")
    print("   - 数据驱动: tests/test_data_driven.py")
    print("   - 高级功能: tests/test_advanced_features.py")


def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        return
    
    # 创建示例测试
    create_sample_test()
    
    # 运行示例测试
    if not run_sample_test():
        print("❌ 示例测试运行失败，请检查环境配置")
        return
    
    # 生成Allure报告
    generate_allure_report()
    
    # 显示后续步骤
    show_next_steps()


if __name__ == "__main__":
    main()