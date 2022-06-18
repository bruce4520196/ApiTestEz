# -*- coding: utf-8 -*-
"""
# @Time    : 2022/6/9 19:30
# @Author  : bruce
# @desc    :
"""
import re
from abc import abstractmethod, ABC

from api_test_ez.ez.orm.errors import ValidationError


__all__ = ["StringField", "IntegerField", "ListField", "DynamicListField"]


validator_funcs = [
    'should_be', 'should_in', 'should_contain', 'should_like',
    # For list field
    'count_should_be', 'count_should_gt', 'count_should_lt',
    'count_should_gte', 'count_should_lte',
    # For list members
    'members_should_contain_model'
]


class BaseField(ABC):
    field_type = None

    def __init__(self, required=False, null=False, **kwargs):
        self.required = required
        self.null = null
        self.name = None

        # Discover any validator function, which start with `should_`.
        # Store in `validator_funcs` dict.
        self.validate_funcs = {}
        for key, value in kwargs.items():
            if key in validator_funcs:
                self.validate_funcs.update({key: value})

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        # return getattr(instance.__fields_mapping__, self.validated_name, None)
        return instance.__fields_mapping__.get(self.name)

    def __set__(self, instance, value):
        # return maybe `errors` or `value`.
        value = self.validate(value)
        instance.__fields_mapping__[self.name] = value

    def error(self, message="", errors=None, field_name=None):
        """Raise a ValidationError."""
        field_name = field_name if field_name else self.name
        return ValidationError(message, errors=errors, field_name=field_name)

    def _func_should_be(self, value, expect_value):
        if value != expect_value:
            return self.error("[Lv2] %s should be %s but %s found." % (self.__class__.__name__, expect_value, value))
        return value

    def _func_should_in(self, value, expect_value):
        if value not in expect_value:
            return self.error("[Lv2] %s %s does not in %s." % (self.__class__.__name__, value, expect_value))
        return value

    def _func_should_contain(self, value, expect_value):
        if expect_value not in value:
            return self.error("[Lv2] %s %s does not contain %s." % (self.__class__.__name__, value, expect_value))
        return value

    @staticmethod
    def _validation_is_error(value):
        if "ValidationError" in str(value):
            return True
        return False

    def validate(self, value):
        """Perform validation on a value."""
        # Lv1 validate
        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        if self.field_type is not None:
            value = self._validate_types(value, self.field_type)

        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        # Lv2 validate
        value = self._validate_should_funcs(value)

        return value

    def _validate_should_funcs(self, value):
        # call `func_should_`.
        if len(self.validate_funcs) > 0:
            for should, expect_value in self.validate_funcs.items():
                func = getattr(self, "_func_%s" % should)
                value = func(value, expect_value)
        return value

    def _validate_types(self, value, field_type):
        if not isinstance(value, field_type):
            return self.error(f"[Lv1] {self.__class__.__name__} only accepts {self.field_type} values. "
                              f"but {value!r} found.")
        return value


class StringField(BaseField):

    __slots__ = ('should_be', 'should_in', 'should_contain', 'should_like')

    field_type = str

    def _func_should_like(self, value, expect_regex):
        res = re.search(expect_regex, value)
        if res:
            return value
        else:
            return self.error(f"[Lv2] {self.__class__.__name__} {value!r} does not match {expect_regex!r}.")


class IntegerField(BaseField):

    __slots__ = ('should_be', 'should_in', 'should_contain', 'should_like')

    field_type = int


