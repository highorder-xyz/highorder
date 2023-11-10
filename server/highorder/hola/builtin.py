import random

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
