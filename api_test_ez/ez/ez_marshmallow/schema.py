# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""
import typing
from marshmallow import Schema, ValidationError


class EzSchema(Schema):

    def __getattr__(self, item):
        """Return fields in `_declared_fields`, to dynamically modify field properties."""
        if item in self.declared_fields.keys():
            return self.declared_fields[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def handle_error(
        self, error: ValidationError, data: typing.Any, *, many: bool, **kwargs
    ):
        err_msg = f"Error Message: {error.messages}.\n" \
                  f"Raw Data: {error.data}"
        raise ValidationError(err_msg)
