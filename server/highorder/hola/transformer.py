
import ast

class HolaExprParseError(Exception):
    pass

class FilterExprTransformer:
    def __init__(self):
        pass

    def parse(self, expr):
        syntax_error_template = (
            'Line {lineno}: {type}: {msg} at statement: {statement!r}')
        expr_ast = None
        try:
            expr_ast = ast.parse(expr, '<string>', 'eval')
        except (TypeError, ValueError) as e:
            raise HolaExprParseError(str(e))
        except SyntaxError as v:
            raise HolaExprParseError(syntax_error_template.format(
                lineno=v.lineno,
                type=v.__class__.__name__,
                msg=v.msg,
                statement=v.text.strip() if v.text else None
            ))
        return expr_ast


    def transform(self, expr):
        expr_ast = self.parse(expr)
        return expr_ast
