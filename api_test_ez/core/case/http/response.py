# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/12 17:54
# @Author  : bruce
# @desc    :
"""
import logging
from json import JSONDecodeError

from requests import Response

from api_test_ez.ez.decorator.jsonbean import json_bean
from api_test_ez.ez.orm.errors import ValidationError
from api_test_ez.ez.orm.models import ValidatorModel
from marshmallow import Schema


class EzResponse(Response):

    __slots__ = ("owner", "response")

    def __init__(self, response: Response = None):
        super().__init__()
        self.response = response

    def __getattribute__(self, item):
        if item not in ("owner", "response") and not item.startswith('__') and hasattr(self.response, item):
            return self.response.__getattribute__(item)
        else:
            return super(EzResponse, self).__getattribute__(item)

    def set(self, response: Response):
        self.response = response

    @json_bean
    def bean(self):
        return self.json()

    def pair(self, model: ValidatorModel, full_repr=False):
        validate_result = model.validate(self.response.json(), full_repr)
        if 'ValidationError' in str(validate_result):
            raise ValidationError(f'[{self.owner} {validate_result}]')

    def validate(self, schema: Schema):
        """Validate from marshmallow."""
        return schema.load(self.response.json())

    def __str__(self):
        if self.response:
            return f"<{self.__class__.__name__}> {self.owner}:\n" \
                   f"{self.response.text!r}"
        else:
            return f"<{self.__class__.__name__}> {self.owner}: response is None, " \
                   f"maybe you didn't send the request?"

    __repr__ = __str__
