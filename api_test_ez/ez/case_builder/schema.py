import itertools

from collections import namedtuple
from typing import Dict, List, Iterable, Callable

import tablib
from allpairspy import AllPairs

from api_test_ez.ez.case_builder.fields import UniqueField, IterableField, BaseField, FixedField


def to_pairs(name, field):     # In order to be consistent with the `allpairspy.Pairs` type
    return namedtuple("Pairs", name)(field)


class CaseBuilderSchemaMeta(type):

    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(mcs, name, bases, attrs)

        # If a base class just call super new
        if name == "CaseBuilderSchema":
            return klass

        # filter fields
        klass._ort_iterable_fields = []
        klass._exh_iterable_fields = []
        klass._unique_field = []
        klass._fixed_field = []

        for attr_name, attr_value in attrs.items():
            if issubclass(attr_value.__class__, IterableField):
                if attr_value.iterative_mode == 'ORT':
                    klass._ort_iterable_fields.append(
                        mcs._convert_field_to_list(attr_name, attr_value.value)
                    )
                elif attr_value.iterative_mode == 'EXH':
                    klass._exh_iterable_fields.append(
                        mcs._convert_field_to_list(attr_name, attr_value.value)
                    )
            elif issubclass(attr_value.__class__, UniqueField):
                klass._unique_field.append(
                       {attr_name: attr_value.value}
                    )
            elif issubclass(attr_value.__class__, FixedField):
                klass._fixed_field.append(
                       {attr_name: attr_value.value}
                    )
        return klass

    @staticmethod
    def _convert_field_to_list(
            field_name,
            field_value: Iterable
    ) -> List[dict]:
        return [{field_name: value} for value in field_value]