class ListField(BaseField):

    __slots__ = ('should_be', 'should_in', 'should_contain', 'should_not_contain',
                 # For list field
                 'count_should_be', 'count_should_gt', 'count_should_lt',
                 'count_should_gte', 'count_should_lte', 'should_no_duplicates'
                 # For list members
                 'members_should_contain_model'
                 )

    field_type = list

    def __init__(self, *fields, **kwargs):
        self.fields = fields
        super().__init__(**kwargs)

    def _func_should_contain(self, value, expect_value):
        if isinstance(expect_value, list):
            if len(set(value).intersection(set(expect_value))) != len(expect_value):
                return self.error("[Lv2] %s %s does not contain %s." % (self.__class__.__name__, value, expect_value))
        else:
            if expect_value not in value:
                return self.error("[Lv2] %s %s does not contain %s." % (self.__class__.__name__, value, expect_value))
        return value

    def _func_should_no_duplicates(self, value, expect_value=True):
        # bcz dict can not be `set`, loop to validate.
        if isinstance(expect_value, bool):
            new_list = []
            for v in value:
                if v not in new_list:
                    new_list.append(v)
            if len(new_list) != len(value):
                return self.error("[Lv2] %s %s has duplicate data." % (self.__class__.__name__, value))
        else:
            return self.error(f"[Lv2] `should_no_duplicates` only accepts bool params, but {expect_value!r} found.")

    def _func_should_not_contain(self, value, expect_value):
        if isinstance(expect_value, list):
            if len(set(value).intersection(set(expect_value))) > 0:
                return self.error("[Lv2] %s %s should not contain %s." % (self.__class__.__name__, value, expect_value))
        else:
            if expect_value in value:
                return self.error("[Lv2] %s %s should not contain %s." % (self.__class__.__name__, value, expect_value))
        return value

    def _func_should_in(self, value, expect_value):
        if isinstance(expect_value, list):
            if len(set(value).intersection(set(expect_value))) != len(value):
                return self.error("[Lv2] %s %s does not in %s." % (self.__class__.__name__, value, expect_value))
            return value
        else:
            return self.error(f"[Lv1] {self.__class__.__name__} only accepts {self.field_type} values. "
                              f"but {expect_value!r} found.")

    def _func_count_should_be(self, value, expect_value):
        if isinstance(expect_value, int):
            if len(value) == expect_value:
                return value
            else:
                return self.error("[Lv2] %s count should be %s, but %s found."
                                  % (self.__class__.__name__, expect_value, len(value)))
        else:
            return self.error(f"[Lv2] `count_should_be` only accepts integer params, but {expect_value!r} found.")

    def _func_count_should_gt(self, value, expect_value):
        if isinstance(expect_value, int):
            if len(value) > expect_value:
                return value
            else:
                return self.error("[Lv2] %s count should greater than %s, but %s found."
                                  % (self.__class__.__name__, expect_value, len(value)))
        else:
            return self.error(f"[Lv2] `count_should_gt` only accepts integer params, but {expect_value!r} found.")

    def _func_count_should_gte(self, value, expect_value):
        if isinstance(expect_value, int):
            if len(value) >= expect_value:
                return value
            else:
                return self.error("[Lv2] %s count should greater than or equal to %s, but %s found."
                                  % (self.__class__.__name__, expect_value, len(value)))
        else:
            return self.error(f"[Lv2] `count_should_gte` only accepts integer params, but {expect_value!r} found.")

    def _func_count_should_lt(self, value, expect_value):
        if isinstance(expect_value, int):
            if len(value) < expect_value:
                return value
            else:
                return self.error("[Lv2] %s count should less than %s, but %s found."
                                  % (self.__class__.__name__, expect_value, len(value)))
        else:
            return self.error(f"[Lv2] `count_should_lt` only accepts integer params, but {expect_value!r} found.")

    def _func_count_should_lte(self, value, expect_value):
        if isinstance(expect_value, int):
            if len(value) <= expect_value:
                return value
            else:
                return self.error("[Lv2] %s count should less than or equal to %s, but %s found."
                                  % (self.__class__.__name__, expect_value, len(value)))
        else:
            return self.error(f"[Lv2] `count_should_lte` only accepts integer params, but {expect_value!r} found.")

    def _func_members_should_contain_model(self, value, expect_model):
        """It requires that members must contain a specific validator-model"""
        # Due to complications of circular imports, judge class by `__class__.__base__.__name__`.
        if expect_model.__class__.__base__.__name__ == 'ValidatorModel':
            for v in value:
                v = expect_model.validate(v)
                if self._validation_is_error(v):
                    return self.error(f"[Lv2] {self.__class__.__name__}'s members should contain {expect_model!r}, "
                                      f"but {v!r} does not match.")
            return value
        else:
            return self.error(f"[Lv2] `members_should_contain_model` only accepts ValidatorModel params, "
                              f"but {type(expect_model)!r} found.")

    def validate(self, value):
        # Lv1 validate
        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        if self.field_type is not None:
            value = self._validate_types(value, self.field_type)

        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        if len(self.fields) > len(value):
            return self.error(f"[Lv1] {self.__class__.__name__} expects {len(self.fields)} objects, but {len(value)} found.")

        for i, v in enumerate(self.fields):
            if issubclass(v.__class__, BaseField):
                v = v.validate(value[i])
            # Due to complications of circular imports, judge class by `__class__.__base__.__name__`.
            elif v.__class__.__base__.__name__ == 'ValidatorModel':
                v = v.validate(value[i])

            value[i] = v

        # Lv2 validate
        value = self._validate_should_funcs(value)

        return value


