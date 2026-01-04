"""
Hola词法分析器
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator
from .error import TokenizeError, ErrorPosition


class TokenKind(Enum):
    """Token类型枚举"""
    # 结构token
    Identifier = auto()       # Page
    PropertyName = auto()     # name
    StringLiteral = auto()    # "hello"
    NumberLiteral = auto()    # 123
    ColorLiteral = auto()     # #FF0000
    BoolLiteral = auto()      # true, false
    NullLiteral = auto()      # null
    
    # 分隔符
    LBrace = auto()           # {
    RBrace = auto()           # }
    LBracket = auto()         # [
    RBracket = auto()         # ]
    Colon = auto()            # :
    Comma = auto()            # ,
    LineBreak = auto()        # \n
    
    # 运算符
    Plus = auto()             # +
    Minus = auto()            # -
    Star = auto()             # *
    Slash = auto()            # /
    Bang = auto()             # !
    Equal = auto()            # =
    LParen = auto()           # (
    RParen = auto()           # )
    Dot = auto()              # .
    
    # 复合运算符
    BangEqual = auto()        # !=
    EqualEqual = auto()       # ==
    Greater = auto()          # >
    GreaterEqual = auto()     # >=
    Less = auto()             # <
    LessEqual = auto()        # <=
    AndAnd = auto()           # &&
    OrOr = auto()             # ||
    
    # 表达式标记
    LBraceLBrace = auto()     # {{
    RBraceRBrace = auto()     # }}
    
    # 其他
    Comment = auto()          # // comment or /* comment */
    Eof = auto()
    Unknown = auto()


@dataclass
class Token:
    """Token数据结构"""
    kind: TokenKind
    value: str
    line: int
    column: int
    index: int
    
    def __str__(self) -> str:
        return f"Token({self.kind.name}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def position(self) -> ErrorPosition:
        """获取错误位置"""
        return ErrorPosition(self.line, self.column, self.index)


class TokenizerState(Enum):
    """词法分析器状态"""
    Default = auto()
    InExpression = auto()


class Tokenizer:
    """Hola词法分析器"""
    
    def __init__(self, source: str):
        self.source = source
        self.chars = iter(source)
        self.state = TokenizerState.Default
        self._peek: Optional[str] = None
        
        # 位置跟踪
        self.line = 1
        self.column = 1
        self.index = 0
    
    def tokenize(self) -> List[Token]:
        """将源代码转换为token列表"""
        tokens = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.kind == TokenKind.Eof:
                break
        return tokens
    
    def next_token(self) -> Token:
        """获取下一个token"""
        if self.state == TokenizerState.Default:
            return self._next_default()
        else:
            return self._next_expression()
    
    def _next_default(self) -> Token:
        """默认模式下的token生成"""
        self._skip_whitespace()
        
        start_line = self.line
        start_column = self.column
        start_index = self.index
        
        ch = self._advance()
        
        if ch is None:
            return Token(TokenKind.Eof, "", start_line, start_column, start_index)
        
        match ch:
            case '{':
                if self._peek_char() == '{':
                    self._advance()
                    self.state = TokenizerState.InExpression
                    return Token(TokenKind.LBraceLBrace, "{{", start_line, start_column, start_index)
                return Token(TokenKind.LBrace, "{", start_line, start_column, start_index)
            
            case '}':
                return Token(TokenKind.RBrace, "}", start_line, start_column, start_index)
            
            case '[':
                return Token(TokenKind.LBracket, "[", start_line, start_column, start_index)
            
            case ']':
                return Token(TokenKind.RBracket, "]", start_line, start_column, start_index)
            
            case ':':
                return Token(TokenKind.Colon, ":", start_line, start_column, start_index)
            
            case ',':
                return Token(TokenKind.Comma, ",", start_line, start_column, start_index)
            
            case '\n':
                return Token(TokenKind.LineBreak, "\n", start_line, start_column, start_index)
            
            case '.':
                return Token(TokenKind.Dot, ".", start_line, start_column, start_index)
            
            case '/':
                if self._peek_char() == '/':
                    return self._read_line_comment(start_line, start_column, start_index)
                elif self._peek_char() == '*':
                    return self._read_block_comment(start_line, start_column, start_index)
                return Token(TokenKind.Slash, "/", start_line, start_column, start_index)
            
            case '#':
                return self._read_color(start_line, start_column, start_index)
            
            case '"' | "'":
                return self._read_string(ch, start_line, start_column, start_index)
            
            case _:
                if ch.isalpha() or ch == '_':
                    return self._read_identifier(ch, start_line, start_column, start_index)
                elif ch.isdigit():
                    return self._read_number(ch, start_line, start_column, start_index)
                else:
                    return Token(TokenKind.Unknown, ch, start_line, start_column, start_index)
    
    def _next_expression(self) -> Token:
        """表达式模式下的token生成"""
        self._skip_whitespace()
        
        start_line = self.line
        start_column = self.column
        start_index = self.index
        
        ch = self._advance()
        
        if ch is None:
            return Token(TokenKind.Eof, "", start_line, start_column, start_index)
        
        match ch:
            case '}':
                if self._peek_char() == '}':
                    self._advance()
                    self.state = TokenizerState.Default
                    return Token(TokenKind.RBraceRBrace, "}}", start_line, start_column, start_index)
                return Token(TokenKind.RBrace, "}", start_line, start_column, start_index)
            
            case '+':
                return Token(TokenKind.Plus, "+", start_line, start_column, start_index)
            
            case '-':
                return Token(TokenKind.Minus, "-", start_line, start_column, start_index)
            
            case '*':
                return Token(TokenKind.Star, "*", start_line, start_column, start_index)
            
            case '/':
                return Token(TokenKind.Slash, "/", start_line, start_column, start_index)
            
            case '(':
                return Token(TokenKind.LParen, "(", start_line, start_column, start_index)
            
            case ')':
                return Token(TokenKind.RParen, ")", start_line, start_column, start_index)
            
            case '[':
                return Token(TokenKind.LBracket, "[", start_line, start_column, start_index)
            
            case ']':
                return Token(TokenKind.RBracket, "]", start_line, start_column, start_index)
            
            case ',':
                return Token(TokenKind.Comma, ",", start_line, start_column, start_index)
            
            case '.':
                return Token(TokenKind.Dot, ".", start_line, start_column, start_index)
            
            case '=':
                if self._peek_char() == '=':
                    self._advance()
                    return Token(TokenKind.EqualEqual, "==", start_line, start_column, start_index)
                return Token(TokenKind.Equal, "=", start_line, start_column, start_index)
            
            case '!':
                if self._peek_char() == '=':
                    self._advance()
                    return Token(TokenKind.BangEqual, "!=", start_line, start_column, start_index)
                return Token(TokenKind.Bang, "!", start_line, start_column, start_index)
            
            case '>':
                if self._peek_char() == '=':
                    self._advance()
                    return Token(TokenKind.GreaterEqual, ">=", start_line, start_column, start_index)
                return Token(TokenKind.Greater, ">", start_line, start_column, start_index)
            
            case '<':
                if self._peek_char() == '=':
                    self._advance()
                    return Token(TokenKind.LessEqual, "<=", start_line, start_column, start_index)
                return Token(TokenKind.Less, "<", start_line, start_column, start_index)
            
            case '&':
                if self._peek_char() == '&':
                    self._advance()
                    return Token(TokenKind.AndAnd, "&&", start_line, start_column, start_index)
                return Token(TokenKind.Unknown, "&", start_line, start_column, start_index)
            
            case '|':
                if self._peek_char() == '|':
                    self._advance()
                    return Token(TokenKind.OrOr, "||", start_line, start_column, start_index)
                return Token(TokenKind.Unknown, "|", start_line, start_column, start_index)
            
            case '#':
                return self._read_color(start_line, start_column, start_index)
            
            case '"' | "'":
                return self._read_string(ch, start_line, start_column, start_index)
            
            case _:
                if ch.isalpha() or ch == '_':
                    return self._read_identifier(ch, start_line, start_column, start_index)
                elif ch.isdigit():
                    return self._read_number(ch, start_line, start_column, start_index)
                else:
                    return Token(TokenKind.Unknown, ch, start_line, start_column, start_index)
    
    def _skip_whitespace(self):
        """跳过空白字符（不包括换行）"""
        while True:
            ch = self._peek_char()
            if ch and ch.isspace() and ch != '\n':
                self._advance()
            else:
                break
    
    def _read_string(self, quote: str, start_line: int, start_column: int, start_index: int) -> Token:
        """读取字符串字面量"""
        value = []
        while True:
            ch = self._advance()
            if ch is None:
                break
            
            if ch == quote:
                return Token(TokenKind.StringLiteral, ''.join(value), start_line, start_column, start_index)
            
            if ch == '\\':
                ch = self._advance()
                if ch is None:
                    break
                
                # 处理转义序列
                escape_map = {
                    'n': '\n',
                    'r': '\r',
                    't': '\t',
                    'v': '\v',
                    'b': '\b',
                    'f': '\f',
                    'a': '\a',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                }
                value.append(escape_map.get(ch, ch))
            else:
                value.append(ch)
        
        return Token(TokenKind.Unknown, ''.join(value), start_line, start_column, start_index)
    
    def _read_identifier(self, first: str, start_line: int, start_column: int, start_index: int) -> Token:
        """读取标识符"""
        value = [first]
        while True:
            ch = self._peek_char()
            if ch and (ch.isalnum() or ch == '_'):
                value.append(self._advance())
            else:
                break
        
        value_str = ''.join(value)
        
        # 判断token类型
        if value_str in ('true', 'false'):
            return Token(TokenKind.BoolLiteral, value_str, start_line, start_column, start_index)
        elif value_str == 'null':
            return Token(TokenKind.NullLiteral, value_str, start_line, start_column, start_index)
        elif self.state == TokenizerState.Default and first.islower():
            return Token(TokenKind.PropertyName, value_str, start_line, start_column, start_index)
        else:
            return Token(TokenKind.Identifier, value_str, start_line, start_column, start_index)
    
    def _read_number(self, first: str, start_line: int, start_column: int, start_index: int) -> Token:
        """读取数字字面量"""
        value = [first]
        has_dot = False
        
        while True:
            ch = self._peek_char()
            if ch and (ch.isdigit() or ch == '_' or ch == '.'):
                if ch == '.':
                    if has_dot:
                        break
                    has_dot = True
                if ch != '_':
                    value.append(self._advance())
                else:
                    self._advance()
            else:
                break
        
        value_str = ''.join(value)
        return Token(TokenKind.NumberLiteral, value_str, start_line, start_column, start_index)
    
    def _read_line_comment(self, start_line: int, start_column: int, start_index: int) -> Token:
        """读取单行注释"""
        self._advance()  # 消费第二个'/'
        value = []
        while True:
            ch = self._peek_char()
            if ch and ch != '\n':
                value.append(self._advance())
            else:
                break
        return Token(TokenKind.Comment, ''.join(value), start_line, start_column, start_index)
    
    def _read_block_comment(self, start_line: int, start_column: int, start_index: int) -> Token:
        """读取块注释"""
        self._advance()  # 消费'*'
        value = []
        
        while True:
            ch = self._advance()
            if ch is None:
                break
            
            if ch == '*' and self._peek_char() == '/':
                self._advance()  # 消费'/'
                break
            
            value.append(ch)
        
        return Token(TokenKind.Comment, ''.join(value), start_line, start_column, start_index)
    
    def _read_color(self, start_line: int, start_column: int, start_index: int) -> Token:
        """读取颜色字面量"""
        value = ['#']
        
        while True:
            ch = self._peek_char()
            if ch and ch.lower() in '0123456789abcdef':
                value.append(self._advance())
            else:
                break
        
        value_str = ''.join(value)
        hex_len = len(value_str) - 1  # 减去'#'
        
        # 有效的十六进制颜色长度: 3, 4, 6, 8
        if hex_len in (3, 4, 6, 8):
            return Token(TokenKind.ColorLiteral, value_str, start_line, start_column, start_index)
        
        return Token(TokenKind.Unknown, value_str, start_line, start_column, start_index)
    
    def _advance(self) -> Optional[str]:
        """前进一个字符"""
        if self._peek is not None:
            ch = self._peek
            self._peek = None
        else:
            try:
                ch = next(self.chars)
            except StopIteration:
                return None
        
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.index += 1
        return ch
    
    def _peek_char(self) -> Optional[str]:
        """查看下一个字符但不消费"""
        if self._peek is not None:
            return self._peek
        
        try:
            self._peek = next(self.chars)
            return self._peek
        except StopIteration:
            return None
