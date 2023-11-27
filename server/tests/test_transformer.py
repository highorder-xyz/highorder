
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
    t = FilterExprTransformer(target = "model_item", rename= "value")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "value.name": "aaa"
    })

def test_filter_expr_1_1():
    expr = 'model_item.name == "aaa"'
    t = FilterExprTransformer(target = "model_item", rename= "")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "name": "aaa"
    })

def test_filter_expr_1_2():
    expr = 'model_item.name in ["aaa", "bb"]'
    t = FilterExprTransformer(target = "model_item", rename= "")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "name__in": ["aaa", 'bb']
    })

def test_filter_expr_1_2():
    expr = 'model_item.name in ("aaa", "bb")'
    t = FilterExprTransformer(target = "model_item", rename = "")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "name__in": ["aaa", 'bb']
    })

def test_filter_expr_1_3():
    expr = 'model_item.name in ("aaa", "bb")'
    t = FilterExprTransformer(target = "model_item")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "model_item.name__in": ["aaa", 'bb']
    })

def test_filter_expr_2():
    expr = 'model_item.name == "aaa" and model_item.type.name == "bb" '
    t = FilterExprTransformer(target = "model_item")
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
    t = FilterExprTransformer(target = "model_item")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "model_item.name__contains":["abc"]
    })


def test_filter_expr_4():
    expr = ''
    t = FilterExprTransformer(target = "model_item", rename = "value")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False
    })


def test_filter_expr_5():
    expr = 'it.active == true'
    t = FilterExprTransformer(target = "it")
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "it.active": True
    })


def test_filter_expr_6():
    expr = 'it.user_id == user.user_id'
    t = FilterExprTransformer(target = "it", rename="", context={"user": {"user_id": "UIDXXX", "user_name":"tom"}})
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "user_id": "UIDXXX"
    })

def test_filter_expr_7():
    expr = 'it.name == user.user_name'
    t = FilterExprTransformer(target = "it",
        rename = "value",
        context={"user": {"user_id": "UIDXXX", "user_name":"tom"}}
    )
    compare_transformed(t.transform(expr), {
        "type": "expression",
        "operator": "AND",
        "negate": False,
        "value.name": "tom"
    })