from abc import ABC
from typing import Iterable


class BaseField(ABC):

    def __init__(self, value):
        self.value = value


class UniqueField(BaseField):

    def __init__(self, value, autoincrement=True):
        super().__init__(value)
        self.autoincrement = autoincrement


class IterableField(BaseField):

    def __init__(self, value: Iterable, iterative_mode="ORT"):
        """
        iterative_mode: `ORT` - Orthogonal
                        `EXH` - Exhaustive
        """
        super().__init__(value)
        self.iterative_mode = iterative_mode


class FixedField(BaseField):
    pass
