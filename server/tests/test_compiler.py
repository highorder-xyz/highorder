
from highorder.base.compiler import Tokenizer, TokenKind

def compare_tokens(code, desire_tokens):
    raw_tokens = Tokenizer().tokenize(code)
    tokens = list(map(lambda x: (x.kind, x.value), raw_tokens))
    assert tokens == desire_tokens

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
            (TokenKind.Identifier, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/'),
            (TokenKind.RBrace, '}')
        ]
    )