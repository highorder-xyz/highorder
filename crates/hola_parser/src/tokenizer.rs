use std::iter::Peekable;
use std::str::Chars;
use crate::position::{BytePos, Span};

#[derive(Debug, PartialEq, Clone)]
pub struct Token {
    pub kind: TokenKind,
    pub value: String,
    pub span: Span,
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
pub enum TokenKind {
    // Hola structure tokens
    Identifier,     // Page
    PropertyName,   // name
    StringLiteral,  // "hello"
    NumberLiteral,  // 123
    BoolLiteral,    // true, false
    NullLiteral,    // null
    LBrace,         // {
    RBrace,         // }
    LBracket,       // [
    RBracket,       // ]
    Colon,          // :
    Comma,          // ,
    LineBreak,      // \n
    Comment,        // // ...

    // Expression-specific tokens
    Plus,           // +
    Minus,          // -
    Star,           // *
    Slash,          // /
    Bang,           // !
    Equal,          // =
    LParen,         // (
    RParen,         // )
    Dot,            // .

    // Two-character tokens
    BangEqual,      // !=
    EqualEqual,     // ==
    Greater,        // >
    GreaterEqual,   // >=
    Less,           // <
    LessEqual,      // <=
    AndAnd,         // &&
    OrOr,           // ||

    // State-switching tokens
    LBraceLBrace,   // {{
    RBraceRBrace,   // }}

    // Meta tokens
    Eof,
    Unknown,
}

#[derive(Debug, PartialEq, Eq, Clone, Copy)]
enum TokenizerState {
    Default,
    InExpression,
}

pub struct Tokenizer<'a> {
    source: &'a str,
    chars: Peekable<Chars<'a>>,
    state: TokenizerState,
    current_pos: BytePos,
}

impl<'a> Iterator for Tokenizer<'a> {
    type Item = Token;

    fn next(&mut self) -> Option<Self::Item> {
        match self.state {
            TokenizerState::Default => self.next_default(),
            TokenizerState::InExpression => self.next_expression(),
        }
    }
}

impl<'a> Tokenizer<'a> {
    pub fn new(source: &'a str) -> Self {
        Tokenizer {
            source,
            chars: source.chars().peekable(),
            state: TokenizerState::Default,
            current_pos: BytePos(0),
        }
    }

    fn advance_char(&mut self) -> Option<char> {
        if let Some(ch) = self.chars.next() {
            self.current_pos = self.current_pos.shift(ch);
            Some(ch)
        } else {
            None
        }
    }

    fn peek_char(&mut self) -> Option<&char> {
        self.chars.peek()
    }

    fn make_token(&self, kind: TokenKind, value: String, start_pos: BytePos) -> Token {
        Token {
            kind,
            value,
            span: Span::new(start_pos, self.current_pos),
        }
    }

    fn next_default(&mut self) -> Option<Token> {
        self.skip_whitespace();
        let start_pos = self.current_pos;
        let ch = self.advance_char()?;

        match ch {
            '{' => {
                if self.peek_char() == Some(&'{') {
                    self.advance_char(); // consume '{'
                    self.state = TokenizerState::InExpression;
                    Some(self.make_token(TokenKind::LBraceLBrace, "{{".to_string(), start_pos))
                } else {
                    Some(self.make_token(TokenKind::LBrace, "{".to_string(), start_pos))
                }
            }
            '}' => Some(self.make_token(TokenKind::RBrace, "}".to_string(), start_pos)),
            '[' => Some(self.make_token(TokenKind::LBracket, "[".to_string(), start_pos)),
            ']' => Some(self.make_token(TokenKind::RBracket, "]".to_string(), start_pos)),
            ':' => Some(self.make_token(TokenKind::Colon, ":".to_string(), start_pos)),
            ',' => Some(self.make_token(TokenKind::Comma, ",".to_string(), start_pos)),
            '\n' => Some(self.make_token(TokenKind::LineBreak, "\n".to_string(), start_pos)),
            '/' => {
                if self.peek_char() == Some(&'/') {
                    self.read_comment(start_pos)
                } else {
                    Some(self.make_token(TokenKind::Unknown, "/".to_string(), start_pos))
                }
            }
            '"' | '\'' => self.read_string(ch, start_pos),
            c if c.is_ascii_alphabetic() || c == '_' => self.read_identifier(c, start_pos),
            c if c.is_ascii_digit() => self.read_number(c, start_pos),
            _ => Some(self.make_token(TokenKind::Unknown, ch.to_string(), start_pos))
        }
    }

