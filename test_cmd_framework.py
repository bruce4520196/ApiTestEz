#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试命令行工具框架选择功能
"""
import os
import sys
import subprocess
import tempfile


def create_test_files():
    """创建测试文件"""
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix='ez_test_')
    
    # 创建unittest测试文件
    unittest_test = '''# -*- coding: utf-8 -*-
import unittest
from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame

class TestUnittestExample(UnitHttpFrame):
    def test_unittest_example(self):
        """unittest框架测试示例"""
        self.assertTrue(True)
        print("✅ unittest测试执行成功")
'''
    
    # 创建pytest测试文件
    pytest_test = '''# -*- coding: utf-8 -*-
import pytest
import allure
from api_test_ez.core.case.frame.frame_pytest import BaseCase

@allure.feature("命令行工具测试")
class TestPytestExample(BaseCase):
    
    @allure.story("pytest框架测试")
    @pytest.mark.api
    def test_pytest_example(self):
        """pytest框架测试示例"""
        assert True
        print("✅ pytest测试执行成功")
'''
    
    # 写入测试文件
    unittest_file = os.path.join(test_dir, 'test_unittest_example.py')
    pytest_file = os.path.join(test_dir, 'test_pytest_example.py')
    
    with open(unittest_file, 'w', encoding='utf-8') as f:
        f.write(unittest_test)
    
    with open(pytest_file, 'w', encoding='utf-8') as f:
        f.write(pytest_test)
    
    return test_dir, unittest_file, pytest_file


def test_unittest_framework(test_file):
    """测试unittest框架"""
    print("\n🧪 测试unittest框架...")
    
    cmd = [
        sys.executable, '-m', 'api_test_ez.cmd',
        'run', test_file,
        '--framework', 'unittest'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ unittest框架测试成功")
            return True
        else:
            print(f"❌ unittest框架测试失败")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ unittest框架测试超时")
        return False
    except Exception as e:
        print(f"❌ unittest框架测试异常: {e}")
        return False


def test_pytest_framework(test_file):
    """测试pytest框架"""
    print("\n🧪 测试pytest框架...")
    
    cmd = [
        sys.executable, '-m', 'api_test_ez.cmd',
        'run', test_file,
        '--framework', 'pytest'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ pytest框架测试成功")
            return True
        else:
            print(f"❌ pytest框架测试失败")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ pytest框架测试超时")
        return False
    except Exception as e:
        print(f"❌ pytest框架测试异常: {e}")
        return False


def test_help_command():
    """测试帮助命令"""
    print("\n📖 测试帮助命令...")
    
    cmd = [sys.executable, '-m', 'api_test_ez.cmd', '--help']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if 'framework' in result.stdout and 'unittest' in result.stdout and 'pytest' in result.stdout:
            print("✅ 帮助信息包含框架选项")
            return True
        else:
            print("❌ 帮助信息缺少框架选项")
            print(f"stdout: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 测试帮助命令异常: {e}")
        return False


def cleanup_test_files(test_dir):
    """清理测试文件"""
    import shutil
    try:
        shutil.rmtree(test_dir)
        print(f"✅ 清理测试目录: {test_dir}")
    except Exception as e:
        print(f"⚠️  清理测试目录失败: {e}")


def main():
    """主函数"""
    print("🔧 ApiTestEz命令行工具框架选择功能测试")
    print("=" * 60)
    
    # 创建测试文件
    test_dir, unittest_file, pytest_file = create_test_files()
    print(f"📁 创建测试目录: {test_dir}")
    
    try:
        # 测试结果
        results = {}
        
        # 测试帮助命令
        results['帮助命令'] = test_help_command()
        
        # 测试unittest框架
        results['unittest框架'] = test_unittest_framework(unittest_file)
        
        # 测试pytest框架
        results['pytest框架'] = test_pytest_framework(pytest_file)
        
        # 显示测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        
        print(f"\n总计: {passed_tests}/{total_tests} 项测试通过")
        
        if passed_tests == total_tests:
            print("\n🎉 所有测试通过！命令行工具框架选择功能正常工作")
        else:
            print(f"\n⚠️  有 {total_tests - passed_tests} 项测试失败")
            
    finally:
        # 清理测试文件
        cleanup_test_files(test_dir)


if __name__ == "__main__":
    main()