import random
from datetime import datetime, date, timedelta
import builtins
from typing import Mapping
from likepy import safer_getattr

EXPR_BUILTINS = {}

THEME_COLORS = [
    "#45283c",
    "#663931",
    "#8f563b",
    "#df7126",
    "#d9a066",
    "#eec39a",
    "#fbf236",
    "#99e550",
    "#6abe30",
    "#37946e",
    "#4b692f",
    "#524b24",
    "#323c39",
    "#3f3f74",
    "#306082",
    "#5b6ee1",
    "#639bff",
    "#5fcde4",
    "#cbdbfc",
    "#9badb7",
    "#696a6a",
    "#595652",
    "#76428a",
    "#ac3232",
    "#d95763",
    "#d77bba",
    "#8f974a",
    "#8a6f30",
]


class HolaBulitin:
    @staticmethod
    def random(start, end):
        if isinstance(start, int):
            return random.randint(start, end)
        else:
            return random.randint(int(start), int(end))

    @staticmethod
    def lastdays(count=1):
        days = []
        today = date.today()
        for i in range(0, count):
            day = today - timedelta(days=i)
            days.append(day.isoformat())
        return days

    @staticmethod
    def join(arr, separator="\n"):
        return separator.join(arr)

    @staticmethod
    def version_greater_than(version1, version2):
        v1 = sum(
            map(
                lambda x: int(x[1]) * (1000 ** x[0]),
                enumerate(reversed(version1.split("."))),
            )
        )
        v2 = sum(
            map(
                lambda x: int(x[1]) * (1000 ** x[0]),
                enumerate(reversed(version2.split("."))),
            )
        )
        return v1 > v2

    @staticmethod
    def random_color():
        index = random.randint(0, len(THEME_COLORS) - 1)
        return THEME_COLORS[index]

_safe_names = [
    'abs',
    'bool',
    'chr',
    'complex',
    'divmod',
    'float',
    'hash',
    'hex',
    'id',
    'int',
    'len',
    'oct',
    'ord',
    'pow',
    'range',
    'round',
    'slice',
    'str',
    'tuple',
    'zip'
]

_builtin_values = {
    'true': True,
    'false': False,
    'null': None
}

for name in _safe_names:
    EXPR_BUILTINS[name] = getattr(builtins, name)

for name, value in _builtin_values.items():
    EXPR_BUILTINS[name] = value

EXPR_BUILTINS['_getattr_'] = safer_getattr


class EveryExpression:
    def __init__(self, collection):
        self.value = collection

    def __getattr__(self, name):
        attr_value = []
        for v in self.value:
            if isinstance(v, (dict, Mapping)):
                attr_value.append(v.get(name, None))
            else:
                attr_value.append(getattr(v, name, None))
        return EveryExpression(attr_value)

    def __eq__(self, other):
        if not self.value:
            return False
        rets = list(map(lambda x: x == other, self.value))
        return all(rets)


def every(collection):
    return  EveryExpression(collection)


EXPR_BUILTINS['every'] = every