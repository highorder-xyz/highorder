from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import string
from copy import deepcopy

class TokenKind(Enum):
    Unknown = 1
    StringLiteral = 2
    Number = 3
    Identifier = 4
    LBracket = 5
    RBracket = 6
    LBrace = 7
    RBrace = 8
    Colon = 9
    NewLine = 10
    Comment = 11

@dataclass
class CharPosition:
    index: int
    line: int
    column: int

    def move(self, num):
        self.index += num
        self.column += num

    def newline(self):
        self.index += 1
        self.line += 1
        self.column = 0

@dataclass
class Token:
    kind: TokenKind
    value: str
    start_pos: CharPosition
    end_pos: CharPosition

@dataclass
class TokenizeContext:
    start_pos: int
    chars: List[str] = field(default_factory=list)
    in_str_literal: bool = field(default=False)
    is_number: bool = field(default=False)

class NodeKind(Enum):
    Unknown = 1
    Oject = 2
    Property = 3
    Dict = 4
    List = 5
    NewLine = 10


@dataclass
class NodePosition:
    start: int
    end: int

@dataclass
class HolaNode:
    kind: NodeKind
    position: NodePosition
    properties: Dict[str, HolaNode] = field(default_factory=dict())
    children: List[HolaNode] = field(default_factory=list())


ESCAPE_CHAR_MAP = {
    'n': '\n',
    'r': '\r',
    't': '\t',
    'v': '\v',
    'b': '\b',
    'f': '\f',
    'a': '\a'
}

class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, code):
        pos = CharPosition(index = 0, line = 0, column = 0)
        tokens = []
        while pos.index < len(code):
            ch = code[pos.index]
            if ch == '{':
                tokens.append(Token(
                    kind = TokenKind.LBrace,
                    value = '{',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))

                pos.move(1)

            elif ch == '}':
                tokens.append(Token(
                    kind = TokenKind.RBrace,
                    value = '}',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))

                pos.move(1)

            elif ch == ':':
                tokens.append(Token(
                    kind = TokenKind.Colon,
                    value = ':',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))
                pos.move(1)
            elif ch == '\n':
                tokens.append(Token(
                    kind = TokenKind.NewLine,
                    value = '\n',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))
                pos.move(1)
            elif ch == '[':
                tokens.append(Token(
                    kind = TokenKind.LBracket,
                    value = '[',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))
                pos.move(1)
            elif ch == ']':
                tokens.append(Token(
                    kind = TokenKind.RBracket,
                    value = ']',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))
                pos.move(1)
            elif ch == '/':
                pos.move(1)
            elif ch == '"':
                token = self.tokenize_string(pos, code)
                if token:
                    tokens.append(token)
            elif (ch in string.ascii_letters or ch == '_'):
                token = self.tokenize_identifier(pos, code)
                if token:
                    tokens.append(token)
            elif ch in string.digits:
                token = self.tokenize_number(pos, code)
                if token:
                    tokens.append(token)
                pos.move(1)
            else:
                pos.move(1)

        return tokens

    def tokenize_identifier(self, pos, code):
        chars = []
        chars.append(code[pos.index])
        index = pos.index + 1
        while index < len(code):
            ch = code[index]
            if ch in string.ascii_letters or ch == '_' or ch in string.digits:
                chars.append(ch)
                index += 1
            else:
                break
        start_pos = deepcopy(pos)
        end_pos = deepcopy(pos)
        end_pos.index = (index - 1)
        count = index - pos.index
        pos.move(count)
        return Token(
            kind = TokenKind.Identifier,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )

    def tokenize_string(self, pos, code):
        chars = []
        quote_char = code[pos.index]
        index = pos.index + 1
        while index < len(code):
            ch = code[index]
            if ch == '\\':
                next_char = code[index+1]
                if next_char in ESCAPE_CHAR_MAP:
                    chars.append(ESCAPE_CHAR_MAP[next_char])
                else:
                    chars.append(next_char)
                index += 2
            elif ch == quote_char:
                index += 1
                break
            else:
                chars.append(ch)
                index += 1
        start_pos = deepcopy(pos)
        end_pos = deepcopy(pos)
        end_pos.index = (index - 1)
        count = index - pos.index
        pos.move(count)
        return Token(
            kind = TokenKind.StringLiteral,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )

    def tokenize_number(self, pos, code):
        chars = []
        quote_char = code[pos.index]
        index = pos.index + 1
        while index < len(code):
            ch = code[index]
            if ch == '\\':
                next_char = code[index+1]
                if next_char in ESCAPE_CHAR_MAP:
                    chars.append(ESCAPE_CHAR_MAP[next_char])
                else:
                    chars.append(next_char)
                index += 2
            elif ch == quote_char:
                index += 1
                break
            else:
                chars.append(ch)
                index += 1
        start_pos = deepcopy(pos)
        end_pos = deepcopy(pos)
        end_pos.index = (index - 1)
        count = index - pos.index
        pos.move(count)
        return Token(
            kind = TokenKind.StringLiteral,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )