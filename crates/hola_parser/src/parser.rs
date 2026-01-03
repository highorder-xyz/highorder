use std::iter::Peekable;
use crate::ast::{AstRoot, ObjectNode, PropertyValue, LiteralKind};
use crate::tokenizer::{Token, Tokenizer, TokenKind};
use crate::expression_parser;
use std::collections::HashMap;

pub struct Parser<'a> {
    tokens: Peekable<Tokenizer<'a>>,
}

impl<'a> Parser<'a> {
    pub fn new(source: &'a str) -> Self {
        Parser {
            tokens: Tokenizer::new(source).peekable(),
        }
    }

    pub fn parse(&mut self) -> Result<AstRoot, String> {
        let mut objects = Vec::new();
        while self.tokens.peek().is_some() {
            self.consume_breaks();
            if self.tokens.peek().is_none() { break; }
            
            let object = self.parse_object()?;
            objects.push(object);
            self.consume_breaks();
        }
        Ok(AstRoot { objects })
    }

    fn parse_object(&mut self) -> Result<ObjectNode, String> {
        let name = if let Some(token) = self.peek_if(TokenKind::Identifier) {
            self.tokens.next(); // consume first identifier
            let mut name = token.value;
            while let Some(token) = self.tokens.peek() {
                if token.kind != TokenKind::Dot {
                    break;
                }
                self.tokens.next(); // consume '.'
                let next = self.tokens.peek().ok_or("Expect identifier after '.' in type name.")?;
                if next.kind != TokenKind::Identifier {
                    return Err(format!("Expect identifier after '.' in type name, found {:?}", next.kind));
                }
                let next = self.tokens.next().unwrap();
                name.push('.');
                name.push_str(&next.value);
            }
            name
        } else {
            String::new() // Anonymous object
        };

        self.expect(TokenKind::LBrace, "Expect '{' to start an object block.")?;
        self.consume_breaks();

        let mut properties = HashMap::new();
        let mut children = Vec::new();

        while let Some(token) = self.tokens.peek() {
            if token.kind == TokenKind::RBrace {
                break;
            }

            match token.kind {
                TokenKind::PropertyName | TokenKind::StringLiteral => {
                    let (key, value) = self.parse_property()?;
                    properties.insert(key, value);
                }
                TokenKind::Identifier | TokenKind::LBrace => {
                    let child = self.parse_object()?;
                    children.push(child);
                }
                _ => return Err(format!("Unexpected token in object: {:?}", token.kind)),
            }
            self.consume_separators();
        }

        self.expect(TokenKind::RBrace, "Expect '}' to close an object block.")?;

        Ok(ObjectNode { name, properties, children })
    }

    fn parse_property(&mut self) -> Result<(String, PropertyValue), String> {
        // property key can be a bare property name or a quoted string
        let key_token = match self.tokens.peek() {
            Some(t) if t.kind == TokenKind::PropertyName || t.kind == TokenKind::StringLiteral => self.tokens.next().unwrap(),
            Some(t) => return Err(format!("Expect property name, found {:?}", t.kind)),
            None => return Err("Unexpected EOF when expecting property name".to_string()),
        };
        self.expect(TokenKind::Colon, "Expect ':' after property name.")?;
        let value = self.parse_value()?;
        Ok((key_token.value, value))
    }

