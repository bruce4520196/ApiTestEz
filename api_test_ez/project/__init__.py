# -*- coding: utf-8 -*-
"""
# @Time    : 2022/3/5 14:25
# @Author  : bruce
# @desc    :
"""
import sys

from api_test_ez.ez import get_config, Log
from api_test_ez.ez.decorator import singleton
from api_test_ez.project.configs import Configs
from api_test_ez.project.settings import Settings
import os

ENV_EZ_PROJECT_DIR = 'EZ_PROJECT_DIR'
ENV_EZ_SETTINGS_MODULE = 'EZ_SETTINGS_MODULE'


def closest_file(file_name, path='.', prev_path=None):
    """Return the path to the closest project.cfg file by traversing the current
    directory and its parents
    """
    if path == prev_path:
        return ''
    path = os.path.abspath(path)
    cfg_file = os.path.join(path, file_name)
    if os.path.exists(cfg_file):
        return cfg_file
    return closest_file(file_name, os.path.dirname(path), path)


def search_file(file_name: str, path: str = '.', prev_path: str = None, search_result=None):
    """Return the path list to the case.cfg file by traversing the current
    directory and its parents
    """
    if search_result is None:
        search_result = []
    if path == prev_path:
        return search_result
    path = os.path.abspath(path)
    cfg_file = os.path.join(path, file_name)
    if os.path.exists(cfg_file):
        search_result.append(cfg_file)
    return search_file(file_name, path=os.path.dirname(path), prev_path=path, search_result=search_result)


def init_project(project='default'):
    # project config
    ez_cfg_name = 'project.cfg'
    project_cfg_path = closest_file(ez_cfg_name)
    cfg = get_config(project_cfg_path)
    if cfg.has_option('settings', project):
        project_settings_path = cfg.get('settings', project)
        os.environ[ENV_EZ_SETTINGS_MODULE] = project_settings_path
        os.environ[ENV_EZ_PROJECT_DIR] = os.path.abspath(os.path.dirname(project_cfg_path))
        sys.path.append(os.environ[ENV_EZ_PROJECT_DIR])


def get_ez_settings():
    if ENV_EZ_SETTINGS_MODULE not in os.environ:
        init_project()

    _settings = Settings()
    settings_module_path = os.environ.get(ENV_EZ_SETTINGS_MODULE)
    if settings_module_path:
        _settings.set_module(settings_module_path)

    return _settings


def get_ez_config(ez_file_path):
    # ez case config
    ez_cfg_name = 'ez.cfg'
    ez_cfg_filelist = search_file(ez_cfg_name, path=ez_file_path)

    _configs = Configs()
    support_file_config_priority = ['package', 'module', 'project']
    for ez_cfg_file in ez_cfg_filelist:
        if len(support_file_config_priority) <= 0:
            break
        _configs.set_config(ez_cfg_file, support_file_config_priority.pop(0))

    return _configs


def get_ez_logger(project_settings: Settings, logger_name=None):
    """
    :param project_settings:
    :param logger_name:
    :return:
    """
    console_format = project_settings.get('CONSOLE_LOG_FORMAT')
    console_log_level = project_settings.get('CONSOLE_LOG_LEVEL')

    file_format = project_settings.get('FILE_LOG_FORMAT')
    file_log_level = project_settings.get('FILE_LOG_LEVEL')
    file_log_path = project_settings.get('FILE_LOG_PATH')

    log = Log(logger_name=logger_name)

    if console_format:
        log.console_format = console_format

    if console_log_level:
        log.console_log_level = console_log_level

    if file_format:
        log.file_format = file_format

    if file_log_level:
        log.file_log_level = file_log_level

    logger = log.init_logger(file_log_path)

    return logger


class ReportConfig:

    def __init__(self, project_settings: Settings):
        self._report_dir = project_settings.get("REPORT_DIR")
        self._report_file_name = project_settings.get("REPORT_FILE_NAME")

        self._report_file_path = os.path.join(self._report_dir, self._report_file_name) if self._report_dir else None
        self._report_title = project_settings.get("REPORT_TITLE")
        self._report_desc = project_settings.get("REPORT_DESC")
        self._report_theme = project_settings.get("BR_REPORT_THEME")

    @property
    def report_file_path(self):
        return self._report_file_path

    @property
    def report_title(self):
        return self._report_title

    @property
    def report_desc(self):
        return self._report_desc

    @property
    def report_dir(self):
        return self._report_dir

    @property
    def report_file_name(self):
        return self._report_file_name

    @property
    def theme(self):
        return self._report_theme


@singleton
class Project:
    """Ez initialize"""
    def __init__(self, ez_file_path, env_name=None):
        self.env_name = env_name if env_name else os.path.dirname(ez_file_path)
        self._settings = get_ez_settings()
        self._configs = get_ez_config(ez_file_path)
        self._logger = get_ez_logger(self._settings, self.env_name)
        # self._report = ReportConfig(self._settings)

    @property
    def settings(self):
        return self._settings

    @property
    def configs(self):
        return self._configs

    @property
    def logger(self):
        return self._logger

    @property
    def report(self):
        # We should always get the newest report config.
        return ReportConfig(self._settings)
