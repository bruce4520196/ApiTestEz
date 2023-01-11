import os

import tablib

from api_test_ez.core.case import CaseFileNotFoundException
from api_test_ez.project import ENV_EZ_PROJECT_DIR


class CaseLoaderMiddleware(object):

    def __init__(self, configs):
        # ez configs
        self.configs = configs

    def load_test_data(self) -> list:
        raise NotImplementedError


class FileCaseLoaderMiddleware(CaseLoaderMiddleware):

    def load_test_data(self) -> list:
        data_filename = self.configs.get("case_filepath")
        if isinstance(data_filename, str):
            # 增加绝对路径和相对路径兼容
            if not os.path.exists(data_filename):
                data_filename = os.path.join(os.environ[ENV_EZ_PROJECT_DIR], data_filename)
                if not os.path.exists(data_filename):
                    raise CaseFileNotFoundException(
                        err=f'Case file "{data_filename}" not found from both relative and absolute paths.')
            with open(data_filename, 'rb') as f:
                data_set = tablib.Dataset().load(f.read())
                return data_set.dict
        else:
            raise CaseFileNotFoundException(
                err=f'Case filename type err: expect "str" but "{type(data_filename)}" found.')
