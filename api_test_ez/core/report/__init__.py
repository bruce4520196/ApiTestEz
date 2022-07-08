# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""
import os
from abc import ABC, abstractmethod

from BeautifulReport import BeautifulReport

from api_test_ez.libs import HTMLTestRunner
from api_test_ez.project import Project
from unittest.loader import defaultTestLoader


class Reporter(ABC):

    def __init__(self, case_path, report_title=None, report_desc=None, *args, **kwargs):
        self.case_file_name = None
        if os.path.isdir(case_path):
            self.case_file_dir = case_path
        else:
            self.case_file_dir = os.path.dirname(case_path)
            self.case_file_name = os.path.basename(case_path)

        project = Project(ez_file_path=self.case_file_dir)
        self.settings = project.settings
        # log
        self.logger = project.logger
        # report file
        self.report = project.report
        self.report_dir = self.report.report_dir
        self.report_file_name = self.report.report_file_name
        self.report_file_path = project.report.report_file_path
        self.report_title = report_title if report_title else project.report.report_title
        self.report_desc = report_desc if report_desc else project.report.report_desc

    def load_tests(self):
        """Load tests from a dir. It is same as the `load_tests` protocol in `unittest`."""
        if self.case_file_name:
            print(self.case_file_name)
            return defaultTestLoader.discover(self.case_file_dir, pattern=f'{self.case_file_name}')
        else:
            return defaultTestLoader.discover(self.case_file_dir, pattern='*.py')

    @abstractmethod
    def run(self):
        pass

    def send(self):
        pass


class HtmlReporter(Reporter):
    """HTMLTestRunner"""

    def run(self):
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        fp = open(self.report_file_path, 'wb')
        try:
            suit = self.load_tests()
            self.logger.info("********TEST BEGIN********")
            runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=f'{self.report_title}',
                                                   description=f'API:\n{self.report_desc}')
            runner.run(suit)
        except IOError as ex:
            self.logger.error(str(ex))
        finally:
            self.logger.info("********TEST END*********")
            fp.close()


class BRReporter(Reporter):
    """BeautifulReport"""

    def __init__(self, case_path, report_theme=None,  *args, **kwargs):
        super().__init__(case_path, *args, **kwargs)
        self.report_theme = report_theme if report_theme else self.report.theme

    def run(self):
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        suit = self.load_tests()
        result = BeautifulReport(suit)
        result.report(
            filename=self.report_file_name,
            description=self.report_title,
            report_dir=self.report_dir,
            theme=self.report_theme
        )
