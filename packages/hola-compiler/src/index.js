

export const TokenKind = Object.freeze({
    Null: 1,
    StringLiteral: 2,
    NumberLiteral: 3,
    ColorLiteral: 4,
    Identifier: 5,
    PropertyName: 6,
    BoolLiteral: 7,
    LineBreak: 8,
    Comment: 9,
    LBracket: 10,
    RBracket: 11,
    LBrace: 12,
    RBrace: 13,
    LParen: 14,
    RParen: 15,
    Colon: 16,
    Comma: 17,
    Mulitply: 21,
    Division: 22,
    Plus: 23,
    Minus: 24,
    Equal: 25,
    Semicolon: 26,
    Dot: 27
});


class CharPosition {
    constructor(index, line, column) {
        this.index = index;
        this.line = line;
        this.column = column;
    }
    move(num) {
        if (num === 0) {
            return;
        }
        this.index += num;
        this.column += num;
    }
    moveto(new_pos) {
        this.index = new_pos.index;
        this.line = new_pos.line;
        this.column = new_pos.column;
    }
    newline() {
        this.index += 1;
        this.line += 1;
        this.column = 1;
    }
    clone() {
        return new CharPosition(
            this.index,
            this.line,
            this.column
        )
    }
}

export class Token {
    constructor(kind, value, start_pos, end_pos) {
        this.kind = kind;
        this.value = value;
        this.start_pos = start_pos;
        this.end_pos = end_pos;
    }
}

class TokenizeContext {
    constructor(start_pos, chars=[], in_str_literal=false, is_number=false) {
        this.start_pos = start_pos;
        this.chars = chars;
        this.in_str_literal = in_str_literal;
        this.is_number = is_number;
    }
}

export const NodeKind = Object.freeze({
    Root: 1,
    Null: 2,
    Bool: 3,
    String: 4,
    Number: 5,
    List: 6,
    Object: 7
});

class SyntaxNode {
    constructor(kind, start_pos, end_pos, value="", properties={}, children=[]) {
        this.kind = kind;
        this.start_pos = start_pos;
        this.end_pos = end_pos;
        this.value = value;
        this.properties = properties;
        this.children = children;
    }
}

const ESCAPE_CHAR_MAP = {
    "n": "\n",
    "r": "\r",
    "t": "\t",
    "v": "\v",
    "b": "\b",
    "f": "\f",
    "a": "\a",
};