class CaseBuilderSchema(metaclass=CaseBuilderSchemaMeta):

    def __init__(
            self,
            ort_filter_func: Callable = lambda x: True,
            exh_filter_func: Callable = lambda x: True
    ):
        self._ort_filter_func = ort_filter_func
        self._exh_filter_func = exh_filter_func

    def _fields_build(self):

        # self._exh_iterable_fields:
        # [
        #   [{"a": 1}, {"a": 2}],
        #   [{"b": 3}, {"b": 4}],
        # ]

        # self._ort_iterable_fields:
        # [
        #   [{"c": 5}, {"c": 6}],
        #   [{"d": 7}, {"d": 8}],
        # ]

        # 1. generate the "EXH" (Exhaustive) field.
        computed_fields = []
        if len(self._exh_iterable_fields) > 0:
            # computed_exh_fields:
            # [
            #   [{"a": 1}, {"b": 3}],
            #   [{"a": 1}, {"b": 4}],
            #   [{"a": 2}, {"b": 3}],
            #   [{"a": 2}, {"b": 4}],
            # ]
            computed_fields = self._iter_field_build(self._exh_iterable_fields, "EXH")

        # 2. generate the "ORT" (Orthogonal) field.
        if len(self._ort_iterable_fields) > 0:
            if len(computed_fields) > 0:
                # `self._ort_iterable_fields` append `computed_exh_fields`:
                # [
                #   # self._ort_iterable_fields
                #   [{"c": 5}, {"c": 6}],
                #   [{"d": 7}, {"d": 8}],

                #   # computed_exh_fields
                #   [
                #       [{"a": 1}, {"b": 3}],
                #       [{"a": 1}, {"b": 4}],
                #       [{"a": 2}, {"b": 3}],
                #       [{"a": 2}, {"b": 4}],
                #   ],
                # ]
                self._ort_iterable_fields.append(computed_fields)
            computed_fields = self._iter_field_build(self._ort_iterable_fields, "ORT")

        # computed_ort_fields:
        # [
        #     [{'c': 5}, {'d': 7}, [{'a': 1}, {'b': 3}]],
        #     [{'c': 6}, {'d': 8}, [{'a': 1}, {'b': 3}]],
        #     [{'c': 6}, {'d': 7}, [{'a': 1}, {'b': 4}]],
        #     [{'c': 5}, {'d': 8}, [{'a': 1}, {'b': 4}]],
        #     [{'c': 5}, {'d': 8}, [{'a': 2}, {'b': 3}]],
        #     [{'c': 6}, {'d': 7}, [{'a': 2}, {'b': 3}]],
        #     [{'c': 6}, {'d': 7}, [{'a': 2}, {'b': 4}]],
        #     [{'c': 5}, {'d': 8}, [{'a': 2}, {'b': 4}]],
        # ]

        # self._unique_field
        # [{"e": 9}]

        # self._fixed_field
        # [{"f": 10}, {"g": 11}]

        # 3. merge `computed_ort_fields` / `fixed_field` / `unique_field`.
        merged_rows = []
        if len(computed_fields) > 0:
            for i, row in enumerate(computed_fields):
                # merge `fixed_field`
                new_row = row + self._fixed_field

                # merge `unique_field`
                for unique_field in self._unique_field:
                    new_unique_field = {
                        name: f"{value}_{str(i).zfill(len(str(len(computed_fields))))}"
                        for name, value in unique_field.items()
                    }

                    new_row.append(new_unique_field)

                merged_rows.append(new_row)
        else:   # maby `computed_ort_fields` is []
            # merge `fixed_field`
            new_row = self._fixed_field

            # merge `unique_field`
            for unique_field in self._unique_field:
                new_unique_field = {
                    name: f"{value}_01"
                    for name, value in unique_field.items()
                }

                new_row.append(new_unique_field)

            merged_rows.append(new_row)

        return merged_rows

    def unpack_row(self):
        # rows:
        # [{'a': CaseBuilderSchema}, {'b': '2'}, [{'c': '6'}, {'d': '8'}], {'name': 'case_23'}],
        rows = self._fields_build()
        new_rows = []
        for row in rows:
            new_row = []
            inner_row_schema = None
            for cell in row:
                if isinstance(cell, list):
                    # [{'c': '4'}, {'d': '7'}]
                    new_row += cell
                elif isinstance(cell, dict):
                    for v in cell.values():
                        try:
                            if issubclass(v, CaseBuilderSchema):
                                inner_row_schema = v
                        except TypeError:
                            if isinstance(v, list):
                                new_row += v
                            else:
                                new_row.append(cell)

                else:
                    raise Exception(f'Unknown type in row: {cell}')

            if inner_row_schema:
                # Exhaustive `new_row` and `inner_row_list`
                inner_rows = inner_row_schema().unpack_row()

                # `inner_rows`: [[{'name': '1'}, {'age': 2}]]
                # `new_row`: [{'b': '2'}, {'c': '4'}, {'d': '7'}, {'fix': 5}, {'name': 'case_01'}]
                # merge `inner_rows` and `new_row`
                for inner_row in inner_rows:
                    new_rows.append(inner_row + new_row)
            else:
                new_rows.append(new_row)
        return new_rows

    def _iter_field_build(self, iterable_fields, rule):
        if len(iterable_fields) <= 1:
            print("Warning: Algorithm-Rule must provide more than one option.")
            return iterable_fields

        if rule == "EXH":
            return self._exh_algorithm(iterable_fields, filter_func=self._exh_filter_func)
        elif rule == "ORT":
            return self._ort_algorithm(iterable_fields, filter_func=self._ort_filter_func)
        else:
            raise Exception(f"Unknown Algorithm-Rule: {rule}")

    @staticmethod
    def _ort_algorithm(iterable_fields: List[List[dict]], filter_func: Callable = lambda x: True):
        return [pair for pair in AllPairs(iterable_fields, filter_func=filter_func)]

    @staticmethod
    def _exh_algorithm(iterable_fields: List[List[dict]], filter_func: Callable = lambda x: True) -> List[List[dict]]:
        _exh_pairs = []
        for pair in itertools.product(*iterable_fields):

            if filter_func(pair):
                _exh_pairs.append(list(pair))

        return _exh_pairs

    def build(self):
        """
        :rtype: [ [dict] ]
        """
        return self.unpack_row()

    def save(self, file_path="", fmt="xlsx"):
        data = tablib.Dataset()
        cases = self.build()
        headers = []

        if len(cases) > 0:
            d = []
            for case in cases:
                values = []
                for cell in case:
                    for k, v in cell.items():
                        if k not in headers:
                            headers.append(k)
                        values.append(v)
                d.append(values)
                data.append(values)
            data.headers = headers
            export_data = data.export(fmt)

            with open(file_path, 'wb') as fw:
                fw.write(export_data)
        else:
            raise Exception(f"Case build failed, pls check fields in builder-schema.")
