# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/11 13:56
# @Author  : bruce
# @desc    :
"""
from collections import defaultdict


class ValidationError(AssertionError):
    """Validation exception.

    May represent an error validating a field or a
    Model containing fields with validation errors.

    :ivar errors: A dictionary of errors for fields within this
        document or list, or None if the error is for an
        individual field.
    """

    errors = {}
    field_name = None
    _message = None

    def __init__(self, message="", **kwargs):
        super().__init__(message)
        self.errors = kwargs.get("errors", {})
        self.field_name = kwargs.get("field_name")
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}({self.message},)"

    __repr__ = __str__

    def __getattribute__(self, name):
        message = super().__getattribute__(name)
        if name == "message":
            if self.field_name:
                message = "%s" % message
            if self.errors:
                message = f"{message}({self._format_errors()})"
        return message

    def _get_message(self):
        return self._message

    def _set_message(self, message):
        self._message = message

    message = property(_get_message, _set_message)

    def to_dict(self):
        """Returns a dictionary of all errors within a document

        Keys are field names or list indices and values are the
        validation error messages, or a nested dictionary of
        errors for an embedded document or list.
        """

        def build_dict(source):
            errors_dict = {}
            if isinstance(source, dict):
                for field_name, error in source.items():
                    errors_dict[field_name] = build_dict(error)
            elif isinstance(source, ValidationError) and source.errors:
                return build_dict(source.errors)
            else:
                return str(source)

            return errors_dict

        if not self.errors:
            return {}

        return build_dict(self.errors)

    def _format_errors(self):
        """Returns a string listing all errors within a document"""

        def generate_key(value, prefix=""):
            if isinstance(value, list):
                value = " ".join([generate_key(k) for k in value])
            elif isinstance(value, dict):
                value = " ".join([generate_key(v, k) for k, v in value.items()])

            results = f"{prefix}.{value}" if prefix else value
            return results

        error_dict = defaultdict(list)
        for k, v in self.to_dict().items():
            error_dict[generate_key(v)].append(k)
        return " ".join([f"{k}: {v}" for k, v in error_dict.items()])
