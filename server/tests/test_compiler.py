
from highorder.base.compiler import Tokenizer, TokenKind, NodeKind, Parser, Compiler

def compare_tokens(code, desire_tokens):
    raw_tokens = Tokenizer().tokenize(code)
    tokens = list(map(lambda x: (x.kind, x.value), raw_tokens))
    assert tokens == desire_tokens

def compare_nodes(code, desire_nodes):
    def transform_list_node(list_node):
        return [transform_object_node(x) for x in list_node]

    def transform_properties(properties):
        p = {}
        for k,v in properties.items():
            p[k] = transform_object_node(v)
        return p

    def transform_object_node(obj_node):
        r = {
            'kind': obj_node.kind,
            'value': obj_node.value,
            'properties': transform_properties(obj_node.properties),
            'children': transform_list_node(obj_node.children)
        }
        return r

    root_node = Parser().parse(code)
    nodes = list(map(lambda x: transform_object_node(x), root_node.children))
    assert nodes == desire_nodes

def compare_object(code, desire_object):
    root_object = Compiler().compile(code)
    assert root_object == desire_object

def test_tokenizer_simple_1():
    compare_tokens(
        '''''',
        []
    )

def test_tokenizer_simple_2():
    compare_tokens(
        '''Page {}''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_3():
    compare_tokens(
        '''Page { route: "/" }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_31():
    compare_tokens(
        '''Page { route: "/a
bb" }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/a\nbb'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_4():
    compare_tokens(
        '''Page { route: "/"
            size: 5
        }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/'),
            (TokenKind.LineBreak, '\n'),
            (TokenKind.PropertyName, 'size'),
            (TokenKind.Colon, ':'),
            (TokenKind.NumberLiteral, 5),
            (TokenKind.RBrace, '}')
        ]
    )


def test_parser_simple_1():
    compare_nodes(
        '''Page {}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {},
                "children":[]
            }
        ]
    )

def test_parser_simple_2():
    compare_nodes(
        '''Page { route: "/abc" }''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    }
                },
                "children":[]
            }
        ]
    )

def test_compiler_simple_1():
    compare_object(
        '''Page {}''',
        {
            "interfaces": [{
                "type": "page"
            }]
        }
    )


def test_compiler_simple_2():
    compare_object(
        '''Page { route: "/home" }''',
        {
            "interfaces": [{
                "type": "page",
                "route": "/home"
            }]
        }
    )