    fn next_expression(&mut self) -> Option<Token> {
        self.skip_whitespace();
        let start_pos = self.current_pos;
        let ch = self.advance_char()?;

        match ch {
            '}' => {
                if self.peek_char() == Some(&'}') {
                    self.advance_char(); // consume '}'
                    self.state = TokenizerState::Default;
                    Some(self.make_token(TokenKind::RBraceRBrace, "}}".to_string(), start_pos))
                } else {
                    Some(self.make_token(TokenKind::RBrace, "}".to_string(), start_pos))
                }
            }
            '+' => Some(self.make_token(TokenKind::Plus, "+".to_string(), start_pos)),
            '-' => Some(self.make_token(TokenKind::Minus, "-".to_string(), start_pos)),
            '*' => Some(self.make_token(TokenKind::Star, "*".to_string(), start_pos)),
            '/' => Some(self.make_token(TokenKind::Slash, "/".to_string(), start_pos)),
            '(' => Some(self.make_token(TokenKind::LParen, "(".to_string(), start_pos)),
            ')' => Some(self.make_token(TokenKind::RParen, ")".to_string(), start_pos)),
            '[' => Some(self.make_token(TokenKind::LBracket, "[".to_string(), start_pos)),
            ']' => Some(self.make_token(TokenKind::RBracket, "]".to_string(), start_pos)),
            ',' => Some(self.make_token(TokenKind::Comma, ",".to_string(), start_pos)),
            '.' => Some(self.make_token(TokenKind::Dot, ".".to_string(), start_pos)),
            '=' => self.one_or_two_char('=', TokenKind::EqualEqual, TokenKind::Equal, start_pos),
            '!' => self.one_or_two_char('=', TokenKind::BangEqual, TokenKind::Bang, start_pos),
            '>' => self.one_or_two_char('=', TokenKind::GreaterEqual, TokenKind::Greater, start_pos),
            '<' => self.one_or_two_char('=', TokenKind::LessEqual, TokenKind::Less, start_pos),
            '&' => {
                if self.peek_char() == Some(&'&') {
                    self.advance_char();
                    Some(self.make_token(TokenKind::AndAnd, "&&".to_string(), start_pos))
                } else {
                    Some(self.make_token(TokenKind::Unknown, "&".to_string(), start_pos))
                }
            },
            '|' => {
                if self.peek_char() == Some(&'|') {
                    self.advance_char();
                    Some(self.make_token(TokenKind::OrOr, "||".to_string(), start_pos))
                } else {
                    Some(self.make_token(TokenKind::Unknown, "|".to_string(), start_pos))
                }
            },
            '"' | '\'' => self.read_string(ch, start_pos),
            c if c.is_ascii_alphabetic() || c == '_' => self.read_identifier(c, start_pos),
            c if c.is_ascii_digit() => self.read_number(c, start_pos),
            _ => Some(self.make_token(TokenKind::Unknown, ch.to_string(), start_pos))
        }
    }

    fn skip_whitespace(&mut self) {
        while let Some(&c) = self.peek_char() {
            if c.is_whitespace() && c != '\n' {
                self.advance_char();
            } else {
                break;
            }
        }
    }

    fn read_string(&mut self, quote: char, start_pos: BytePos) -> Option<Token> {
        let mut value = String::new();
        while let Some(&c) = self.peek_char() {
            if c == quote {
                self.advance_char();
                return Some(self.make_token(TokenKind::StringLiteral, value, start_pos));
            }
            if c == '\\' {
                self.advance_char();
                if let Some(&n) = self.peek_char() {
                    let ch = match n {
                        'n' => '\n',
                        'r' => '\r',
                        't' => '\t',
                        'v' => '\u{000B}',
                        'b' => '\u{0008}',
                        'f' => '\u{000C}',
                        'a' => '\u{0007}',
                        '\\' => '\\',
                        '"' => '"',
                        '\'' => '\'',
                        other => other,
                    };
                    value.push(ch);
                    self.advance_char();
                    continue;
                } else {
                    break;
                }
            }
            value.push(self.advance_char().unwrap());
        }
        Some(self.make_token(TokenKind::Unknown, value, start_pos))
    }

    fn read_identifier(&mut self, first: char, start_pos: BytePos) -> Option<Token> {
        let mut value = String::new();
        value.push(first);
        while let Some(&c) = self.peek_char() {
            if c.is_ascii_alphanumeric() || c == '_' {
                value.push(self.advance_char().unwrap());
            } else {
                break;
            }
        }

        let kind = match value.as_str() {
            "true" | "false" => TokenKind::BoolLiteral,
            "null" => TokenKind::NullLiteral,
            _ => {
                if self.state == TokenizerState::Default && first.is_ascii_lowercase() {
                    TokenKind::PropertyName
                } else {
                    TokenKind::Identifier
                }
            }
        };
        Some(self.make_token(kind, value, start_pos))
    }

    fn read_number(&mut self, first: char, start_pos: BytePos) -> Option<Token> {
        let mut value = String::new();
        value.push(first);
        while let Some(&c) = self.peek_char() {
            if c.is_ascii_digit() || c == '.' || c == '_' {
                if c != '_' {
                    value.push(self.advance_char().unwrap());
                } else {
                    self.advance_char(); // consume '_'
                }
            } else {
                break;
            }
        }
        Some(self.make_token(TokenKind::NumberLiteral, value, start_pos))
    }
    
    fn read_comment(&mut self, start_pos: BytePos) -> Option<Token> {
        let mut value = String::new();
        self.advance_char(); // consume second '/'
        while let Some(&c) = self.peek_char() {
            if c == '\n' {
                break;
            }
            value.push(self.advance_char().unwrap());
        }
        Some(self.make_token(TokenKind::Comment, value, start_pos))
    }

    fn one_or_two_char(&mut self, next_char: char, two_kind: TokenKind, one_kind: TokenKind, start_pos: BytePos) -> Option<Token> {
        if self.peek_char() == Some(&next_char) {
            self.advance_char();
            Some(self.make_token(two_kind, format!("{}{}", next_char, next_char), start_pos))
        } else {
            Some(self.make_token(one_kind, next_char.to_string(), start_pos))
        }
    }
}
