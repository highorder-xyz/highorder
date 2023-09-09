
from highorder.base.compiler import Tokenizer, TokenKind

def test_tokenizer_simple_1():
    tokens = Tokenizer().tokenize('''''')
    assert len(tokens) == 0

def test_tokenizer_simple_2():
    tokens = Tokenizer().tokenize('''Page {}''')
    assert len(tokens) == 3
    assert tokens[0].kind == TokenKind.Identifier
    assert tokens[1].kind == TokenKind.LBrace
    assert tokens[2].kind == TokenKind.RBrace