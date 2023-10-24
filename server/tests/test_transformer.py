
from highorder.hola.transformer import FilterExprTransformer
import ast

def test_filter_expr_1():
    expr = 'model_item.name == "aaa"'
    t = FilterExprTransformer()
    print(ast.dump(t.transform(expr)))