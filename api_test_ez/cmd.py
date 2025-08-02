# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 13:59
# @Author  : bruce
# @desc    :
"""
import argparse
import os
import pathlib
import sys
import subprocess
from unittest import TestProgram

from api_test_ez.core.report import BRReporter, HtmlReporter, DryRun
from api_test_ez.project import Project

EZ_SUPPORT_ACTION = [
    'run',
    'dry-run'
]


class EzCommand:

    def __init__(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        self.project = None
        self.process_args(argv)

    @staticmethod
    def parse_ez_parent():
        parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
        # action
        parser.add_argument('action',
                            choices=['run'],
                            help='Command action.'
                                 'For example: `ez run` <test_cases_path>')
        # run cases
        parser.add_argument('cases_path',
                            help='Run the next parameters as the test case.'
                                 'For example: ez run <test_cases_path>')
        return parser

    @staticmethod
    def parse_ez_args():
        # parser = argparse.ArgumentParser(add_help=False, parents=[parent])
        parser = argparse.ArgumentParser(add_help=True, exit_on_error=False)
        # action
        parser.add_argument('action',
                            choices=['run', 'dry-run'],
                            help='Command action.'
                                 'For example: `ez run`')
        # run cases
        parser.add_argument('cases_path',
                            help='Run the next parameters as the test case.'
                                 'For example: ez run <test_cases_path>')
        # version
        with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'rb') as f:
            version = f.read().decode('ascii').strip()
        parser.add_argument('-version', '--version',
                            action='version',
                            version=f'ApiTestEz version {version}',
                            help='Current EZ version.')
        # framework
        parser.add_argument('-fk', '--framework', dest='framework',
                            default='unittest',
                            choices=['unittest', 'pytest'],
                            help='`unittest` or `pytest`, how to EZ run cases, `unittest` as default.')
        # config
        parser.add_argument('-cfg', '--config', dest='config',
                            action="extend", nargs="+",
                            help='Set EZ config, priority `command`. '
                                 'For example: `-cfg host=127.0.0.1`, '
                                 'details: https://github.com/bruce4520196/ApiTestEz.')
        # config file
        parser.add_argument('-cfgf', '--config-file', dest='config_file',
                            help='Set EZ <config_file_path>, priority `command`. '
                                 'details: https://github.com/bruce4520196/ApiTestEz.')
        # report style
        parser.add_argument('-rs', '--report-style', dest='report_style',
                            default='br',
                            choices=['html', 'br'],
                            help='Report style. default `html`. '
                                 'support: `html` (ie: HtmlReporter), `br` (ie: BRReporter)')

        parser.add_argument('-t', '--tester', dest='tester',
                            default='Jenkins',
                            help='Tester name.')

        # beautiful report theme
        parser.add_argument('-rt', '--report-theme', dest='report_theme',
                            default='theme_default',
                            choices=['theme_default', 'theme_default', 'theme_cyan', 'theme_candy', 'theme_memories'],
                            help='Beautiful report theme. default `theme_default`. '
                                 'support: `theme_default`, `theme_default`,`theme_default`, '
                                 '`theme_cyan`, `theme_candy`, `theme_memories`')

        # report file
        parser.add_argument('-rf', '--report-file', dest='report_file',
                            help='Report file path.')
        return parser

    def process_args(self, argv):
        ez_parser = self.parse_ez_args()

        if len(argv) == 0:
            ez_parser.print_help()
            return

        if argv[0] == '-version' or argv[0] == '--version':
            ez_parser.parse_args()
            return

        if argv[0] not in EZ_SUPPORT_ACTION:
            print(
                f'EZ COMMAND ERROR: unknown action-word `{argv[0]}`. Support word must in {EZ_SUPPORT_ACTION}. See: \n')
            ez_parser.print_help()
            return

        if len(argv) == 1:
            print(f'EZ COMMAND ERROR: expect a <case-file-path> after the action-word `{argv[0]}`. See: \n')
            ez_parser.print_help()
            return

        if argv[1].startswith('-'):
            print(f'EZ COMMAND ERROR: expect a <case-file-path> after the action-word `{argv[0]}`, '
                  f'but `{argv[1]}` found. See: \n')
            ez_parser.print_help()
            return
        args, unknown_args = ez_parser.parse_known_args(argv)

        cases_path = args.cases_path
        if not cases_path:
            print('EZ COMMAND ERROR: `cases_path` not found. See: \n')
            ez_parser.print_help()
            return
        if not os.path.isfile(cases_path) and not os.path.isdir(cases_path):
            print('EZ COMMAND ERROR: `cases_path` is not a file or dir. See: \n')
            ez_parser.print_help()
            return
        project = Project(ez_file_path=cases_path if os.path.isdir(cases_path) else os.path.dirname(cases_path))

        if args.report_style:
            project.settings.set('REPORT_STYLE', args.report_style)

        if args.report_theme:
            project.settings.set('BR_REPORT_THEME', args.report_theme)

        if args.report_file:
            report_dir = os.path.dirname(args.report_file) \
                if os.path.dirname(args.report_file) \
                else os.path.dirname(__file__)
            project.settings.set('REPORT_DIR', report_dir)
            project.settings.set('REPORT_FILE_NAME', os.path.basename(args.report_file))

        if args.config_file:
            if os.path.exists(args.config_file):
                print(f'EZ COMMAND ERROR: can not find ez-config-file `{args.config_file}`.')
                ez_parser.print_help()
            else:
                project.configs.set_config(args.config_file, priority='command')

        if args.config:
            for cfg in args.config:
                if '=' not in cfg:
                    print('EZ COMMAND ERROR: config format error, For example: `-cfg host=127.0.0.1`. See: \n')
                    ez_parser.print_help()
                    return
                project.configs.set(*cfg.split('=', 1), priority='command')

        if args.action == 'run':
            # 根据框架参数选择运行方式
            if args.framework == 'pytest':
                self._run_pytest(args, project)
                return
            elif args.framework == 'unittest':
                self._run_unittest(args, project)
                return
            else:
                print(f'EZ COMMAND ERROR: unsupported framework `{args.framework}`. See: \n')
                ez_parser.print_help()
                return

        elif args.action == 'dry-run':
            DryRun(args.cases_path).run()
            return

        else:
            print(f'EZ COMMAND ERROR: {args.action} is not supported `action`. See: \n')
            ez_parser.print_help()
            return

    def _run_unittest(self, args, project):
        """运行unittest框架测试"""
        if project.report.report_dir:
            if args.report_style == 'br':
                BRReporter(args.cases_path, tester=args.tester).run()
                return
            elif args.report_style == 'html':
                HtmlReporter(args.cases_path, tester=args.tester).run()
                return
            else:
                print(f'EZ COMMAND WARNING: `{args.report_style}` is not supported `report_style`, '
                      f'run tests as dry-run. See: \n')
        else:
            print(f'EZ COMMAND WARNING: `report_dir` does not set, run tests as dry-run.\n')
        DryRun(args.cases_path).run()

    def _run_pytest(self, args, project):
        """运行pytest框架测试"""
        try:
            import subprocess
            import sys
            
            # 检查pytest是否可用
            try:
                subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print('❌ 错误: pytest未安装，请运行: pip install pytest')
                sys.exit(1)
            
            # 构建pytest命令
            pytest_cmd = [sys.executable, '-m', 'pytest']
            
            # 添加测试路径
            pytest_cmd.append(args.cases_path)
            
            # 添加详细输出
            pytest_cmd.append('-v')
            
            # 检查并添加可用的插件参数
            available_plugins = self._check_pytest_plugins()
            
            # 设置报告目录
            if project.report.report_dir:
                if not os.path.exists(project.report.report_dir):
                    os.makedirs(project.report.report_dir)
                
                # 添加allure报告（如果插件可用）
                if available_plugins.get('allure'):
                    allure_results_dir = os.path.join(project.report.report_dir, 'allure-results')
                    pytest_cmd.extend(['--alluredir', allure_results_dir])
                    print(f'✅ 将生成Allure报告到: {allure_results_dir}')
                
                # 添加HTML报告（如果插件可用）
                if available_plugins.get('html'):
                    html_report_path = os.path.join(project.report.report_dir, 'pytest_report.html')
                    pytest_cmd.extend(['--html', html_report_path, '--self-contained-html'])
                    print(f'✅ 将生成HTML报告到: {html_report_path}')
                
                if not available_plugins.get('allure') and not available_plugins.get('html'):
                    print('⚠️  未安装报告插件，将只生成基础测试输出')
                    print('   安装命令: pip install allure-pytest pytest-html')
                
                print(f'Pytest报告将生成到: {project.report.report_dir}')
            
            print(f'执行命令: {" ".join(pytest_cmd)}')
            
            # 运行pytest
            result = subprocess.run(pytest_cmd, cwd=os.getcwd())
            
            if result.returncode == 0:
                print('✅ Pytest测试执行成功')
                
                # 尝试生成allure报告
                if project.report.report_dir and available_plugins.get('allure'):
                    self._generate_allure_report(project.report.report_dir)
            else:
                print(f'❌ Pytest测试执行失败，退出码: {result.returncode}')
                
        except ImportError:
            print('❌ 错误: pytest未安装，请运行: pip install pytest')
            sys.exit(1)
        except Exception as e:
            print(f'❌ 运行pytest时出错: {e}')
            sys.exit(1)

    def _check_pytest_plugins(self):
        """检查pytest插件是否可用"""
        import subprocess
        import sys
        
        plugins = {
            'allure': False,
            'html': False
        }
        
        try:
            # 检查allure-pytest插件
            result = subprocess.run([sys.executable, '-m', 'pytest', '--help'], 
                                  capture_output=True, text=True)
            if '--alluredir' in result.stdout:
                plugins['allure'] = True
            if '--html' in result.stdout:
                plugins['html'] = True
        except:
            pass
        
        return plugins

    def _generate_allure_report(self, report_dir):
        """生成allure报告"""
        try:
            import subprocess
            
            allure_results_dir = os.path.join(report_dir, 'allure-results')
            allure_report_dir = os.path.join(report_dir, 'allure-report')
            
            if os.path.exists(allure_results_dir):
                # 检查allure命令是否可用
                subprocess.run(['allure', '--version'], check=True, capture_output=True)
                
                # 生成allure报告
                subprocess.run([
                    'allure', 'generate', allure_results_dir,
                    '-o', allure_report_dir, '--clean'
                ], check=True, capture_output=True)
                
                print(f'✅ Allure报告已生成: {allure_report_dir}/index.html')
                
        except subprocess.CalledProcessError:
            print('⚠️  Allure命令行工具未安装，跳过allure报告生成')
            print('   如需使用allure报告，请安装allure命令行工具')
        except Exception as e:
            print(f'⚠️  生成allure报告时出错: {e}')


def main():
    EzCommand()


if __name__ == '__main__':
    main()
