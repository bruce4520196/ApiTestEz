# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""
import typing
from marshmallow import Schema, ValidationError


class EzSchema(Schema):
    """Rewrite error message."""

    def handle_error(
        self, error: ValidationError, data: typing.Any, *, many: bool, **kwargs
    ):
        err_msg = f"Error Message: {error.messages}.\n" \
                  f"Raw Data: {error.data}"
        raise ValidationError(err_msg)
