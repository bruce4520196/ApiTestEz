# -*- coding: utf-8 -*-
"""
简单的pytest测试用例
"""
import pytest

def test_simple_pytest():
    """简单的pytest测试"""
    print("✅ pytest框架测试执行成功")
    assert True
    
def test_another_pytest():
    """另一个pytest测试"""
    print("✅ 另一个pytest测试执行成功")
    assert 1 + 1 == 2
    
def test_marked_pytest():
    """带标记的pytest测试"""
    print("✅ 带标记的pytest测试执行成功")
    assert "hello" in "hello world"
