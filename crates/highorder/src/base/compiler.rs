use std::collections::HashMap;
use std::string::String;
use std::fmt;
use serde_json::{Value, Number, Map};
use std::str::FromStr;
use lazy_static::lazy_static;

#[derive(Debug, PartialEq, Eq, Clone)]
enum TokenKind {
    Null = 1,
    StringLiteral = 2,
    NumberLiteral = 3,
    ColorLiteral = 4,
    Identifier = 5,
    PropertyName = 6,
    BoolLiteral = 7,
    LineBreak = 8,
    Comment = 9,
    LBracket = 10,
    RBracket = 11,
    LBrace = 12,
    RBrace = 13,
    LParen = 14,
    RParen = 15,
    Colon = 16,
    Comma = 17,
    Mulitply = 21,
    Division = 22,
    Plus = 23,
    Minus = 24,
    Equal = 25,
    Semicolon = 26,
}

impl fmt::Display for TokenKind {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

#[derive(Debug, PartialEq, Eq, Clone)]
struct CharPosition {
    index: i32,
    line: i32,
    column: i32,
}

impl CharPosition {
    fn move_num(&mut self, num: i32) {
        if num == 0 {
            return;
        }
        self.index += num;
        self.column += num;
    }

    fn moveto(&mut self, new_pos: &CharPosition) {
        self.index = new_pos.index;
        self.line = new_pos.line;
        self.column = new_pos.column;
    }

    fn newline(&mut self) {
        self.index += 1;
        self.line += 1;
        self.column = 1;
    }

}

#[derive(Debug, PartialEq, Eq, Clone)]
struct Token {
    kind: TokenKind,
    value: String,
    start_pos: CharPosition,
    end_pos: CharPosition,
}

#[derive(Debug, PartialEq, Eq)]
struct TokenizeContext {
    start_pos: i32,
    chars: Vec<char>,
    in_str_literal: bool,
    is_number: bool,
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
enum NodeKind {
    Root = 1,
    Null = 2,
    Bool = 3,
    String = 4,
    Number = 5,
    List = 6,
    Object = 7,
}

#[derive(Debug, PartialEq, Eq)]
struct SyntaxNode {
    kind: NodeKind,
    start_pos: CharPosition,
    end_pos: CharPosition,
    value: String,
    properties: HashMap<String, SyntaxNode>,
    children: Vec<SyntaxNode>,
}

lazy_static! {
static ref ESCAPE_CHAR_MAP: HashMap<char, char> = [
    ('n', '\n'),
    ('r', '\r'),
    ('t', '\t'),
    ('v', '\x0B'),
    ('b', '\x08'),
    ('f', '\x0C'),
    ('a', '\x07'),
]
.iter()
.cloned()
.collect();
}


struct Tokenizer {}

impl Tokenizer {
    fn new() -> Self {
        Tokenizer {}
    }

