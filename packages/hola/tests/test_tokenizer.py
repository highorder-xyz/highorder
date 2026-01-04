"""
Tokenizer单元测试
"""

import sys
import os
import unittest

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

from hola.tokenizer import Tokenizer, TokenKind, TokenizerState


class TestTokenizer(unittest.TestCase):
    """Tokenizer测试类"""
    
    def test_simple_object(self):
        """测试简单对象tokenization"""
        source = 'Page { title: "Hello" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 7
        assert tokens[0].kind == TokenKind.Identifier
        assert tokens[0].value == 'Page'
        assert tokens[1].kind == TokenKind.LBrace
        assert tokens[2].kind == TokenKind.PropertyName
        assert tokens[2].value == 'title'
        assert tokens[3].kind == TokenKind.Colon
        assert tokens[4].kind == TokenKind.StringLiteral
        assert tokens[4].value == 'Hello'
        assert tokens[5].kind == TokenKind.RBrace
        assert tokens[6].kind == TokenKind.Eof
    
    def test_string_literals(self):
        """测试字符串字面量"""
        source = '"hello" \'world\''
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.StringLiteral
        assert tokens[0].value == 'hello'
        assert tokens[1].kind == TokenKind.StringLiteral
        assert tokens[1].value == 'world'
        assert tokens[2].kind == TokenKind.Eof
    
    def test_string_with_escapes(self):
        """测试带转义字符的字符串"""
        source = r'"line1\nline2\ttab"'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 2
        assert tokens[0].kind == TokenKind.StringLiteral
        assert tokens[0].value == 'line1\nline2\ttab'
    
    def test_number_literals(self):
        """测试数字字面量"""
        source = '123 99.9 1_000_000'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 4
        assert tokens[0].kind == TokenKind.NumberLiteral
        assert tokens[0].value == '123'
        assert tokens[1].kind == TokenKind.NumberLiteral
        assert tokens[1].value == '99.9'
        assert tokens[2].kind == TokenKind.NumberLiteral
        assert tokens[2].value == '1_000_000'
        assert tokens[3].kind == TokenKind.Eof
    
    def test_bool_literals(self):
        """测试布尔字面量"""
        source = 'true false'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.BoolLiteral
        assert tokens[0].value == 'true'
        assert tokens[1].kind == TokenKind.BoolLiteral
        assert tokens[1].value == 'false'
        assert tokens[2].kind == TokenKind.Eof
    
    def test_null_literal(self):
        """测试null字面量"""
        source = 'null'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 2
        assert tokens[0].kind == TokenKind.NullLiteral
        assert tokens[0].value == 'null'
        assert tokens[1].kind == TokenKind.Eof
    
    def test_color_literals(self):
        """测试颜色字面量"""
        source = '#FF0000 #abc'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.ColorLiteral
        assert tokens[0].value == '#FF0000'
        assert tokens[1].kind == TokenKind.ColorLiteral
        assert tokens[1].value == '#abc'
        assert tokens[2].kind == TokenKind.Eof
    
    def test_expression_block(self):
        """测试表达式块"""
        source = '{{ a + b }}'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 6
        assert tokens[0].kind == TokenKind.LBraceLBrace
        assert tokens[1].kind == TokenKind.Identifier
        assert tokens[1].value == 'a'
        assert tokens[2].kind == TokenKind.Plus
        assert tokens[3].kind == TokenKind.Identifier
        assert tokens[3].value == 'b'
        assert tokens[4].kind == TokenKind.RBraceRBrace
        assert tokens[5].kind == TokenKind.Eof
    
    def test_line_comment(self):
        """测试单行注释"""
        source = '// this is a comment\nPage { title: "Test" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        # 注释应该被忽略
        assert tokens[0].kind == TokenKind.Identifier
        assert tokens[0].value == 'Page'
    
    def test_block_comment(self):
        """测试块注释"""
        source = '/* block comment */ Page { title: "Test" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        # 注释应该被忽略
        assert tokens[0].kind == TokenKind.Identifier
        assert tokens[0].value == 'Page'
    
    def test_list(self):
        """测试列表"""
        source = '[1, 2, 3]'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 7
        assert tokens[0].kind == TokenKind.LBracket
        assert tokens[1].kind == TokenKind.NumberLiteral
        assert tokens[2].kind == TokenKind.Comma
        assert tokens[3].kind == TokenKind.NumberLiteral
        assert tokens[4].kind == TokenKind.Comma
        assert tokens[5].kind == TokenKind.NumberLiteral
        assert tokens[6].kind == TokenKind.RBracket
    
    def test_list_with_holes(self):
        """测试带空位的列表"""
        source = '[1,,3]'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 5
        assert tokens[0].kind == TokenKind.LBracket
        assert tokens[1].kind == TokenKind.NumberLiteral
        assert tokens[2].kind == TokenKind.Comma
        assert tokens[3].kind == TokenKind.Comma
        assert tokens[4].kind == TokenKind.NumberLiteral
    
    def test_multiline_list(self):
        """测试多行列表"""
        source = '[1\n2\n3]'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 7
        assert tokens[0].kind == TokenKind.LBracket
        assert tokens[1].kind == TokenKind.NumberLiteral
        assert tokens[2].kind == TokenKind.LineBreak
        assert tokens[3].kind == TokenKind.NumberLiteral
        assert tokens[4].kind == TokenKind.LineBreak
        assert tokens[5].kind == TokenKind.NumberLiteral
        assert tokens[6].kind == TokenKind.RBracket
    
    def test_operators(self):
        """测试运算符"""
        source = '+ - * / == != < <= > >= && || !'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].kind == TokenKind.Plus
        assert tokens[1].kind == TokenKind.Minus
        assert tokens[2].kind == TokenKind.Star
        assert tokens[3].kind == TokenKind.Slash
        assert tokens[4].kind == TokenKind.EqualEqual
        assert tokens[5].kind == TokenKind.BangEqual
        assert tokens[6].kind == TokenKind.Less
        assert tokens[7].kind == TokenKind.LessEqual
        assert tokens[8].kind == TokenKind.Greater
        assert tokens[9].kind == TokenKind.GreaterEqual
        assert tokens[10].kind == TokenKind.AmpAmp
        assert tokens[11].kind == TokenKind.PipePipe
        assert tokens[12].kind == TokenKind.Bang
    
    def test_namespace(self):
        """测试命名空间"""
        source = 'System.Collections.Generic.List { count: 0 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].kind == TokenKind.Identifier
        assert tokens[0].value == 'System'
        assert tokens[1].kind == TokenKind.Dot
        assert tokens[2].kind == TokenKind.Identifier
        assert tokens[2].value == 'Collections'
        assert tokens[3].kind == TokenKind.Dot
        assert tokens[4].kind == TokenKind.Identifier
        assert tokens[4].value == 'Generic'
        assert tokens[5].kind == TokenKind.Dot
        assert tokens[6].kind == TokenKind.Identifier
        assert tokens[6].value == 'List'
    
    def test_token_positions(self):
        """测试token位置信息"""
        source = 'Page { title: "Hello" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[1].line == 1
        assert tokens[1].column == 6
        assert tokens[2].line == 1
        assert tokens[2].column == 8
    
    def test_empty_source(self):
        """测试空源代码"""
        source = ''
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.Eof
    
    def test_whitespace_only(self):
        """测试只有空白字符的源代码"""
        source = '   \n\t   '
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.Eof
