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

        if argv[0] not in EZ_SUPPORT_ACTION:
            print(f'EZ COMMAND ERROR: unknown action-word `{argv[0]}`. Support word must in {EZ_SUPPORT_ACTION}. See: \n')
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

        print(args)
        print(unknown_args)
        cases_path = args.cases_path
        if not cases_path:
            print('EZ COMMAND ERROR: `cases_path` not found. See: \n')
            ez_parser.print_help()
            return
        if not os.path.isfile(cases_path) or not os.path.isfile(cases_path):
            print('EZ COMMAND ERROR: `cases_path` is not a file or dir. See: \n')
            ez_parser.print_help()
            return
        project = Project(ez_file_path=cases_path if os.path.isdir(cases_path) else os.path.dirname(cases_path))

        if args.report_style:
            project.settings.set('REPORT_STYLE', args.report_style)

        if args.report_theme:
            project.settings.set('BR_REPORT_THEME', args.report_theme)

        if args.report_file:
            project.settings.set('REPORT_DIR', os.path.dirname(args.report_file))
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
            if args.report_style and project.report.report_dir:
                if args.report_style == 'br':
                    BRReporter(args.cases_path).run()
                    return
                elif args.report_style == 'html':
                    HtmlReporter(args.cases_path).run()
                    return
                else:
                    print(f'EZ COMMAND WARNING: `{args.report_style}` is not supported `report_style`, '
                          f'run tests as dry-run. See: \n')
            DryRun(args.cases_path).run()
            return

        elif args.action == 'dry-run':
            DryRun(args.cases_path).run()
            return

        else:
            print(f'EZ COMMAND ERROR: {args.action} is not supported `action`. See: \n')
            ez_parser.print_help()
            return


def main():
    EzCommand()


if __name__ == '__main__':
    main()
    # import argparse
    #
    # parser = argparse.ArgumentParser()
    # parser.add_argument("square", type=int,
    #                     help="display a square of a given number")
    # parser.add_argument("-v", "--verbose", action="store_true",
    #                     help="increase output verbosity")
    # args = parser.parse_args(['--verbose', '4'])
    # print(args)
