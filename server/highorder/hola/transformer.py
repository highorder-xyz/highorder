
import ast


def camel_to_snake(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')

class HolaExprParseError(Exception):
    pass

class QueryExpr:
    AND = "AND"
    OR = "OR"

    def __init__(self, *args, join_type=AND, **kwargs):
        if args and kwargs:
            newarg = QueryExpr(join_type=join_type, **kwargs)
            args = (newarg,) + args
            kwargs = {}
        if not all(isinstance(node, QueryExpr) for node in args):
            raise Exception("All ordered arguments must be QueryExpr nodes")
        self.children = args
        self.filters = kwargs
        if join_type not in {self.AND, self.OR}:
            raise Exception("join_type must be AND or OR")
        self.join_type = join_type
        self._is_negated = False

    def __and__(self, other):
        if not isinstance(other, QueryExpr):
            raise Exception("AND operation requires a QueryExpr node")
        return QueryExpr(self, other, join_type=self.AND)

    def __or__(self, other):
        if not isinstance(other, QueryExpr):
            raise Exception("OR operation requires a QueryExpr node")
        return QueryExpr(self, other, join_type=self.OR)

    def __invert__(self):
        q = QueryExpr(*self.children, join_type=self.join_type, **self.filters)
        q.negate()
        return q

    def negate(self):
        self._is_negated = not self._is_negated

    def to_dict(self):
        pass


class FilterExprTransformer:
    op_suffix_map = {
        'eq': '',
        'noteq': 'not',
        'lt': 'lt',
        'lte': 'lte',
        'gt': 'gt',
        'gte': 'gte',
        'in': 'in',
        'notin': 'not_in'
    }
    def __init__(self, expr_cls = QueryExpr, **kwargs):
        self.expr_cls = expr_cls
        self.name_replace = kwargs.get("name_replace", {})

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
        # print(ast.dump(expr_ast, indent='\t'))
        f_expr = self.transform_node(expr_ast)
        return f_expr

    def transform_node(self, node):
        name = camel_to_snake(node.__class__.__name__)
        method_name = f'transform_{name}'
        method = getattr(self, method_name, None)
        if callable(method):
            return method(node)
        else:
            raise Exception(f'no transform for node type: {name}.')

    def transform_expression(self, node):
        return self.transform_node(node.body)


    def transform_compare(self, node):
        name = self.transform_node(node.left)
        op = node.ops[0].__class__.__name__.lower()
        suffix = self.op_suffix_map[op]
        if suffix:
            key_name = f'{name}__{suffix}'
        else:
            key_name = f'{name}'
        target = self.transform_node(node.comparators[0])
        return self.expr_cls(**{key_name: target})

    def transform_call(self, node):
        func_name = self.transform_node(node.func)
        args = [self.transform_node(arg) for arg in node.args]
        return self.expr_cls(**{func_name: args})

    def transform_attribute(self, node):
        keys = []
        keys.append(self.transform_node(node.value))
        keys.append(node.attr)
        return '__'.join(keys)

    def transform_name(self, node):
        name = node.id
        if name in self.name_replace:
            return self.name_replace[name]
        else:
            return name

    def transform_constant(self, node):
        return node.value

    def transform_bool_op(self, node):
        op = node.op.__class__.__name__.upper()
        expr_values = [self.transform_node(n) for n in node.values]
        expr_values = list(filter(lambda x: x != None, expr_values))
        return self.expr_cls(*expr_values, join_type=op)