class DynamicListField(ListField):
    """This filed can be a little complicated.

    It validates every field and try to find a match result.
    We will loop through all elements to do this.
    This may take a long time."""

    __slots__ = ('should_be', 'should_in', 'should_contain', 'should_not_contain',
                 # For list field
                 'count_should_be', 'count_should_gt', 'count_should_lt',
                 'count_should_gte', 'count_should_lte', 'should_no_duplicates',
                 # For list members
                 'members_should_contain_model'
                 )

    field_type = list

    def _func_should_be(self, value: list, expect_value):
        if isinstance(expect_value, list):
            value.sort()
            expect_value.sort()
            if value == expect_value:
                return value
        return self.error("[Lv2] %s should be %s but %s found." % (self.__class__.__name__, expect_value, value))

    def validate(self, value):
        original_value = value
        # Lv1 validate
        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        if self.field_type is not None:
            value = self._validate_types(value, self.field_type)

        # If validate fail, just return value.
        if self._validation_is_error(value):
            return value

        int_field_list = []
        str_field_list = []
        lst_field_list = []
        model_field_list = []

        int_value_list = []
        str_value_list = []
        lst_value_list = []
        dict_value_list = []
        # Categorize fields, to validate if field type match.
        for field in self.fields:
            if isinstance(field, IntegerField):
                int_field_list.append(field)
            elif isinstance(field, StringField):
                str_field_list.append(field)
            elif isinstance(field, ListField) or isinstance(field, DynamicListField):
                lst_field_list.append(field)
            # Due to complications of circular imports, judge class by `__class__.__base__.__name__`.
            elif field.__class__.__base__.__name__ == 'ValidatorModel':
                model_field_list.append(field)

        # Categorize values
        for v in value:
            if isinstance(v, int):
                int_value_list.append(v)
            elif isinstance(v, str):
                str_value_list.append(v)
            elif isinstance(v, list):
                lst_value_list.append(v)
            elif isinstance(v, dict):
                dict_value_list.append(v)

        # At first, the count of values list should always >= the count of fields list.
        if len(int_field_list) > len(int_value_list):
            return self.error(f"Expect {len(int_field_list)} integer objects, but {len(int_value_list)} found.")
        if len(str_field_list) > len(str_value_list):
            return self.error(f"Expect {len(str_field_list)} string objects, but {len(str_value_list)} found.")
        if len(lst_field_list) > len(lst_value_list):
            return self.error(f"Expect {len(lst_field_list)} list objects, but {len(lst_value_list)} found.")
        if len(model_field_list) > len(dict_value_list):
            return self.error(f"Expect {len(model_field_list)} dict objects, but {len(dict_value_list)} found.")

        # Then we validate all the type one by one.
        # A list to record validate result.
        validate_result = []
        for field in self.fields:
            value = 'not_assigned'
            if isinstance(field, IntegerField):
                value, int_value_list = self._validate_field_in_value_list(field, int_value_list)

            elif isinstance(field, StringField):
                value, str_value_list = self._validate_field_in_value_list(field, str_value_list)

            elif isinstance(field, ListField) or isinstance(field, DynamicListField):
                value, lst_value_list = self._validate_field_in_value_list(field, lst_value_list)

            elif field.__class__.__base__.__name__ == 'ValidatorModel':
                value, dict_value_list = self._validate_field_in_value_list(field, dict_value_list)

            if self._validation_is_error(value):
                validate_result.append(value)
                return validate_result

        # Lv2 validate, we need use original value to validate.
        validate_result = self._validate_should_funcs(original_value)
        return validate_result

    @staticmethod
    def _validate_field_in_value_list(field, value_list: list):
        value = None
        lv2_value = None
        for value in value_list:
            value = field.validate(value)
            # If validate pass, remove the value to avoid validation conflicts.
            if 'ValidationError' not in str(value):
                value_list.remove(value)
                return value, value_list
            else:
                # Lv2 error means the validation goes to final stage. we should take this error priority to Lv1.
                if '[Lv2]' in str(value):
                    lv2_value = value
        return lv2_value if lv2_value else value, value_list

