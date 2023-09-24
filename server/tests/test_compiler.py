
from highorder.base.compiler import Tokenizer, TokenKind, NodeKind, Parser

def compare_tokens(code, desire_tokens):
    raw_tokens = Tokenizer().tokenize(code)
    tokens = list(map(lambda x: (x.kind, x.value), raw_tokens))
    assert tokens == desire_tokens

def compare_nodes(code, desire_nodes):
    root_node = Parser().parse(code)
    nodes = list(map(lambda x: {'kind': x.kind, 'value': x.value, 'properties': x.properties, 'children':x.children}, root_node.children))
    assert desire_nodes == desire_nodes

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