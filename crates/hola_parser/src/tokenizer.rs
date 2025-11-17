use std::iter::Peekable;
use std::str::Chars;

#[derive(Debug, PartialEq, Clone)]
pub struct Token {
    pub kind: TokenKind,
    pub value: String,
    // TODO: Add span for error reporting
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
    chars: Peekable<Chars<'a>>,
    state: TokenizerState,
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
            chars: source.chars().peekable(),
            state: TokenizerState::Default,
        }
    }

    fn next_default(&mut self) -> Option<Token> {
        self.skip_whitespace();
        let ch = self.chars.next()?;

        match ch {
            '{' => {
                if self.chars.peek() == Some(&'{') {
                    self.chars.next(); // consume '{'
                    self.state = TokenizerState::InExpression;
                    Some(Token { kind: TokenKind::LBraceLBrace, value: "{{".to_string() })
                } else {
                    Some(Token { kind: TokenKind::LBrace, value: "{".to_string() })
                }
            }
            '}' => Some(Token { kind: TokenKind::RBrace, value: "}".to_string() }),
            '[' => Some(Token { kind: TokenKind::LBracket, value: "[".to_string() }),
            ']' => Some(Token { kind: TokenKind::RBracket, value: "]".to_string() }),
            ':' => Some(Token { kind: TokenKind::Colon, value: ":".to_string() }),
            ',' => Some(Token { kind: TokenKind::Comma, value: ",".to_string() }),
            '\n' => Some(Token { kind: TokenKind::LineBreak, value: "\n".to_string() }),
            '/' => {
                if self.chars.peek() == Some(&'/') {
                    self.read_comment()
                } else {
                    Some(Token { kind: TokenKind::Unknown, value: "/".to_string() })
                }
            }
            '"' | '\'' => self.read_string(ch),
            c if c.is_ascii_alphabetic() || c == '_' => self.read_identifier(c),
            c if c.is_ascii_digit() => self.read_number(c),
            _ => Some(Token { kind: TokenKind::Unknown, value: ch.to_string() })
        }
    }

    fn next_expression(&mut self) -> Option<Token> {
        self.skip_whitespace();
        let ch = self.chars.next()?;

        match ch {
            '}' => {
                if self.chars.peek() == Some(&'}') {
                    self.chars.next(); // consume '}'
                    self.state = TokenizerState::Default;
                    Some(Token { kind: TokenKind::RBraceRBrace, value: "}}".to_string() })
                } else {
                    // This could be an error in a real implementation
                    Some(Token { kind: TokenKind::RBrace, value: "}".to_string() })
                }
            }
            '+' => Some(Token { kind: TokenKind::Plus, value: "+".to_string() }),
            '-' => Some(Token { kind: TokenKind::Minus, value: "-".to_string() }),
            '*' => Some(Token { kind: TokenKind::Star, value: "*".to_string() }),
            '/' => Some(Token { kind: TokenKind::Slash, value: "/".to_string() }),
            '(' => Some(Token { kind: TokenKind::LParen, value: "(".to_string() }),
            ')' => Some(Token { kind: TokenKind::RParen, value: ")".to_string() }),
            '[' => Some(Token { kind: TokenKind::LBracket, value: "[".to_string() }),
            ']' => Some(Token { kind: TokenKind::RBracket, value: "]".to_string() }),
            ',' => Some(Token { kind: TokenKind::Comma, value: ",".to_string() }),
            '.' => Some(Token { kind: TokenKind::Dot, value: ".".to_string() }),
            '=' => self.one_or_two_char('=', TokenKind::EqualEqual, TokenKind::Equal),
            '!' => self.one_or_two_char('=', TokenKind::BangEqual, TokenKind::Bang),
            '>' => self.one_or_two_char('=', TokenKind::GreaterEqual, TokenKind::Greater),
            '<' => self.one_or_two_char('=', TokenKind::LessEqual, TokenKind::Less),
            '&' => {
                if self.chars.peek() == Some(&'&') {
                    self.chars.next();
                    Some(Token { kind: TokenKind::AndAnd, value: "&&".to_string() })
                } else {
                    Some(Token { kind: TokenKind::Unknown, value: "&".to_string() })
                }
            },
            '|' => {
                if self.chars.peek() == Some(&'|') {
                    self.chars.next();
                    Some(Token { kind: TokenKind::OrOr, value: "||".to_string() })
                } else {
                    Some(Token { kind: TokenKind::Unknown, value: "|".to_string() })
                }
            },
            '"' | '\'' => self.read_string(ch),
            c if c.is_ascii_alphabetic() || c == '_' => self.read_identifier(c),
            c if c.is_ascii_digit() => self.read_number(c),
            _ => Some(Token { kind: TokenKind::Unknown, value: ch.to_string() })
        }
    }

    fn skip_whitespace(&mut self) {
        while let Some(&c) = self.chars.peek() {
            if c.is_whitespace() && c != '\n' {
                self.chars.next();
            } else {
                break;
            }
        }
    }

    fn read_string(&mut self, quote: char) -> Option<Token> {
        let mut value = String::new();
        while let Some(&c) = self.chars.peek() {
            if c == quote {
                self.chars.next();
                return Some(Token { kind: TokenKind::StringLiteral, value });
            }
            if c == '\\' {
                self.chars.next();
                if let Some(&n) = self.chars.peek() {
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
                    self.chars.next();
                    continue;
                } else {
                    break;
                }
            }
            value.push(self.chars.next().unwrap());
        }
        Some(Token { kind: TokenKind::Unknown, value })
    }

    fn read_identifier(&mut self, first: char) -> Option<Token> {
        let mut value = String::new();
        value.push(first);
        while let Some(&c) = self.chars.peek() {
            if c.is_ascii_alphanumeric() || c == '_' {
                value.push(self.chars.next().unwrap());
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
        Some(Token { kind, value })
    }

    fn read_number(&mut self, first: char) -> Option<Token> {
        let mut value = String::new();
        value.push(first);
        while let Some(&c) = self.chars.peek() {
            if c.is_ascii_digit() || c == '.' || c == '_' {
                if c != '_' {
                    value.push(self.chars.next().unwrap());
                }
                 else {
                    self.chars.next(); // consume '_'
                }
            } else {
                break;
            }
        }
        Some(Token { kind: TokenKind::NumberLiteral, value })
    }
    
    fn read_comment(&mut self) -> Option<Token> {
        let mut value = String::new();
        self.chars.next(); // consume second '/'
        while let Some(&c) = self.chars.peek() {
            if c == '\n' {
                break;
            }
            value.push(self.chars.next().unwrap());
        }
        Some(Token { kind: TokenKind::Comment, value })
    }

    fn one_or_two_char(&mut self, next_char: char, two_kind: TokenKind, one_kind: TokenKind) -> Option<Token> {
        if self.chars.peek() == Some(&next_char) {
            self.chars.next();
            Some(Token { kind: two_kind, value: format!("{}{}", next_char, next_char) })
        } else {
            Some(Token { kind: one_kind, value: next_char.to_string() })
        }
    }
}
