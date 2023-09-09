from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import string

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
class Token:
    kind: TokenKind
    value: str
    start_pos: int
    end_pos: int

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


class Tokenizer:
    def __init__(self):
        pass

    def tokenize(self, code):
        def handle_context():
            if len(context.chars) == 0:
                return
            if len(context.chars) == 1:
                tokens.append(Token(
                    kind = TokenKind.Identifier,
                    value = context.chars[0],
                    start_pos = context.start_pos,
                    end_pos = context.start_pos
                ))
            else:
                if context.chars[0] == '"' and context.chars[-1] == '"':
                    tokens.append(Token(
                        kind = TokenKind.StringLiteral,
                        value = ''.join(context.chars[1:-2]),
                        start_pos = context.start_pos,
                        end_pos = context.start_pos + len(context.chars) - 2
                    ))
                else:
                    tokens.append(Token(
                        kind = TokenKind.Identifier,
                        value = ''.join(context.chars),
                        start_pos = context.start_pos,
                        end_pos = context.start_pos + len(context.chars)
                    ))
        pos = 0
        tokens = []
        context = TokenizeContext(start_pos=pos, chars = [], in_str_literal = False)
        while pos < len(code):
            ch = code[pos]
            if ch == '{':
                handle_context()
                tokens.append(Token(
                    kind = TokenKind.LBrace,
                    value = '{',
                    start_pos = pos,
                    end_pos = pos
                ))

                pos += 1
                context = TokenizeContext(
                    start_pos = pos
                )
            elif ch == '}':
                handle_context()
                tokens.append(Token(
                    kind = TokenKind.RBrace,
                    value = '}',
                    start_pos = pos,
                    end_pos = pos
                ))

                pos += 1
                context = TokenizeContext(
                    start_pos = pos
                )
            elif ch == ':':
                pos += 1
            elif ch == '\n':
                pos += 1
            elif ch == '[':
                pos += 1
            elif ch == ']':
                pos += 1
            elif ch == '/':
                pos += 1
            elif (ch in string.ascii_letters or ch in string.digits or
                  ch == '.' or ch == '_'):
                context.chars.append(ch)
                pos += 1
            else:
                handle_context()
                pos += 1
                context = TokenizeContext(
                    start_pos = pos
                )
        handle_context()

        return tokens