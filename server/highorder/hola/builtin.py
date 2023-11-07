
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

def random_color():
    index = random.randint(0, len(THEME_COLORS) - 1)
    return THEME_COLORS[index]

