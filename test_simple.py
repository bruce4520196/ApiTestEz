# -*- coding: utf-8 -*-
"""
简单测试用例，用于验证框架选择功能
"""
import unittest
from api_test_ez.core.case.frame.frame_unittest import UnitHttpFrame

class TestSimpleExample(UnitHttpFrame):
    
    def test_simple_unittest(self):
        """简单的unittest测试"""
        print("✅ unittest框架测试执行成功")
        self.assertTrue(True)
        
    def test_another_unittest(self):
        """另一个unittest测试"""
        print("✅ 另一个unittest测试执行成功")
        self.assertEqual(1 + 1, 2)