    fn tokenize(&self, code: &str) -> Vec<Token> {
        let mut pos = CharPosition {
            index: 0,
            line: 0,
            column: 0,
        };
        let mut tokens = Vec::new();
        let chars: Vec<char> = code.chars().collect();
        let context = TokenizeContext {
            start_pos: 0,
            chars,
            in_str_literal: false,
            is_number: false,
        };

        while pos.index < context.chars.len() as i32 {
            let ch = context.chars[pos.index as usize];
            if ch == '{' {
                tokens.push(Token {
                    kind: TokenKind::LBrace,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == '}' {
                tokens.push(Token {
                    kind: TokenKind::RBrace,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == ':' {
                tokens.push(Token {
                    kind: TokenKind::Colon,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == '\n' {
                tokens.push(Token {
                    kind: TokenKind::LineBreak,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == ',' {
                tokens.push(Token {
                    kind: TokenKind::Comma,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == '[' {
                tokens.push(Token {
                    kind: TokenKind::LBracket,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == ']' {
                tokens.push(Token {
                    kind: TokenKind::RBracket,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == ';' {
                tokens.push(Token {
                    kind: TokenKind::Semicolon,
                    value: ch.to_string(),
                    start_pos: pos.clone(),
                    end_pos: pos.clone(),
                });
                pos.move_num(1);
            } else if ch == '/' {
                let token = self.tokenize_comment_or_division(&mut pos, &context);
                if let Some(token) = token {
                    tokens.push(token);
                }
            } else if ch == '"' || ch == '\'' {
                let token = self.tokenize_string(&mut pos, &context);
                if let Some(token) = token {
                    tokens.push(token);
                }
            } else if ch.is_ascii_alphabetic() || ch == '_' {
                let token = self.tokenize_identifier(&mut pos, &context);
                if let Some(token) = token {
                    tokens.push(token);
                }
            } else if ch.is_ascii_digit() {
                let token = self.tokenize_number(&mut pos, &context);
                if let Some(token) = token {
                    tokens.push(token);
                }
            } else {
                pos.move_num(1);
            }
        }

        tokens
    }

    fn tokenize_identifier(
        &self,
        pos: &mut CharPosition,
        context: &TokenizeContext,
    ) -> Option<Token> {
        let mut chars = Vec::new();
        chars.push(context.chars[pos.index as usize]);
        let mut index = pos.index + 1;
        while index < context.chars.len() as i32 {
            let ch = context.chars[index as usize];
            if ch.is_ascii_alphanumeric() || ch == '_' {
                chars.push(ch);
                index += 1;
            } else {
                break;
            }
        }
        let start_pos = pos.clone();
        let count = index - pos.index - 1;
        pos.move_num(count);
        let end_pos = pos.clone();
        pos.move_num(1);
        let value: String = chars.iter().collect();
        let kind = if chars[0].is_ascii_lowercase() {
            if value == "true" || value == "false" {
                TokenKind::BoolLiteral
            } else if value == "null" {
                TokenKind::Null
            } else {
                TokenKind::PropertyName
            }
        } else {
            TokenKind::Identifier
        };
        Some(Token {
            kind,
            value,
            start_pos,
            end_pos,
        })
    }

    fn tokenize_string(
        &self,
        pos: &mut CharPosition,
        context: &TokenizeContext,
    ) -> Option<Token> {
        let mut chars = Vec::new();
        let mut tmp_pos = pos.clone();
        let mut last_line_end_pos = None;
        let quote_char = context.chars[pos.index as usize];
        tmp_pos.move_num(1);
        while tmp_pos.index < context.chars.len() as i32 {
            let index = tmp_pos.index as usize;
            let ch = context.chars[index];
            if ch == '\\' {
                if index + 1 >= context.chars.len() {
                    chars.push(ch);
                    tmp_pos.move_num(1);
                    break;
                }
                let next_char = context.chars[index + 1];
                if let Some(escaped_char) = ESCAPE_CHAR_MAP.get(&next_char) {
                    chars.push(*escaped_char);
                } else {
                    chars.push(next_char);
                }
                tmp_pos.move_num(2);
            } else if ch == quote_char {
                tmp_pos.move_num(1);
                break;
            } else if ch == '\n' {
                chars.push(ch);
                last_line_end_pos = Some(tmp_pos.clone());
                tmp_pos.newline();
            } else {
                chars.push(ch);
                tmp_pos.move_num(1);
            }
        }
        let start_pos = pos.clone();
        let end_pos = if tmp_pos.index == 1 {
            last_line_end_pos.unwrap()
        } else {
            let mut end_pos = tmp_pos.clone();
            end_pos.move_num(-1);
            end_pos
        };
        pos.moveto(&tmp_pos);
        Some(Token {
            kind: TokenKind::StringLiteral,
            value: chars.iter().collect(),
            start_pos,
            end_pos,
        })
    }

    fn tokenize_number(
        &self,
        pos: &mut CharPosition,
        context: &TokenizeContext,
    ) -> Option<Token> {
        let mut chars = Vec::new();
        chars.push(context.chars[pos.index as usize]);
        let mut has_dot = false;
        let mut index = pos.index + 1;
        while index < context.chars.len() as i32 {
            let ch = context.chars[index as usize];
            if ch.is_ascii_digit() {
                chars.push(ch);
                index += 1;
            } else if ch == '.' {
                chars.push(ch);
                has_dot = true;
                index += 1;
            } else if ch == '_' {
                index += 1;
            } else {
                break;
            }
        }
        let start_pos = pos.clone();
        let count = index - pos.index - 1;
        pos.move_num(count);
        let end_pos = pos.clone();
        pos.move_num(1);
        let raw_value: String = chars.iter().collect();
        let value = if !has_dot {
            raw_value.parse::<i32>().unwrap().to_string()
        } else {
            raw_value.parse::<f32>().unwrap().to_string()
        };
        Some(Token {
            kind: TokenKind::NumberLiteral,
            value: value,
            start_pos,
            end_pos,
        })
    }

    fn tokenize_comment_or_division(
        &self,
        pos: &mut CharPosition,
        context: &TokenizeContext,
    ) -> Option<Token> {
        let mut chars = Vec::new();
        let mut index = pos.index + 1;
        if (index < context.chars.len() as i32 && context.chars[index as usize] != '/')
            || index == context.chars.len() as i32
        {
            pos.move_num(1);
            return Some(Token {
                kind: TokenKind::Division,
                value: "/".to_string(),
                start_pos: pos.clone(),
                end_pos: pos.clone(),
            });
        }
        index += 1;
        while index < context.chars.len() as i32 {
            let ch = context.chars[index as usize];
            if ch == '\n' {
                break;
            } else {
                chars.push(ch);
                index += 1;
            }
        }
        let start_pos = pos.clone();
        let count = index - pos.index - 1;
        pos.move_num(count);
        let end_pos = pos.clone();
        pos.move_num(1);
        Some(Token {
            kind: TokenKind::Comment,
            value: chars.iter().collect(),
            start_pos,
            end_pos,
        })
    }
}

struct TokenStream {
    tokens: Vec<Token>,
    idx: usize,
}

impl TokenStream {
    fn new(tokens: Vec<Token>) -> Self {
        TokenStream { tokens, idx: 0 }
    }

    fn peek(&self) -> Option<&Token> {
        if self.idx >= self.tokens.len() {
            return None;
        }
        Some(&self.tokens[self.idx])
    }

    fn peek_next(&self, num: usize) -> Option<&Token> {
        if num < 0 {
            panic!("TokenStream.peek_next num must >= 0, but {} given.", num);
        }
        let new_idx = self.idx + num;
        if new_idx >= self.tokens.len() {
            return None;
        }
        Some(&self.tokens[new_idx])
    }

    fn consume(&mut self, kind: TokenKind) -> usize {
        let old_idx = self.idx;
        let mut idx = self.idx;
        while idx < self.tokens.len() && self.tokens[idx].kind == kind {
            idx += 1;
        }
        self.idx = idx;
        self.idx - old_idx
    }

    fn consume_any(&mut self, kinds: &[TokenKind]) -> usize {
        let old_idx = self.idx;
        let mut idx = self.idx;
        while idx < self.tokens.len() && kinds.contains(&self.tokens[idx].kind) {
            idx += 1;
        }
        self.idx = idx;
        self.idx - old_idx
    }

    fn expect(&mut self, token_kind: TokenKind) {
        let token = self.peek().unwrap();
        let expected = token.kind == token_kind;
        if !expected {
            panic!(
                "Expect Token({:?}), But {:?} Found.",
                token_kind, token.kind
            );
        } else {
            self.next();
        }
    }

    fn next(&mut self) {
        self.idx += 1;
        if self.idx > self.tokens.len() {
            self.idx = self.tokens.len();
        }
    }

    fn move_num(&mut self, steps: usize) {
        if steps < 0 {
            panic!("TokenStream.move_num steps must >= 0, but {} given.", steps);
        }
        self.idx += steps;
        if self.idx > self.tokens.len() {
            self.idx = self.tokens.len();
        }
    }

    fn eof(&self) -> bool {
        self.idx >= self.tokens.len()
    }
}

#[derive(Debug)]
struct HolaSyntaxError {
    message: String,
    pos: CharPosition,
}

impl HolaSyntaxError {
    fn new(message: String, pos: CharPosition) -> Self {
        let new_message = format!(
            "Syntax Error (Line = {}, Column: {}): {}",
            pos.line, pos.column, message
        );
        HolaSyntaxError {
            message: new_message,
            pos,
        }
    }
}

#[derive(Debug)]
struct HolaSyntaxExpectError {
    expect: Vec<TokenKind>,
    found: Token,
    pos: CharPosition,
}

impl HolaSyntaxExpectError {
    fn new(expect: Vec<TokenKind>, found: Token) -> Self {
        let pos = found.start_pos.clone();
        HolaSyntaxExpectError { expect, found, pos }
    }
}

#[derive(Debug)]
struct Parser {}

impl Parser {
    fn new() -> Self {
        Parser {}
    }

    fn parse(&self, code: &str) -> SyntaxNode {
        let tokenizer = Tokenizer::new();
        let mut tokens = TokenStream::new(tokenizer.tokenize(code));
        let mut root = SyntaxNode {
            kind: NodeKind::Root,
            start_pos: CharPosition {
                index: 0,
                line: 0,
                column: 0,
            },
            end_pos: CharPosition {
                index: -1,
                line: -1,
                column: -1,
            },
            value: String::new(),
            properties: HashMap::new(),
            children: Vec::new(),
        };
        tokens.consume(TokenKind::LineBreak);
        while !tokens.eof() {
            let _tokens = &mut tokens;
            let node = self.parse_object(_tokens);
            root.children.push(node);
            tokens.consume(TokenKind::LineBreak);
        }
        root
    }

    fn parse_object(&self, tokens: &mut TokenStream) -> SyntaxNode {
        let token = tokens.peek().unwrap().clone();
        let token_kind = token.kind.clone();
        let mut name = String::new();
        if token_kind == TokenKind::Identifier {
            name = token.value.clone();
            tokens.next();
        } else if token_kind == TokenKind::LBrace {
            // do nothing
        } else {
            let expect = vec![TokenKind::Identifier, TokenKind::LBrace];
            let error = HolaSyntaxExpectError::new(expect, token.clone());
            panic!("{:?}", error);
        }

        let mut node = SyntaxNode {
            kind: NodeKind::Object,
            start_pos: token.start_pos.clone(),
            end_pos: CharPosition {
                index: -1,
                line: -1,
                column: -1,
            },
            value: name,
            properties: HashMap::new(),
            children: Vec::new(),
        };
        tokens.expect(TokenKind::LBrace);
        tokens.consume_any(&vec![TokenKind::Comma, TokenKind::LineBreak]);
        while !tokens.eof() {
            let token = tokens.peek().unwrap();
            let token_kind = token.kind.clone();
            if token_kind == TokenKind::RBrace {
                break;
            }
            if token_kind == TokenKind::PropertyName || token_kind == TokenKind::StringLiteral {
                let (name, value) = self.parse_property(tokens);
                node.properties.insert(name, value);
            } else if token_kind == TokenKind::Identifier || token_kind == TokenKind::LBrace {
                let sub_node = self.parse_object(tokens);
                node.children.push(sub_node);
            } else {
                let expect = vec![
                    TokenKind::StringLiteral,
                    TokenKind::PropertyName,
                    TokenKind::Identifier,
                ];
                let error = HolaSyntaxExpectError::new(expect, token.clone());
                panic!("{:?}", error);
            }
            let next_token = tokens.peek().unwrap();
            let next_token_kind = next_token.kind.clone();
            if next_token_kind == TokenKind::Comma || next_token_kind == TokenKind::LineBreak {
                tokens.next();
                tokens.consume(TokenKind::LineBreak);
                continue;
            };
        }
        let last_token = tokens.peek().unwrap();
        node.end_pos = last_token.end_pos.clone();
        tokens.expect(TokenKind::RBrace);
        node
    }

    fn parse_property(&self, tokens: &mut TokenStream) -> (String, SyntaxNode) {
        let token = tokens.peek().unwrap();
        let name = token.value.clone();
        tokens.next();
        tokens.expect(TokenKind::Colon);
        let value = self.parse_value(tokens);
        (name, value)
    }

    fn parse_value(&self, tokens: &mut TokenStream) -> SyntaxNode {
        let token = tokens.peek().unwrap().clone();
        if token.kind == TokenKind::Null {
            tokens.next();
            SyntaxNode {
                kind: NodeKind::Null,
                value: "".to_string(),
                start_pos: token.start_pos.clone(),
                end_pos: token.end_pos.clone(),
                properties: HashMap::new(),
                children: Vec::new()
            }
        } else if token.kind == TokenKind::BoolLiteral {
            tokens.next();
            SyntaxNode {
                kind: NodeKind::Bool,
                value: if token.value == "true" { true.to_string() } else { false.to_string() },
                start_pos: token.start_pos.clone(),
                end_pos: token.end_pos.clone(),
                properties: HashMap::new(),
                children: Vec::new()
            }
        } else if token.kind == TokenKind::StringLiteral {
            tokens.next();
            SyntaxNode {
                kind: NodeKind::String,
                value: token.value.clone(),
                start_pos: token.start_pos.clone(),
                end_pos: token.end_pos.clone(),
                properties: HashMap::new(),
                children: Vec::new()
            }
        } else if token.kind == TokenKind::NumberLiteral {
            tokens.next();
            SyntaxNode {
                kind: NodeKind::Number,
                value: token.value.clone(),
                start_pos: token.start_pos.clone(),
                end_pos: token.end_pos.clone(),
                properties: HashMap::new(),
                children: Vec::new()
            }
        } else if token.kind == TokenKind::LBracket {
            self.parse_list(tokens)
        } else if token.kind == TokenKind::Identifier || token.kind == TokenKind::LBrace {
            self.parse_object(tokens)
        } else {
            let message = format!(
                "Unknown To Handle Token Kind {} and {}",
                token.kind, token.value
            );
            let error = HolaSyntaxError::new(message, token.start_pos.clone());
            panic!("{:?}", error);
        }
    }

    fn parse_list(&self, tokens: &mut TokenStream) -> SyntaxNode {
        let token = tokens.peek().unwrap().clone();
        let mut node = SyntaxNode {
            kind: NodeKind::List,
            start_pos: token.start_pos.clone(),
            end_pos: CharPosition {
                index: -1,
                line: -1,
                column: -1,
            },
            value: "".to_string(),
            properties: HashMap::new(),
            children: Vec::new(),
        };
        tokens.expect(TokenKind::LBracket);
        tokens.consume(TokenKind::LineBreak);
        while !tokens.eof() {
            let token = tokens.peek().unwrap();
            if token.kind == TokenKind::RBracket {
                break;
            } else if token.kind == TokenKind::Comma {
                node.children.push(SyntaxNode {
                    kind: NodeKind::Null,
                    start_pos: token.start_pos.clone(),
                    end_pos: token.start_pos.clone(),
                    value: "".to_string(),
                    properties: HashMap::new(),
                    children: Vec::new(),
                });
                tokens.consume(TokenKind::LineBreak);
                continue;
            } else {
                let sub_node = self.parse_value(tokens);
                node.children.push(sub_node);
                let next_token = tokens.peek().unwrap();
                if next_token.kind == TokenKind::Comma || next_token.kind == TokenKind::LineBreak {
                    tokens.next();
                    tokens.consume(TokenKind::LineBreak);
                    continue;
                }
            }
        }
        let token = tokens.peek().unwrap();
        node.end_pos = token.end_pos.clone();
        tokens.expect(TokenKind::RBracket);
        node
    }
}

lazy_static! {
static ref OBJECT_CATEGORY_MAP: HashMap<&'static str, &'static str> = [
    ("page", "interfaces"),
    ("modal", "interfaces"),
    ("component", "interfaces"),
    ("action", "actions"),
    ("task", "actions"),
    ("currency", "objects"),
    ("variable", "objects"),
    ("item", "objects"),
    ("object-meta", "objects"),
    ("attribute", "objects"),
]
.iter()
.cloned()
.collect();
}



#[derive(Debug)]
struct ObjectTreeCodeGenerator {}

impl ObjectTreeCodeGenerator {
    fn new() -> Self {
        ObjectTreeCodeGenerator {}
    }

    fn gen(&self, node: &SyntaxNode) -> Value {
        let mut raw_obj_list = Vec::new();
        for sub_node in &node.children {
            assert_eq!(sub_node.kind, NodeKind::Object);
            let obj = self.gen_object(sub_node);
            raw_obj_list.push(obj);
        }
        let mut json_obj_root = Map::new();
        for obj in raw_obj_list {
            let obj_type: &str = obj.get("type").unwrap().as_str().unwrap().clone();
            let category: &str = OBJECT_CATEGORY_MAP.get(obj_type).unwrap_or(&"objects");
            if !json_obj_root.contains_key(category) {
                json_obj_root.insert(category.to_string(),  Value::Array(Vec::new()));
            };
            let category_objects: &mut Vec<Value> = json_obj_root.get_mut(category).unwrap().as_array_mut().unwrap();
            category_objects.push(obj);
        }
        Value::Object(json_obj_root)
    }

    fn transform_obj_name(&self, name: &str) -> String {
        if name.is_empty() {
            return name.to_string();
        }
        let mut chars = Vec::new();
        chars.push(name.chars().next().unwrap().to_ascii_lowercase());
        for char in name.chars().skip(1) {
            if char.is_ascii_uppercase() {
                chars.push('-');
                chars.push(char.to_ascii_lowercase());
            } else {
                chars.push(char);
            }
        }
        chars.into_iter().collect()
    }

    fn gen_object(&self, node: &SyntaxNode) -> Value {
        let mut obj = Map::new();
        if node.value.to_lowercase() != "object" {
            if !node.value.is_empty() {
                obj.insert("type".to_string(), Value::String(self.transform_obj_name(&node.value)));
            }
        }
        for (k, v) in &node.properties {
            if k.to_lowercase() == "type" {
                continue;
            }
            obj.insert(k.clone(), self.gen_value(v));
        }
        if !node.children.is_empty() {
            let child_key_name = "elements".to_string();
            obj.insert(
                child_key_name.clone(),
                node.children.iter().map(|child| self.gen_object(child)).collect(),
            );
        }
        Value::Object(obj)
    }

    fn gen_list(&self, node: &SyntaxNode) -> Value {
        node.children.iter().map(|sub_node| self.gen_value(sub_node)).collect()
    }

    fn gen_value(&self, node: &SyntaxNode) -> Value {
        match node.kind {
            NodeKind::Null => Value::Null.into(),
            NodeKind::Bool => node.value.clone().parse().unwrap_or(false).into(),
            NodeKind::Number => Number::from_str(node.value.as_str()).unwrap().into(),
            NodeKind::String => node.value.clone().into(),
            NodeKind::List => self.gen_list(node),
            NodeKind::Object => self.gen_object(node),
            NodeKind::Root => self.gen_object(node)
        }
    }
}

#[derive(Debug)]
struct Compiler {}

impl Compiler {
    fn new() -> Self {
        Compiler {}
    }

    fn compile(&self, code: &str, target: &str) -> Value {
        let parser = Parser::new();
        let node = parser.parse(code);
        if target == "object_tree" {
            let generator = ObjectTreeCodeGenerator::new();
            generator.gen(&node)
        } else {
            panic!("Only target with object_tree supported.");
        }
    }
}


#[cfg(test)]
mod tests {
    use crate::base::compiler::NodeKind;
    use crate::base::compiler::TokenKind;
    use crate::base::compiler::HashMap;
    use crate::base::compiler::Tokenizer;
    use crate::base::compiler::Parser;
    use crate::base::compiler::Compiler;
    use crate::base::compiler::SyntaxNode;
    use serde_json::{Value, json};

    #[derive(Debug, PartialEq, Eq)]
    struct ObjectNode {
        kind: NodeKind,
        value: String,
        properties: HashMap<String, ObjectNode>,
        children: Vec<ObjectNode>
    }

    fn compare_tokens(code: &str, desire_tokens: &[(TokenKind, &str)]) {
        let raw_tokens = Tokenizer::new().tokenize(code);
        let tokens: Vec<(TokenKind, &str)> = raw_tokens.iter().map(|x| (x.kind.clone(), x.value.as_str())).collect();
        assert_eq!(tokens, desire_tokens);
    }

    fn compare_nodes(code: &str, desire_nodes: &[ObjectNode]) {
        fn transform_list_node(list_node: &[SyntaxNode]) -> Vec<ObjectNode> {
            list_node.iter().map(|x| transform_object_node(x)).collect()
        }

        fn transform_properties(properties: &HashMap<String, SyntaxNode>) -> HashMap<String, ObjectNode> {
            let mut p = HashMap::new();
            for (k, v) in properties.iter() {
                p.insert(k.clone(), transform_object_node(v));
            }
            p
        }

        fn transform_object_node(obj_node: &SyntaxNode) -> ObjectNode {
            let r = ObjectNode {
                kind: obj_node.kind,
                value: obj_node.value.clone(),
                properties: transform_properties(&obj_node.properties),
                children: transform_list_node(&obj_node.children),
            };
            r
        }

        let root_node = Parser::new().parse(code);
        let nodes: Vec<ObjectNode> = root_node.children.iter().map(|x| transform_object_node(x)).collect();

        assert_eq!(nodes, desire_nodes);
    }

    fn compare_object(code: &str, desire_object: &Value) {
        let root_object = Compiler::new().compile(code, "object_tree");
        assert_eq!(&root_object, desire_object);
    }

    #[test]
    fn test_tokenizer_simple_1() {
        compare_tokens(
            "",
            &[]
        );
    }

    #[test]
    fn test_tokenizer_simple_2() {
        compare_tokens(
            "Page {}",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::RBrace, "}")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_3() {
        compare_tokens(
            "Page { route: \"/\" }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::StringLiteral, "/"),
                (TokenKind::RBrace, "}")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_31() {
        compare_tokens(
            "Page { route: \"/a
bb\" }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::StringLiteral, "/a\nbb"),
                (TokenKind::RBrace, "}")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_4() {
        compare_tokens(
            "Page { route: \"/\"
            size: 5
        }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::StringLiteral, "/"),
                (TokenKind::LineBreak, "\n"),
                (TokenKind::PropertyName, "size"),
                (TokenKind::Colon, ":"),
                (TokenKind::NumberLiteral, "5"),
                (TokenKind::LineBreak, "\n"),
                (TokenKind::RBrace, "}")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_5() {
        compare_tokens(
            "Page { route: /
            size: 5
        }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::Division, "/"),
                (TokenKind::LineBreak, "\n"),
                (TokenKind::PropertyName, "size"),
                (TokenKind::Colon, ":"),
                (TokenKind::NumberLiteral, "5"),
                (TokenKind::LineBreak, "\n"),
                (TokenKind::RBrace, "}")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_6() {
        compare_tokens(
            "Page { route: /\"
            size: 5
        }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::Division, "/"),
                (TokenKind::StringLiteral, "\n            size: 5\n        }")
            ]
        );
    }

    #[test]
    fn test_tokenizer_simple_7() {
        compare_tokens(
            "Page { route: /\"
            size: \"5\"
        }",
            &[
                (TokenKind::Identifier, "Page"),
                (TokenKind::LBrace, "{"),
                (TokenKind::PropertyName, "route"),
                (TokenKind::Colon, ":"),
                (TokenKind::Division, "/"),
                (TokenKind::StringLiteral, "\n            size: "),
                (TokenKind::NumberLiteral, "5"),
                (TokenKind::StringLiteral, "\n        }"),
            ]
        );
    }

    #[test]
    fn test_parser_simple_1() {
        compare_nodes(
            "Page {}",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: HashMap::new(),
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_simple_2() {
        compare_nodes(
            "Page { route: \"/abc\" }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("route".to_string(), ObjectNode {
                            kind: NodeKind::String,
                            value: "/abc".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_simple_3() {
        compare_nodes(
            "Page { popup: true, hide: false}",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("popup".to_string(), ObjectNode {
                            kind: NodeKind::Bool,
                            value: true.to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("hide".to_string(), ObjectNode {
                            kind: NodeKind::Bool,
                            value: false.to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_simple_4() {
        compare_nodes(
            "Page { text: null }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("text".to_string(), ObjectNode {
                            kind: NodeKind::Null,
                            value: "".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_simple_5() {
        compare_nodes(
            "Page { int: 1234
                float: 1223.23
            }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("int".to_string(), ObjectNode {
                            kind: NodeKind::Number,
                            value: "1234".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("float".to_string(), ObjectNode {
                            kind: NodeKind::Number,
                            value: "1223.23".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_complex_1() {
        compare_nodes(
            "Page { route: \"/abc\", valid: [\"111\", \"222\"] }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("route".to_string(), ObjectNode {
                            kind: NodeKind::String,
                            value: "/abc".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("valid".to_string(), ObjectNode {
                            kind: NodeKind::List,
                            value: "".to_string(),
                            properties: HashMap::new(),
                            children: vec![
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "111".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                },
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "222".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                }
                            ],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_complex_2() {
        compare_nodes(
            "Page {
                route: \"/abc\", valid: [\"111\", \"222\"]
                Hero {
                    \"text\": \"Welcome\"
                }

            }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("route".to_string(), ObjectNode {
                            kind: NodeKind::String,
                            value: "/abc".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("valid".to_string(), ObjectNode {
                            kind: NodeKind::List,
                            value: "".to_string(),
                            properties: HashMap::new(),
                            children: vec![
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "111".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                },
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "222".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                }
                            ],
                        });
                        p
                    },
                    children: vec![
                        ObjectNode {
                            kind: NodeKind::Object,
                            value: "Hero".to_string(),
                            properties: {
                                let mut p = HashMap::new();
                                p.insert("text".to_string(), ObjectNode {
                                    kind: NodeKind::String,
                                    value: "Welcome".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                });
                                p
                            },
                            children: vec![],
                        }
                    ],
                }
            ]
        );
    }

    #[test]
    fn test_parser_complex_3() {
        compare_nodes(
            "Page {
                route: \"/abc\", valid: [\"111\", Hero {
                    \"text\": \"Welcome\"
                }]
            }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("route".to_string(), ObjectNode {
                            kind: NodeKind::String,
                            value: "/abc".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("valid".to_string(), ObjectNode {
                            kind: NodeKind::List,
                            value: "".to_string(),
                            properties: HashMap::new(),
                            children: vec![
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "111".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                },
                                ObjectNode {
                                    kind: NodeKind::Object,
                                    value: "Hero".to_string(),
                                    properties: {
                                        let mut p = HashMap::new();
                                        p.insert("text".to_string(), ObjectNode {
                                            kind: NodeKind::String,
                                            value: "Welcome".to_string(),
                                            properties: HashMap::new(),
                                            children: vec![],
                                        });
                                        p
                                    },
                                    children: vec![],
                                }
                            ],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_parser_complex_4() {
        compare_nodes(
            "Page {
                route: \"/abc\", valid: [\"111\", {
                    \"text\": \"Welcome\"
                }]
            }",
            &[
                ObjectNode {
                    kind: NodeKind::Object,
                    value: "Page".to_string(),
                    properties: {
                        let mut p = HashMap::new();
                        p.insert("route".to_string(), ObjectNode {
                            kind: NodeKind::String,
                            value: "/abc".to_string(),
                            properties: HashMap::new(),
                            children: vec![],
                        });
                        p.insert("valid".to_string(), ObjectNode {
                            kind: NodeKind::List,
                            value: "".to_string(),
                            properties: HashMap::new(),
                            children: vec![
                                ObjectNode {
                                    kind: NodeKind::String,
                                    value: "111".to_string(),
                                    properties: HashMap::new(),
                                    children: vec![],
                                },
                                ObjectNode {
                                    kind: NodeKind::Object,
                                    value: "".to_string(),
                                    properties: {
                                        let mut p = HashMap::new();
                                        p.insert("text".to_string(), ObjectNode {
                                            kind: NodeKind::String,
                                            value: "Welcome".to_string(),
                                            properties: HashMap::new(),
                                            children: vec![],
                                        });
                                        p
                                    },
                                    children: vec![],
                                }
                            ],
                        });
                        p
                    },
                    children: vec![],
                }
            ]
        );
    }

    #[test]
    fn test_compiler_simple_1() {
        compare_object(
            "Page {}",
            &json!({
                "interfaces": [
                    {
                        "type": "page".to_string(),
                    }
                ],
            })
        );
    }

    #[test]
    fn test_compiler_simple_2() {
        compare_object(
            "Page { route: \"/home\" }",
            &json! ({
                "interfaces": [
                    {
                        "type": "page".to_string(),
                        "route": Some("/home".to_string()),
                    }
                ],
            })
        );
    }

    #[test]
    fn test_compiler_simple_3() {
        compare_object(
            "Page { route: \"/home\"
            name: \"home\" }",
            &json!({
                "interfaces": [
                    {
                        "type": "page".to_string(),
                        "route": Some("/home".to_string()),
                        "name": Some("home".to_string()),
                    }
                ],
            })
        );
    }

}







