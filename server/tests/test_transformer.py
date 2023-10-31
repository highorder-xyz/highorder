
from highorder.hola.transformer import FilterExprTransformer
import ast
import pprint

pp = pprint.PrettyPrinter(indent=4)

def expr_to_dict(expr):
    transformed = {
        "type": "expression",
        "operator": expr.join_type,
        "negate": expr._is_negated
    }
    if expr.filters:
        transformed.update(expr.filters)
    elif expr.children:
        transformed['elements'] = []
        for child in expr.children:
            transformed['elements'].append(expr_to_dict(child))
    return transformed

def expr_dump(expr, **kwargs):
    d = expr_to_dict(expr)
    pp.pprint(d)

def compare_transformed(transformed, desire_dict):
    expr_dict = expr_to_dict(transformed)
    assert expr_dict == desire_dict

def test_filter_expr_1():
    expr = 'model_item.name == "aaa"'
    t = FilterExprTransformer(name_replace = {"model_item": "value"})
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "value.name": "aaa"
    })

def test_filter_expr_2():
    expr = 'model_item.name == "aaa" and model_item.type.name == "bb" '
    t = FilterExprTransformer()
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "elements": [
            {
                "type": "expression",
                "operator": "AND",
                "negate": False,
                "model_item.name": "aaa"
            },
            {
                "type": "expression",
                "operator": "AND",
                "negate": False,
                "model_item.type.name": "bb"
            }
        ]
    })

def test_filter_expr_3():
    expr = 'model_item.name.contains("abc") '
    t = FilterExprTransformer()
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "model_item.name__contains":["abc"]
    })