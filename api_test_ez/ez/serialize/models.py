# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""
import copy

from api_test_ez.ez.serialize.errors import ValidationError
from api_test_ez.ez.serialize.fields import BaseField, StringField, IntegerField


__all__ = ["ValidatorModel"]


class ModelMetaclass(type):

    def __new__(mcs, name, bases, attrs):
        super_new = super().__new__

        # If a base class just call super new
        if name == "ValidatorModel":
            return super_new(mcs, name, bases, attrs)

        # Discover any fields
        fields_mapping = {}

        for attr_name, attr_value in attrs.items():
            if issubclass(attr_value.__class__, BaseField) \
                    or attr_value.__class__.__base__.__name__ in __all__:   # is subclass of `ValidatorModel`
                fields_mapping.update({attr_name: attr_value})
                attrs.update({attr_name: attr_value})

        # Record all fields.
        attrs["__declared_fields__"] = fields_mapping

        return super_new(mcs, name, bases, attrs)


class ValidatorModel(metaclass=ModelMetaclass):

    def __init__(self, *args, **values):
        self.__fields_mapping__ = copy.deepcopy(getattr(self, "__declared_fields__"))
        if args:
            raise TypeError(
                "Instantiating a field with positional arguments is not "
                "supported. Please use `field_name=value` keyword arguments."
            )

        self.source_values = values

    def validate(self, data: dict, full_repr=True):
        """
        :param data:
        :param full_repr:   Determines the completeness of the returned result data.
                            Must be `True` when call internally.
        :return:
        """
        data.update(self.source_values)
        fields_mapping = copy.deepcopy(getattr(self, "__fields_mapping__"))

        for k, v in fields_mapping.items():
            try:
                # If `v` is `ValidateModel`, we validate it by itself.
                # We use `setattr` to set attributes, in order to trigger `__set__`.
                if isinstance(v, ValidatorModel):
                    setattr(self, k, v.validate(data[k]))
                else:
                    setattr(self, k, data[k])
                v = getattr(self, k)
                data.update({k: v})
            except KeyError:
                if getattr(v, 'required', None):
                    _error = ValidationError("Field is required but not provided.")
                    setattr(self, k, repr(_error))
                    data.update({k: repr(_error)})
        if full_repr:
            return data
        else:
            return getattr(self, "__fields_mapping__")

    def __str__(self):
        return f"<{self.__class__.__name__}> {getattr(self, '__fields_mapping__')}"

    __repr__ = __str__
