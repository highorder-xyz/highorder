
from typing import (Any, Callable, Dict, List, Set, Tuple, Union, cast)

class Tag:
    def __init__(self, name, attrs = {}, children = []):
        self.name = name
        self.attrs = attrs
        self.children = children

    def add_attr(self, name, value):
        self.attrs[name] = value

    def add_tag(self, tag):
        self.children.append(tag)


class HtmlDoc:
    pass