    fn parse_value(&mut self) -> Result<PropertyValue, String> {
        let token = self.tokens.peek().ok_or("Unexpected end of input, expected a value.")?;
        match token.kind {
            TokenKind::StringLiteral => {
                let token = self.tokens.next().unwrap();
                Ok(PropertyValue::Literal(LiteralKind::String(token.value)))
            }
            TokenKind::NumberLiteral => {
                let token = self.tokens.next().unwrap();
                let num = if token.value.contains('.') {
                    LiteralKind::Number(crate::ast::NumberValue::Float(token.value.parse().map_err(|e| format!("Invalid float: {}", e))?))
                } else {
                    // try parse int
                    match token.value.parse::<i64>() {
                        Ok(iv) => LiteralKind::Number(crate::ast::NumberValue::Int(iv)),
                        Err(_) => LiteralKind::Number(crate::ast::NumberValue::Float(token.value.parse().map_err(|e| format!("Invalid number: {}", e))?)),
                    }
                };
                Ok(PropertyValue::Literal(num))
            }
            TokenKind::ColorLiteral => {
                let token = self.tokens.next().unwrap();
                Ok(PropertyValue::Literal(LiteralKind::Color(token.value)))
            }
            TokenKind::BoolLiteral => {
                let token = self.tokens.next().unwrap();
                Ok(PropertyValue::Literal(LiteralKind::Bool(token.value.parse().unwrap())))
            }
            TokenKind::NullLiteral => {
                self.tokens.next();
                Ok(PropertyValue::Literal(LiteralKind::Null))
            }
            TokenKind::LBracket => self.parse_list(),
            TokenKind::LBrace | TokenKind::Identifier => Ok(PropertyValue::Object(self.parse_object()?)),
            TokenKind::LBraceLBrace => self.parse_expression_block(),
            _ => Err(format!("Unexpected token for a value: {:?}", token.kind)),
        }
    }

    fn parse_list(&mut self) -> Result<PropertyValue, String> {
        self.expect(TokenKind::LBracket, "Expect '[' to start a list.")?;
        let mut items = Vec::new();
        let mut last_was_sep = true; // at start, a comma means leading null

        loop {
            // skip line breaks between tokens and mark as separator if any
            let mut had_break = false;
            while let Some(t) = self.tokens.peek() {
                if t.kind == TokenKind::LineBreak {
                    self.tokens.next();
                    had_break = true;
                } else {
                    break;
                }
            }
            if had_break { last_was_sep = true; }

            // end of list
            if self.peek_if(TokenKind::RBracket).is_some() {
                break;
            }

            // separator: comma
            if let Some(t) = self.tokens.peek() {
                if t.kind == TokenKind::Comma {
                    self.tokens.next();
                    if last_was_sep {
                        // leading or consecutive comma => empty slot
                        items.push(PropertyValue::Literal(LiteralKind::Null));
                    }
                    last_was_sep = true;
                    continue;
                }
            }

            // normal element
            let v = self.parse_value()?;
            items.push(v);
            last_was_sep = false;
        }

        self.expect(TokenKind::RBracket, "Expect ']' to close a list.")?;
        Ok(PropertyValue::List(items))
    }

    fn parse_expression_block(&mut self) -> Result<PropertyValue, String> {
        self.expect(TokenKind::LBraceLBrace, "Expect '{{' to start an expression.")?;
        
        let mut expr_tokens = Vec::new();
        while let Some(token) = self.tokens.peek() {
            if token.kind == TokenKind::RBraceRBrace {
                break;
            }
            expr_tokens.push(self.tokens.next().unwrap());
        }

        self.expect(TokenKind::RBraceRBrace, "Expect '}}' to close an expression.")?;

        let expr = expression_parser::parse_expression(&expr_tokens)?;
        Ok(PropertyValue::Expression(expr))
    }

    // --- Utility Functions ---

    fn expect(&mut self, kind: TokenKind, msg: &str) -> Result<Token, String> {
        match self.tokens.next() {
            Some(token) if token.kind == kind => Ok(token),
            Some(token) => Err(format!("{} Found {:?} instead.", msg, token.kind)),
            None => Err(msg.to_string()),
        }
    }

    fn peek_if(&mut self, kind: TokenKind) -> Option<Token> {
        self.tokens.peek().filter(|t| t.kind == kind).cloned()
    }

    fn consume_breaks(&mut self) {
        while let Some(token) = self.tokens.peek() {
            if token.kind == TokenKind::LineBreak || token.kind == TokenKind::Comment {
                self.tokens.next();
            } else {
                break;
            }
        }
    }

    fn consume_linebreaks(&mut self) {
        while let Some(token) = self.tokens.peek() {
            if token.kind == TokenKind::LineBreak {
                self.tokens.next();
            } else {
                break;
            }
        }
    }
    
    fn consume_separators(&mut self) {
        while let Some(token) = self.tokens.peek() {
            if token.kind == TokenKind::LineBreak || token.kind == TokenKind::Comma || token.kind == TokenKind::Comment {
                self.tokens.next();
            } else {
                break;
            }
        }
    }
}
