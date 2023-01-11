import os

import tablib

from api_test_ez.core.case import CaseFileNotFoundException
from api_test_ez.project import ENV_EZ_PROJECT_DIR


class CaseLoaderMiddleware(object):

    def load_test_data(self) -> list:
        raise NotImplementedError


class FileCaseLoaderMiddleware(object):

    def __init__(self, data_filename):
        self.data_filename = data_filename

    def load_test_data(self) -> list:
        if isinstance(self.data_filename, str):
            # 增加绝对路径和相对路径兼容
            if not os.path.exists(self.data_filename):
                self.data_filename = os.path.join(os.environ[ENV_EZ_PROJECT_DIR], self.data_filename)
                if not os.path.exists(self.data_filename):
                    raise CaseFileNotFoundException(
                        err=f'Case file "{self.data_filename}" not found from both relative and absolute paths.')
            with open(self.data_filename, 'rb') as f:
                data_set = tablib.Dataset().load(f.read())
                return data_set.dict
        else:
            raise CaseFileNotFoundException(
                err=f'Case filename type err: expect "str" but "{type(self.data_filename)}" found.')
