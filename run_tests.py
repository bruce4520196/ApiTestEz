#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
支持多种测试运行模式和报告生成
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, shell=True):
    """执行命令"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    print(result.stdout)
    return True


def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    return run_command("pip install -r requirements.txt")


def run_tests(test_path="tests", markers=None, parallel=False, verbose=True):
    """运行测试"""
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if markers:
        cmd.extend(["-m", markers])
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    # 添加allure结果目录
    cmd.extend(["--alluredir", "reports/allure-results"])
    
    # 添加HTML报告
    cmd.extend(["--html", "reports/html/report.html", "--self-contained-html"])
    
    # 添加测试路径
    cmd.append(test_path)
    
    print("正在运行测试...")
    return run_command(" ".join(cmd))


def generate_allure_report():
    """生成allure报告"""
    print("正在生成allure报告...")
    
    # 检查allure是否安装
    if not run_command("allure --version"):
        print("Allure未安装，请先安装allure命令行工具")
        print("安装方法:")
        print("1. 下载并安装Java 8+")
        print("2. 下载allure命令行工具: https://github.com/allure-framework/allure2/releases")
        print("3. 将allure/bin目录添加到PATH环境变量")
        return False
    
    # 生成报告
    return run_command("allure generate reports/allure-results -o reports/allure-report --clean")


def serve_allure_report():
    """启动allure报告服务"""
    print("正在启动allure报告服务...")
    return run_command("allure serve reports/allure-results")


def clean_reports():
    """清理报告目录"""
    print("正在清理报告目录...")
    import shutil
    
    dirs_to_clean = [
        "reports/allure-results",
        "reports/allure-report", 
        "reports/html",
        "reports/logs"
    ]
    
    for dir_path in dirs_to_clean:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"已清理: {dir_path}")
    
    # 重新创建目录
    for dir_path in dirs_to_clean:
        os.makedirs(dir_path, exist_ok=True)
        print(f"已创建: {dir_path}")


def main():
    parser = argparse.ArgumentParser(description="ApiTestEz测试运行工具")
    parser.add_argument("--install", action="store_true", help="安装依赖")
    parser.add_argument("--clean", action="store_true", help="清理报告目录")
    parser.add_argument("--test", default="tests", help="测试路径 (默认: tests)")
    parser.add_argument("--markers", help="测试标记过滤 (例如: smoke, api, regression)")
    parser.add_argument("--parallel", action="store_true", help="并行运行测试")
    parser.add_argument("--no-allure", action="store_true", help="不生成allure报告")
    parser.add_argument("--serve", action="store_true", help="启动allure报告服务")
    parser.add_argument("--report-only", action="store_true", help="仅生成报告，不运行测试")
    
    args = parser.parse_args()
    
    # 安装依赖
    if args.install:
        if not install_dependencies():
            sys.exit(1)
        return
    
    # 清理报告
    if args.clean:
        clean_reports()
        return
    
    # 仅生成报告
    if args.report_only:
        if not generate_allure_report():
            sys.exit(1)
        return
    
    # 启动报告服务
    if args.serve:
        if not serve_allure_report():
            sys.exit(1)
        return
    
    # 运行测试
    success = run_tests(
        test_path=args.test,
        markers=args.markers,
        parallel=args.parallel
    )
    
    if not success:
        print("测试运行失败")
        sys.exit(1)
    
    # 生成allure报告
    if not args.no_allure:
        if not generate_allure_report():
            print("allure报告生成失败，但测试已完成")
        else:
            print("测试完成，报告已生成")
            print("HTML报告: reports/html/report.html")
            print("Allure报告: reports/allure-report/index.html")
            print("运行 'python run_tests.py --serve' 启动allure报告服务")


if __name__ == "__main__":
    main()