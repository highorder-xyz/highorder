
import re

propIdentifier = re.compile(r"[_a-z][_a-zA-Z0-9]*")

def snake_to_upper(name):
    if not name:
        return name
    parts = name.replace('_', '-').split('-')
    ret = []
    for p in parts:
        if not p:
            ret.append('_')
            continue
        ret.append(p[0].upper())
        ret.append(p[1:])
    return ''.join(ret)

class Decompiler:
    OBJ_DEFAULT_CHILDREN_MAP = {
        "data-object": "properties",
        "page": "elements",

    }

    def __init__(self):
        pass

    def decompile(self, hola_json):
        codes = ['']
        for category in ["objects", "variables", "attributes", "currencies",
                         "items", "itemboxes", "actions", "tasks",
                         "widgets", "components", "interfaces", "hooks"]:
            for obj in hola_json.get(category, []):
                codes.append(self.decompile_object(obj, multi_line=True, indent=0))
                codes.append('')
        return '\n'.join(codes)

    def decompile_object(self, obj, multi_line = True, indent=0):
        codes = []
        obj_type = obj.get('type', '')
        obj_classname = snake_to_upper(obj_type)
        indent_str = ' '*indent
        if multi_line:
            if obj_classname:
                codes.append(f'{indent_str}{obj_classname} {{')
            else:
                codes.append(f'{indent_str}{{')
        else:
            codes.append('{')
        children_property_name = self.OBJ_DEFAULT_CHILDREN_MAP.get(obj_type, 'elements')
        self._decompile_properties(obj, codes, ignore=["type", children_property_name], multi_line=multi_line, indent=indent+4)
        for child_obj in obj.get(children_property_name, []):
            codes.append(self.decompile_object(child_obj, multi_line=multi_line, indent=indent+4))
        if multi_line:
            codes.append(f'{indent_str}}}')
        else:
            codes.append('}')
        if multi_line:
            return '\n'.join(codes)
        else:
            return '{' + ','.join(codes[1:-1]) + '}'

    def _decompile_properties(self, obj, codes, ignore, multi_line=False, indent=0):
        ident_str = ' '*indent
        key_quote = not ("type" in obj)
        for key, value in obj.items():
            if ignore and key in ignore:
                continue
            if key_quote or not(propIdentifier.match(key)):
                key_str = f'"{key}"'
            else:
                key_str = key

            value_str = self._wrap_value(value, multi_line=multi_line, indent= indent).lstrip()
            if multi_line:
                codes.append(f'{ident_str}{key_str}: {value_str}')
            else:
                codes.append(f'{key_str}: {value_str}')

    def _wrap_value(self, value, multi_line=False, indent=0):
        indent_str = ' '*indent
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif value == None:
            return "null"
        elif isinstance(value, (tuple, list)):
            ret = []
            ret.append('[')
            for v in value:
                ret.append(self._wrap_value(v, multi_line=False, indent=0))
            ret.append(']')
            return '[' + ', '.join(ret[1:-1]) + ']'
        elif isinstance(value, (dict)):
            return self.decompile_object(value, multi_line=multi_line, indent=indent)
        else:
            print('unhandled type of value:', type(value))


