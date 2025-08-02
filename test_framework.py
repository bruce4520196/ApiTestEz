#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
框架功能验证脚本
快速验证ApiTestEz Pytest框架是否正常工作
"""
import sys
import os
import importlib.util


def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试pytest导入
        import pytest
        print(f"✅ pytest版本: {pytest.__version__}")
        
        # 测试allure导入
        import allure
        print("✅ allure-pytest导入成功")
        
        # 测试ApiTestEz核心模块
        from api_test_ez.core.case.frame.frame_pytest import BaseCase, PytestHttpFrame
        print("✅ ApiTestEz Pytest框架导入成功")
        
        # 测试工具类
        from api_test_ez.core.case.frame.pytest_utils import TestDataHelper, AllureHelper
        print("✅ Pytest工具类导入成功")
        
        # 测试HTTP模块
        from api_test_ez.ez import Http
        print("✅ HTTP客户端导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        # 测试BaseCase实例化
        from api_test_ez.core.case.frame.frame_pytest import BaseCase
        test_case = BaseCase()
        test_case.init_request("test_method")
        print("✅ BaseCase实例化成功")
        
        # 测试工具类功能
        from api_test_ez.core.case.frame.pytest_utils import TestDataHelper
        random_email = TestDataHelper.generate_random_email()
        random_phone = TestDataHelper.generate_random_phone()
        test_user = TestDataHelper.generate_test_user()
        
        print(f"✅ 随机数据生成成功:")
        print(f"   邮箱: {random_email}")
        print(f"   手机: {random_phone}")
        print(f"   用户: {test_user['name']}")
        
        # 测试HTTP客户端
        from api_test_ez.ez import Http
        http_client = Http()
        print("✅ HTTP客户端创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


def test_configuration_files():
    """测试配置文件"""
    print("\n📋 检查配置文件...")
    
    config_files = [
        ("pytest.ini", "Pytest配置文件"),
        ("allure.properties", "Allure配置文件"),
        ("requirements.txt", "依赖配置文件"),
        ("tests/conftest.py", "Pytest全局配置"),
        ("README_PYTEST.md", "使用文档")
    ]
    
    all_exist = True
    for file_path, description in config_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}缺失: {file_path}")
            all_exist = False
    
    return all_exist


def test_directory_structure():
    """测试目录结构"""
    print("\n📁 检查目录结构...")
    
    required_dirs = [
        ("tests", "测试目录"),
        ("tests/data", "测试数据目录"),
        ("api_test_ez/core/case/frame", "框架核心目录"),
        ("reports", "报告目录")
    ]
    
    all_exist = True
    for dir_path, description in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {description}: {dir_path}")
        else:
            print(f"⚠️  {description}不存在，将自动创建: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    return all_exist


def test_sample_files():
    """测试示例文件"""
    print("\n📄 检查示例文件...")
    
    sample_files = [
        ("tests/test_api_example.py", "API测试示例"),
        ("tests/test_data_driven.py", "数据驱动测试示例"),
        ("tests/test_advanced_features.py", "高级功能测试示例"),
        ("tests/data/user_test_data.json", "测试数据文件")
    ]
    
    all_exist = True
    for file_path, description in sample_files:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}缺失: {file_path}")
            all_exist = False
    
    return all_exist


def run_quick_test():
    """运行快速测试"""
    print("\n🚀 运行快速功能测试...")
    
    try:
        # 创建一个简单的测试用例
        from api_test_ez.core.case.frame.frame_pytest import BaseCase
        from api_test_ez.core.case.frame.pytest_utils import TestDataHelper
        
        class QuickTest(BaseCase):
            def test_quick_functionality(self):
                # 测试请求设置
                self._request.set({
                    "url": "https://httpbin.org/get",
                    "method": "GET",
                    "headers": {"Content-Type": "application/json"},
                    "timeout": 10,
                    "cookies": None,
                    "retry": 3,
                    "proxies": None,
                    "allow_redirects": True,
                    "verify": True
                })
                
                # 测试数据生成
                test_data = TestDataHelper.generate_test_user("快速测试")
                
                return True
        
        # 实例化并运行测试
        quick_test = QuickTest()
        quick_test.init_request("test_quick_functionality")
        result = quick_test.test_quick_functionality()
        
        print("✅ 快速功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 快速功能测试失败: {e}")
        return False


def show_summary(results):
    """显示测试总结"""
    print("\n" + "="*60)
    print("📊 框架验证总结")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 项测试通过")
    
    if passed_tests == total_tests:
        print("\n🎉 恭喜！ApiTestEz Pytest框架验证完全通过！")
        print("您可以开始使用以下命令:")
        print("   python quick_start.py        # 快速入门")
        print("   python run_tests.py          # 运行测试")
        print("   pytest tests/ -v             # 直接使用pytest")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 项测试失败，请检查环境配置")
        print("建议:")
        print("1. 运行 pip install -r requirements.txt 安装依赖")
        print("2. 检查Python版本是否为3.6+")
        print("3. 确保所有必需文件都存在")


def main():
    """主函数"""
    print("🔧 ApiTestEz Pytest框架验证工具")
    print("="*60)
    
    # 运行各项测试
    test_results = {
        "模块导入测试": test_imports(),
        "基本功能测试": test_basic_functionality(),
        "配置文件检查": test_configuration_files(),
        "目录结构检查": test_directory_structure(),
        "示例文件检查": test_sample_files(),
        "快速功能测试": run_quick_test()
    }
    
    # 显示总结
    show_summary(test_results)


if __name__ == "__main__":
    main()