from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
import string
from copy import deepcopy
# import pprint
# pp = pprint.PrettyPrinter(indent=4)

class TokenKind(Enum):
    Null = 1
    StringLiteral = 2
    NumberLiteral = 3
    ColorLiteral = 4
    Identifier = 5
    PropertyName = 6
    BoolLiteral = 7
    LineBreak = 8
    Comment = 9
    LBracket = 10
    RBracket = 11
    LBrace = 12
    RBrace = 13
    LParen = 14
    RParen = 15
    Colon = 16
    Comma = 17

    Mulitply = 21
    Division = 22
    Plus = 23
    Minus = 24
    Equal = 25
    Semicolon = 26


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
    Root = 1
    Null = 2
    Bool = 3
    String = 4
    Number = 5
    List = 6
    Object = 7


@dataclass
class SyntaxNode:
    kind: NodeKind
    start_pos: CharPosition
    end_pos: CharPosition
    value: str = field(default_factory=str)
    properties: Dict[str, SyntaxNode] = field(default_factory=dict)
    children: List[SyntaxNode] = field(default_factory=list)


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
            elif ch == ',':
                tokens.append(Token(
                    kind = TokenKind.Comma,
                    value = ',',
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
                    value = ';',
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
        kind = TokenKind.Identifier
        value = ''.join(chars)
        if chars[0] in string.ascii_lowercase:
            if value == 'true' or value == 'false':
                kind = TokenKind.BoolLiteral
            elif value == 'null':
                kind = TokenKind.Null
            else:
                kind = TokenKind.PropertyName
        return Token(
            kind = kind,
            value = value,
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
            pos.move(1)
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


class TokenStream:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def peek(self):
        if self.idx >= len(self.tokens):
            return None
        return self.tokens[self.idx]

    def peek_next(self, num = 0):
        if num < 0:
            raise Exception(f'TokenStream.peek_next num must >= 0, but {num} given.')
        new_idx = self.idx + num
        if new_idx >= len(self.tokens):
            return None
        return self.tokens[new_idx]

    def consume(self, kind):
        old_idx = self.idx
        idx = self.idx
        if isinstance(kind, (list, tuple)):
            kinds = kind
        else:
            kinds = [kind]
        while idx < len(self.tokens) and self.tokens[idx].kind in kinds:
            idx += 1
        self.idx = idx
        return self.idx - old_idx

    def expect(self, token_kind):
        token = self.peek()
        if isinstance(token_kind, (list, tuple)):
            expected_kinds =  token_kind
        else:
            expected_kinds = [token_kind]
        expected = token and token.kind in expected_kinds
        if not expected:
            raise HolaSyntaxError(message = f'Expect Token(token_kind), But {token.kind} Found.', pos=token.start_pos)
        else:
            self.next()

    def next(self):
        self.idx += 1
        if self.idx > len(self.tokens):
            self.idx = len(self.tokens)

    def move(self, steps):
        if steps < 0:
            raise Exception(f'TokenStream.move steps must >= 0, but {steps} given.')
        self.idx += steps
        if self.idx > len(self.tokens):
            self.idx = len(self.tokens)

    def eof(self):
        return self.idx >= len(self.tokens)

class HolaSyntaxError(Exception):
    def __init__(self, message, pos):
        self.message = message
        self.pos = pos
        new_message = f'Syntax Error (Line = {self.pos.line}, Column: {self.pos.column}): {self.message}'
        super().__init__(self, new_message)

class HolaSyntaxExpectError(Exception):
    def __init__(self, expect, found):
        self.pos = found.start_pos
        if not isinstance(expect, (list, tuple)):
            self.expect = [expect]
        else:
            self.expect = expect
        self.found = found
        expect_str = ', '.join(list(map(lambda x: repr(x), self.expect)))
        message = f'''Syntax Error (Line = {self.pos.line}, Column: {self.pos.column}):
    Expect token:  {expect_str}
    Found token: k={self.found.kind}, v="{self.found.value}"
    '''
        super().__init__(self, message)



class Parser:
    def __init__(self):
        pass

    def parse(self, code):
        tokenizer = Tokenizer()
        tokens = TokenStream(tokenizer.tokenize(code))
        root = SyntaxNode(
            kind = NodeKind.Root,
            start_pos = CharPosition(index = 0, line = 0, column = 0),
            end_pos = CharPosition(index = -1, line = -1, column = -1),
            value = '',
            properties = {},
            children = []
        )
        tokens.consume(TokenKind.LineBreak)
        while not tokens.eof():
            node = self.parse_object(tokens)
            root.children.append(node)
            tokens.consume(TokenKind.LineBreak)

        return root

    def parse_object(self, tokens):
        token = tokens.peek()
        name = ''
        if token.kind == TokenKind.Identifier:
            name = token.value
            tokens.next()
        elif token.kind == TokenKind.LBrace:
            pass
        else:
            raise HolaSyntaxExpectError([TokenKind.Identifier, TokenKind.LBrace], token)

        node = SyntaxNode(
            kind = NodeKind.Object,
            start_pos = deepcopy(token.start_pos),
            end_pos = CharPosition(index=-1, line=-1, column=-1),
            value = name,
            properties = {},
            children = []
        )
        tokens.expect(TokenKind.LBrace)
        tokens.consume([TokenKind.Comma, TokenKind.LineBreak])
        while not tokens.eof():
            token = tokens.peek()
            if token.kind == TokenKind.RBrace:
                break
            if token.kind in [TokenKind.PropertyName, TokenKind.StringLiteral]:
                name, value = self.parse_property(tokens)
                node.properties[name] = value
            elif token.kind in (TokenKind.Identifier, TokenKind.LBrace):
                sub_node = self.parse_object(tokens)
                node.children.append(sub_node)
            else:
                raise HolaSyntaxExpectError(
                    [TokenKind.StringLiteral, TokenKind.PropertyName, TokenKind.Identifier],
                    token
                )
            next_token = tokens.peek()
            if next_token.kind in [TokenKind.Comma, TokenKind.LineBreak]:
                tokens.next()
                tokens.consume(TokenKind.LineBreak)
                continue

        token = tokens.peek()
        node.end_pos = deepcopy(token.end_pos)
        tokens.expect(TokenKind.RBrace)
        return node

    def parse_property(self, tokens):
        token = tokens.peek()
        name = token.value
        tokens.next()
        tokens.expect(TokenKind.Colon)
        value = self.parse_value(tokens)
        return (name, value)

    def parse_value(self, tokens):
        token = tokens.peek()
        if token.kind == TokenKind.Null:
            tokens.next()
            return SyntaxNode(
                kind = NodeKind.Null,
                value = None,
                start_pos = deepcopy(token.start_pos),
                end_pos = deepcopy(token.end_pos)
            )
        elif token.kind == TokenKind.BoolLiteral:
            tokens.next()
            return SyntaxNode(
                kind = NodeKind.Bool,
                value = True if token.value == 'true' else False,
                start_pos = deepcopy(token.start_pos),
                end_pos = deepcopy(token.end_pos)
            )

        elif token.kind == TokenKind.StringLiteral:
            tokens.next()
            return SyntaxNode(
                kind = NodeKind.String,
                value = token.value,
                start_pos = deepcopy(token.start_pos),
                end_pos = deepcopy(token.end_pos)
            )

        elif token.kind == TokenKind.NumberLiteral:
            tokens.next()
            return SyntaxNode(
                kind = NodeKind.Number,
                value = token.value,
                start_pos = deepcopy(token.start_pos),
                end_pos = deepcopy(token.end_pos)
            )

        elif token.kind == TokenKind.LBracket:
            return self.parse_list(tokens)
        elif token.kind == TokenKind.Identifier or token.kind == TokenKind.LBrace:
            return self.parse_object(tokens)
        else:
            raise HolaSyntaxError(message=f'Unknown To Handle Token Kind {token.kind} and {token.value}')

    def parse_list(self, tokens):
        token = tokens.peek()
        node = SyntaxNode(
            kind = NodeKind.List,
            start_pos = deepcopy(token.start_pos),
            end_pos = CharPosition(index=-1, line=-1, column=-1),
            value = None,
            properties = {},
            children = []
        )
        tokens.expect(TokenKind.LBracket)
        tokens.consume(TokenKind.LineBreak)

        while not tokens.eof():
            token = tokens.peek()
            if token.kind == TokenKind.RBracket:
                break
            elif token.kind == TokenKind.Comma:
                node.children.append(node = SyntaxNode(
                    kind = NodeKind.Null,
                    start_pos = deepcopy(token.start_pos),
                    end_pos = deepcopy(token.start_pos),
                    value = None,
                    properties = {},
                    children = []
                ))
                tokens.consume(TokenKind.LineBreak)
                continue
            else:
                sub_node = self.parse_value(tokens)
                node.children.append(sub_node)
                next_token = tokens.peek()
                if next_token.kind in [TokenKind.Comma, TokenKind.LineBreak]:
                    tokens.next()
                    tokens.consume(TokenKind.LineBreak)
                    continue
                continue

        token = tokens.peek()
        node.end_pos = deepcopy(token.end_pos)
        tokens.expect(TokenKind.RBracket)
        return node

OBJECT_CATEGORY_MAP = {
    "page": "interfaces",
    "modal": "interfaces",
    "component": "interfaces",
    "action": "actions",
    "task": "actions",
    "currency": "objects",
    "variable": "objects",
    "item": "objects",
    "object-meta": "objects",
    "attribute": "objects"
}

class ObjectTreeCodeGenerator:
    def __init__(self):
        pass

    def gen(self, node):
        raw_obj_list = []
        for sub_node in node.children:
            assert sub_node.kind == NodeKind.Object
            obj = self.gen_object(sub_node)
            raw_obj_list.append(obj)

        json_obj_root = {}

        for obj in raw_obj_list:
            obj_type = obj["type"]

            category = OBJECT_CATEGORY_MAP.get(obj_type, "objects")
            category_objects = json_obj_root.setdefault(category, [])
            category_objects.append(obj)

        return json_obj_root

    def transform_obj_name(self, name):
        if not name:
            return name
        chars = []
        chars.append(name[0].lower())
        for char in name[1:]:
            if char in string.ascii_uppercase:
                chars.append('-')
                chars.append(char.lower())
            else:
                chars.append(char)
        return ''.join(chars)

    def gen_object(self, node):
        obj = {}
        if node.value.lower() != "object":
            if node.value:
                obj["type"] = self.transform_obj_name(node.value)
        for k, v in node.properties.items():
            if k.lower() == "type":
                continue
            obj[k] = self.gen_value(v)

        if node.children:
            child_key_name = "elements"
            obj[child_key_name] = []
            for child in node.children:
                obj[child_key_name].append(self.gen_value(child))

        return obj

    def gen_list(self, node):
        _list = []
        for sub_node in node.children:
            _list.append(self.gen_value(sub_node))
        return _list

    def gen_value(self, node):
        if node.kind == NodeKind.Null:
            return None
        elif node.kind == NodeKind.Bool:
            return node.value
        elif node.kind == NodeKind.Number:
            return node.value
        elif node.kind == NodeKind.String:
            return node.value
        elif node.kind == NodeKind.List:
            return self.gen_list(node)
        elif node.kind == NodeKind.Object:
            return self.gen_object(node)
        else:
            raise Exception('no generator function for Node(kind={node.kind})')


class Compiler:
    def __init__(self):
        pass

    def compile(self, code, target="object_tree"):
        parser = Parser()
        node = parser.parse(code)
        if target == 'object_tree':
            generator = ObjectTreeCodeGenerator()
            return generator.gen(node)
        else:
            raise Exception(f'Only target with object_tree supported.')