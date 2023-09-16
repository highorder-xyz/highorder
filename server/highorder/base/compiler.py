from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import string
from copy import deepcopy

class TokenKind(Enum):
    Unknown = 1
    StringLiteral = 2
    NumberLiteral = 3
    ColorLiteral = 4
    Identifier = 5
    LineBreak = 8
    Comment = 9
    LBracket = 10
    RBracket = 11
    LBrace = 12
    RBrace = 13
    Colon = 14
    Mulitply = 15
    Division = 16
    Plus = 17
    Minus = 18
    Equal = 19
    Semicolon = 20


@dataclass
class CharPosition:
    index: int
    line: int
    column: int

    def move(self, num):
        if num == 0:
            return
        self.index += num
        self.column += num

    def moveto(self, new_pos):
        self.index = new_pos.index
        self.line = new_pos.line
        self.column = new_pos.column

    def newline(self):
        self.index += 1
        self.line += 1
        self.column = 1

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
    LineBreak = 10


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
                    kind = TokenKind.LineBreak,
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
            elif ch == ';':
                tokens.append(Token(
                    kind = TokenKind.Semicolon,
                    value = ']',
                    start_pos = deepcopy(pos),
                    end_pos = deepcopy(pos)
                ))
                pos.move(1)
            elif ch == '/':
                token = self.tokenize_comment_or_division(pos, code)
                if token:
                    tokens.append(token)
            elif ch == '"' or ch == "'":
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
        count = index - pos.index - 1
        pos.move(count)
        end_pos = deepcopy(pos)
        pos.move(1)
        return Token(
            kind = TokenKind.Identifier,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )

    def tokenize_string(self, pos, code):
        chars = []
        tmp_pos = deepcopy(pos)
        last_line_end_pos = None
        quote_char = code[pos.index]
        tmp_pos.move(1)
        while tmp_pos.index < len(code):
            index = tmp_pos.index
            ch = code[index]
            if ch == '\\':
                if index + 1 >= len(code):
                    chars.append(ch)
                    tmp_pos.move(1)
                    break
                next_char = code[index+1]
                if next_char in ESCAPE_CHAR_MAP:
                    chars.append(ESCAPE_CHAR_MAP[next_char])
                else:
                    chars.append(next_char)
                tmp_pos.move(2)
            elif ch == quote_char:
                tmp_pos.move(1)
                break
            elif ch == '\n':
                chars.append(ch)
                last_line_end_pos = deepcopy(tmp_pos)
                tmp_pos.newline()
            else:
                chars.append(ch)
                tmp_pos.move(1)
        start_pos = deepcopy(pos)
        if tmp_pos.index == 1:
            end_pos = last_line_end_pos
        else:
            end_pos = deepcopy(tmp_pos)
            end_pos.move(-1)

        pos.moveto(tmp_pos)

        return Token(
            kind = TokenKind.StringLiteral,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )

    def tokenize_number(self, pos, code):
        chars = []
        chars.append(code[pos.index])
        has_dot = False
        index = pos.index + 1
        while index < len(code):
            ch = code[index]
            if ch in string.digits:
                chars.append(ch)
                index += 1
            elif ch == '.':
                chars.append(ch)
                has_dot = True
                index += 1
            elif ch == '_':
                index += 1
            else:
                break
        start_pos = deepcopy(pos)
        count = index - pos.index - 1
        pos.move(count)
        end_pos = deepcopy(pos)
        pos.move(1)

        raw_value = ''.join(chars)
        if not has_dot:
            value = int(raw_value)
        else:
            value = float(raw_value)
        return Token(
            kind = TokenKind.NumberLiteral,
            value = value,
            start_pos = start_pos,
            end_pos = end_pos
        )

    def tokenize_comment_or_division(self, pos, code):
        chars = []
        index = pos.index + 1
        if (index < len(code) and code[index] != '/') or (index == len(code)):
            return Token(
                kind = TokenKind.Division ,
                value = '/',
                start_pos = deepcopy(pos),
                end_pos = deepcopy(pos)
            )

        index += 1
        while index < len(code):
            ch = code[index]
            if ch == '\n':
                break
            else:
                chars.append(ch)
                index += 1
        start_pos = deepcopy(pos)
        count = index - pos.index - 1
        pos.move(count)
        end_pos = deepcopy(pos)
        pos.move(1)

        return Token(
            kind = TokenKind.Comment,
            value = ''.join(chars),
            start_pos = start_pos,
            end_pos = end_pos
        )