export class Tokenizer {
    constructor() {
    }
    tokenize(code) {
        let pos = new CharPosition(0, 0, 0);
        let tokens = [];
        while (pos.index < code.length) {
            let ch = code[pos.index];
            if (ch === "{") {
                tokens.push(new Token(
                    TokenKind.LBrace,
                    "{",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === "}") {
                tokens.push(new Token(
                    TokenKind.RBrace,
                    "}",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === ":") {
                tokens.push(new Token(
                    TokenKind.Colon,
                    ":",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === "\n") {
                tokens.push(new Token(
                    TokenKind.LineBreak,
                    "\n",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === ",") {
                tokens.push(new Token(
                    TokenKind.Comma,
                    ",",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === "[") {
                tokens.push(new Token(
                    TokenKind.LBracket,
                    "[",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === "]") {
                tokens.push(new Token(
                    TokenKind.RBracket,
                    "]",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === ".") {
                tokens.push(new Token(
                    TokenKind.Dot,
                    ".",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === ";") {
                tokens.push(new Token(
                    TokenKind.Semicolon,
                    ";",
                    new CharPosition(pos.index, pos.line, pos.column),
                    new CharPosition(pos.index, pos.line, pos.column)
                ));
                pos.move(1);
            } else if (ch === "/") {
                let token = this.tokenize_comment_or_division(pos, code);
                if (token) {
                    tokens.push(token);
                }
            } else if (ch === '"' || ch === "'") {
                let token = this.tokenize_string(pos, code);
                if (token) {
                    tokens.push(token);
                }
            } else if (ch.match(/[a-zA-Z_]/)) {
                let token = this.tokenize_identifier(pos, code);
                if (token) {
                    tokens.push(token);
                }
            } else if (ch.match(/[0-9]/)) {
                let token = this.tokenize_number(pos, code);
                if (token) {
                    tokens.push(token);
                }
            } else {
                pos.move(1);
            }
        }
        return tokens;
    }
    tokenize_identifier(pos, code) {
        let chars = [];
        chars.push(code[pos.index]);
        let index = pos.index + 1;
        while (index < code.length) {
            let ch = code[index];
            if (ch.match(/[a-zA-Z_]/) || ch.match(/[0-9]/)) {
                chars.push(ch);
                index += 1;
            } else {
                break;
            }
        }
        let start_pos = new CharPosition(pos.index, pos.line, pos.column);
        let count = index - pos.index - 1;
        pos.move(count);
        let end_pos = new CharPosition(pos.index, pos.line, pos.column);
        pos.move(1);
        let kind = TokenKind.Identifier;
        let value = chars.join("");
        if (chars[0].match(/[a-z]/)) {
            if (value === "true" || value === "false") {
                kind = TokenKind.BoolLiteral;
            } else if (value === "null") {
                kind = TokenKind.Null;
            } else {
                kind = TokenKind.PropertyName;
            }
        }
        return new Token(kind, value, start_pos, end_pos);
    }
    tokenize_string(pos, code) {
        let chars = [];
        let tmp_pos = new CharPosition(pos.index, pos.line, pos.column);
        let last_line_end_pos = null;
        let quote_char = code[pos.index];
        tmp_pos.move(1);
        while (tmp_pos.index < code.length) {
            let index = tmp_pos.index;
            let ch = code[index];
            if (ch === "\\") {
                if (index + 1 >= code.length) {
                    chars.push(ch);
                    tmp_pos.move(1);
                    break;
                }
                let next_char = code[index + 1];
                if (next_char in ESCAPE_CHAR_MAP) {
                    chars.push(ESCAPE_CHAR_MAP[next_char]);
                } else {
                    chars.push(next_char);
                }
                tmp_pos.move(2);
            } else if (ch === quote_char) {
                tmp_pos.move(1);
                break;
            } else if (ch === "\n") {
                chars.push(ch);
                last_line_end_pos = new CharPosition(tmp_pos.index, tmp_pos.line, tmp_pos.column);
                tmp_pos.newline();
            } else {
                chars.push(ch);
                tmp_pos.move(1);
            }
        }
        let start_pos = new CharPosition(pos.index, pos.line, pos.column);
        let end_pos = null;
        if (tmp_pos.index === 1) {
            end_pos = last_line_end_pos;
        } else {
            end_pos = new CharPosition(tmp_pos.index, tmp_pos.line, tmp_pos.column);
            end_pos.move(-1);
        }
        pos.moveto(tmp_pos);
        return new Token(
            TokenKind.StringLiteral,
            chars.join(""),
            start_pos,
            end_pos
        );
    }
    tokenize_number(pos, code) {
        let chars = [];
        chars.push(code[pos.index]);
        let has_dot = false;
        let index = pos.index + 1;
        while (index < code.length) {
            let ch = code[index];
            if (ch.match(/[0-9]/)) {
                chars.push(ch);
                index += 1;
            } else if (ch === ".") {
                chars.push(ch);
                has_dot = true;
                index += 1;
            } else if (ch === "_") {
                index += 1;
            } else {
                break;
            }
        }
        let start_pos = new CharPosition(pos.index, pos.line, pos.column);
        let count = index - pos.index - 1;
        pos.move(count);
        let end_pos = new CharPosition(pos.index, pos.line, pos.column);
        pos.move(1);
        let raw_value = chars.join("");
        let value = null;
        if (!has_dot) {
            value = parseInt(raw_value);
        } else {
            value = parseFloat(raw_value);
        }
        return new Token(
            TokenKind.NumberLiteral,
            value,
            start_pos,
            end_pos
        );
    }
    tokenize_block_comment(pos, code) {
        // pos is currently at '/', next char is '*'
        let chars = [];
        let tmp_pos = new CharPosition(pos.index, pos.line, pos.column);
        const start_pos = tmp_pos.clone();

        // consume '/*'
        tmp_pos.move(2);

        while (tmp_pos.index < code.length) {
            const ch = code[tmp_pos.index];
            const next = tmp_pos.index + 1 < code.length ? code[tmp_pos.index + 1] : null;
            if (ch === "*" && next === "/") {
                tmp_pos.move(2);
                break;
            }
            if (ch === "\n") {
                chars.push(ch);
                tmp_pos.newline();
                continue;
            }
            chars.push(ch);
            tmp_pos.move(1);
        }

        let end_pos = tmp_pos.clone();
        end_pos.move(-1);
        pos.moveto(tmp_pos);
        return new Token(TokenKind.Comment, chars.join(""), start_pos, end_pos);
    }
    tokenize_comment_or_division(pos, code) {
        let index = pos.index + 1;
        if (index >= code.length) {
            let start_pos = new CharPosition(pos.index, pos.line, pos.column);
            pos.move(1);
            return new Token(TokenKind.Division, "/", start_pos, start_pos);
        }

        // block comment: /* ... */
        if (code[index] === "*") {
            return this.tokenize_block_comment(pos, code);
        }

        // division
        if (code[index] !== "/") {
            let start_pos = new CharPosition(pos.index, pos.line, pos.column);
            pos.move(1);
            return new Token(TokenKind.Division, "/", start_pos, start_pos);
        }

        // line comment: // ... (until newline)
        let chars = [];
        index += 1;
        while (index < code.length) {
            let ch = code[index];
            if (ch === "\n") {
                break;
            } else {
                chars.push(ch);
                index += 1;
            }
        }
        let start_pos = new CharPosition(pos.index, pos.line, pos.column);
        let count = index - pos.index - 1;
        pos.move(count);
        let end_pos = new CharPosition(pos.index, pos.line, pos.column);
        pos.move(1);
        return new Token(TokenKind.Comment, chars.join(""), start_pos, end_pos);
    }
}

class TokenStream {
    constructor(tokens) {
        this.tokens = tokens;
        this.idx = 0;
    }
    peek() {
        if (this.idx >= this.tokens.length) {
            return null;
        }
        return this.tokens[this.idx];
    }
    peek_next(num=0) {
        if (num < 0) {
            throw new Error(`TokenStream.peek_next num must >= 0, but ${num} given.`);
        }
        let new_idx = this.idx + num;
        if (new_idx >= this.tokens.length) {
            return null;
        }
        return this.tokens[new_idx];
    }
    consume(kind) {
        let old_idx = this.idx;
        let idx = this.idx;
        let kinds = null;
        if (Array.isArray(kind)) {
            kinds = kind;
        } else {
            kinds = [kind];
        }
        while (idx < this.tokens.length && kinds.includes(this.tokens[idx].kind)) {
            idx += 1;
        }
        this.idx = idx;
        return this.idx - old_idx;
    }
    expect(token_kind) {
        let token = this.peek();
        let expected_kinds = null;
        if (Array.isArray(token_kind)) {
            expected_kinds = token_kind;
        } else {
            expected_kinds = [token_kind];
        }
        let expected = token && expected_kinds.includes(token.kind);
        if (!expected) {
            throw new HolaSyntaxError(
                `Expect Token(token_kind), But ${token.kind} Found.`,
                token.start_pos
            );
        } else {
            this.next();
        }
    }
    next() {
        this.idx += 1;
        if (this.idx > this.tokens.length) {
            this.idx = this.tokens.length;
        }
    }
    move(steps) {
        if (steps < 0) {
            throw new Error(`TokenStream.move steps must >= 0, but ${steps} given.`);
        }
        this.idx += steps;
        if (this.idx > this.tokens.length) {
            this.idx = this.tokens.length;
        }
    }
    eof() {
        return this.idx >= this.tokens.length;
    }
}

class HolaSyntaxError extends Error {
    constructor(message, pos) {
        super(message);
        this.pos = pos;
        this.name = "HolaSyntaxError";
        this.message = `Syntax Error (Line = ${this.pos.line}, Column: ${this.pos.column}): ${this.message}`;
    }
}

class HolaSyntaxExpectError extends Error {
    constructor(expect, found) {
        const pos = found.start_pos;
        const expect_list = Array.isArray(expect) ? expect : [expect];
        const expect_str = expect_list.map(x => JSON.stringify(x)).join(", ");
        const message = `Expect ${expect_str}, But ${found.kind} Found.`;
        super(message);
        this.pos = pos;
        this.expect = expect_list;
        this.found = found;
        this.name = "HolaSyntaxExpectError";
    }
}

export class Parser {
    constructor() {
    }
    parse(code) {
        const tokenizer = new Tokenizer();
        const tokens = new TokenStream(tokenizer.tokenize(code));
        const root = new SyntaxNode(
            NodeKind.Root,
            new CharPosition(0, 0, 0),
            new CharPosition(-1, -1, -1),
            "",
            {},
            []
        );
        tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
        while (!tokens.eof()) {
            const node = this.parse_object(tokens);
            root.children.push(node);
            tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
        }
        return root;
    }
    parse_object(tokens) {
        tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
        const token = tokens.peek();
        let name = "";
        if (token.kind === TokenKind.Identifier) {
            name = token.value;
            tokens.next();
            while (true) {
                const dot = tokens.peek();
                const next = tokens.peek_next(1);
                if (!dot || dot.kind !== TokenKind.Dot) {
                    break;
                }
                if (!next || next.kind !== TokenKind.Identifier) {
                    break;
                }
                tokens.next();
                tokens.next();
                name = `${name}.${next.value}`;
            }
        } else if (token.kind === TokenKind.LBrace) {
            // pass
        } else {
            throw new HolaSyntaxExpectError([TokenKind.Identifier, TokenKind.LBrace], token);
        }
        const node = new SyntaxNode(
            NodeKind.Object,
            token.start_pos.clone(),
            new CharPosition(-1, -1, -1),
            name,
            {},
            []
        );
        tokens.expect(TokenKind.LBrace);
        tokens.consume([TokenKind.Comma, TokenKind.LineBreak, TokenKind.Comment]);
        while (!tokens.eof()) {
            const token = tokens.peek();
            if (token.kind === TokenKind.Comment) {
                tokens.next();
                tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
                continue;
            }
            if (token.kind === TokenKind.RBrace) {
                break;
            }
            if ([TokenKind.PropertyName, TokenKind.StringLiteral].includes(token.kind)) {
                const [name, value] = this.parse_property(tokens);
                node.properties[name] = value;
            } else if ([TokenKind.Identifier, TokenKind.LBrace].includes(token.kind)) {
                const sub_node = this.parse_object(tokens);
                node.children.push(sub_node);
            } else {
                throw new HolaSyntaxExpectError(
                    [
                        TokenKind.StringLiteral,
                        TokenKind.PropertyName,
                        TokenKind.Identifier,
                    ],
                    token
                );
            }
            const next_token = tokens.peek();
            if ([TokenKind.Comma, TokenKind.LineBreak, TokenKind.Comment].includes(next_token.kind)) {
                tokens.next();
                tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
                continue;
            }
        }
        const last_token = tokens.peek();
        node.end_pos = last_token.end_pos.clone();
        tokens.expect(TokenKind.RBrace);
        return node;
    }
    parse_property(tokens) {
        const token = tokens.peek();
        const name = token.value;
        tokens.next();
        tokens.expect(TokenKind.Colon);
        const value = this.parse_value(tokens);
        return [name, value];
    }
    parse_value(tokens) {
        const token = tokens.peek();
        if (token.kind === TokenKind.Null) {
            tokens.next();
            return new SyntaxNode(
                NodeKind.Null,
                token.start_pos.clone(),
                token.end_pos.clone(),
                null
            );
        } else if (token.kind === TokenKind.BoolLiteral) {
            tokens.next();
            return new SyntaxNode(
                NodeKind.Bool,
                token.start_pos.clone(),
                token.end_pos.clone(),
                token.value === "true" ? true : false
            );
        } else if (token.kind === TokenKind.StringLiteral) {
            tokens.next();
            return new SyntaxNode(
                NodeKind.String,
                token.start_pos.clone(),
                token.end_pos.clone(),
                token.value
            );
        } else if (token.kind === TokenKind.NumberLiteral) {
            tokens.next();
            return new SyntaxNode(
                NodeKind.Number,
                token.start_pos.clone(),
                token.end_pos.clone(),
                token.value
            );
        } else if (token.kind === TokenKind.LBracket) {
            return this.parse_list(tokens);
        } else if ([TokenKind.Identifier, TokenKind.LBrace].includes(token.kind)) {
            return this.parse_object(tokens);
        } else {
            throw new HolaSyntaxError(
                `Unknown To Handle Token Kind ${token.kind} and ${token.value}`,
                token.start_pos
            );
        }
    }
    parse_list(tokens) {
        const token = tokens.peek();
        const node = new SyntaxNode(
            NodeKind.List,
            token.start_pos.clone(),
            new CharPosition(-1, -1, -1),
            null,
            {},
            []
        );
        tokens.expect(TokenKind.LBracket);
        tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
        while (!tokens.eof()) {
            const token = tokens.peek();
            if (token.kind === TokenKind.RBracket) {
                break;
            } else if (token.kind === TokenKind.Comment) {
                tokens.next();
                tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
                continue;
            } else if (token.kind === TokenKind.Comma) {
                node.children.push(
                    new SyntaxNode(
                        NodeKind.Null,
                        token.start_pos.clone(),
                        token.start_pos.clone(),
                        null,
                        {},
                        []
                    )
                );
                tokens.next();
                tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
                continue;
            } else {
                const sub_node = this.parse_value(tokens);
                node.children.push(sub_node);
                const next_token = tokens.peek();
                if ([TokenKind.Comma, TokenKind.LineBreak, TokenKind.Comment].includes(next_token.kind)) {
                    tokens.next();
                    tokens.consume([TokenKind.LineBreak, TokenKind.Comment]);
                    continue;
                }
                continue;
            }
        }
        const last_token = tokens.peek();
        node.end_pos = last_token.end_pos.clone();
        tokens.expect(TokenKind.RBracket);
        return node;
    }
}

const OBJECT_CATEGORY_MAP = {
    "page": "interfaces",
    "modal": "interfaces",
    "component": "interfaces",
    "action": "actions",
    "task": "actions",
    "currency": "objects",
    "variable": "objects",
    "item": "objects",
    "object-meta": "objects",
    "attribute": "objects",
};

class ObjectTreeCodeGenerator {
    constructor() {
    }
    gen(node) {
        const raw_obj_list = [];
        for (const sub_node of node.children) {
            const obj = this.gen_object(sub_node);
            raw_obj_list.push(obj);
        }
        const json_obj_root = {};
        for (const obj of raw_obj_list) {
            const obj_type = obj["type"];
            const category = OBJECT_CATEGORY_MAP[obj_type] || "objects";
            const category_objects = json_obj_root[category] || [];
            category_objects.push(obj);
            json_obj_root[category] = category_objects;
        }
        return json_obj_root;
    }
    transform_obj_name(name) {
        if (!name) {
            return name;
        }
        const chars = [];
        chars.push(name[0].toLowerCase());
        for (let i = 1; i < name.length; i++) {
            const char = name[i];
            if (char.match(/[A-Z]/)) {
                chars.push("-");
                chars.push(char.toLowerCase());
            } else {
                chars.push(char);
            }
        }
        return chars.join("");
    }
    gen_object(node) {
        const obj = {};
        if (node.value.toLowerCase() !== "object") {
            if (node.value) {
                obj["type"] = this.transform_obj_name(node.value);
            }
        }
        for (const [k, v] of Object.entries(node.properties)) {
            if (k.toLowerCase() === "type") {
                continue;
            }
            obj[k] = this.gen_value(v);
        }
        if (node.children.length > 0) {
            const child_key_name = "elements";
            obj[child_key_name] = [];
            for (const child of node.children) {
                obj[child_key_name].push(this.gen_value(child));
            }
        }
        return obj;
    }
    gen_list(node) {
        const _list = [];
        for (const sub_node of node.children) {
            _list.push(this.gen_value(sub_node));
        }
        return _list;
    }
    gen_value(node) {
        if (node.kind === NodeKind.Null) {
            return null;
        } else if (node.kind === NodeKind.Bool) {
            return node.value;
        } else if (node.kind === NodeKind.Number) {
            return node.value;
        } else if (node.kind === NodeKind.String) {
            return node.value;
        } else if (node.kind === NodeKind.List) {
            return this.gen_list(node);
        } else if (node.kind === NodeKind.Object) {
            return this.gen_object(node);
        } else {
            throw new Error(`no generator function for Node(kind=${node.kind})`);
        }
    }
}

export class Compiler {
    constructor() {
    }
    compile(code, target = "object_tree") {
        const parser = new Parser();
        const node = parser.parse(code);
        if (target === "object_tree") {
            const generator = new ObjectTreeCodeGenerator();
            return generator.gen(node);
        } else {
            throw new Error(`Only target with object_tree supported.`);
        }
    }
}


