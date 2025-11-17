use crate::ast::{Expr, LiteralKind, BinaryOperator, UnaryOperator, LogicalOperator};
use crate::tokenizer::{Token, TokenKind};

// Pratt parser implementation for expressions.

// Precedence levels for operators
#[derive(PartialEq, PartialOrd)]
enum Precedence {
    None,
    Assignment, // =
    Or,         // or
    And,        // and
    Equality,   // == !=
    Comparison, // < > <= >=
    Term,       // + -
    Factor,     // * /
    Unary,      // ! -
    Call,       // . ()
    Index,      // []
    Primary,
}

// The main function to parse an expression.
pub fn parse_expression(tokens: &[Token]) -> Result<Expr, String> {
    let mut parser = ExpressionParser::new(tokens);
    parser.parse_precedence(Precedence::Assignment)
}

struct ExpressionParser<'a> {
    tokens: &'a [Token],
    cursor: usize,
}

impl<'a> ExpressionParser<'a> {
    fn new(tokens: &'a [Token]) -> Self {
        Self { tokens, cursor: 0 }
    }

    fn parse_precedence(&mut self, precedence: Precedence) -> Result<Expr, String> {
        let mut expr = self.parse_prefix()?;

        while self.cursor < self.tokens.len() {
            let token = self.peek();
            let next_precedence = self.get_precedence(token.kind);
            if precedence >= next_precedence {
                break;
            }

            match token.kind {
                TokenKind::Dot => {
                    expr = self.parse_get_expression(expr)?;
                }
                TokenKind::LParen => {
                    expr = self.parse_call_expression(expr)?;
                }
                TokenKind::LBracket => {
                    expr = self.parse_list_get(expr)?;
                }
                _ => {
                    expr = self.parse_infix(expr)?;
                }
            }
        }

        Ok(expr)
    }

    fn parse_prefix(&mut self) -> Result<Expr, String> {
        let token = self.advance();
        match token.kind {
            TokenKind::NumberLiteral => {
                let num = if token.value.contains('.') {
                    LiteralKind::Number(crate::ast::NumberValue::Float(token.value.parse().unwrap()))
                } else {
                    match token.value.parse::<i64>() {
                        Ok(iv) => LiteralKind::Number(crate::ast::NumberValue::Int(iv)),
                        Err(_) => LiteralKind::Number(crate::ast::NumberValue::Float(token.value.parse().unwrap())),
                    }
                };
                Ok(Expr::Literal(num))
            }
            TokenKind::StringLiteral => Ok(Expr::Literal(LiteralKind::String(token.value.clone()))),
            TokenKind::BoolLiteral => Ok(Expr::Literal(LiteralKind::Bool(token.value.parse().unwrap()))),
            TokenKind::NullLiteral => Ok(Expr::Literal(LiteralKind::Null)),
            TokenKind::Identifier => Ok(Expr::Variable(token.value.clone())),
            TokenKind::Minus | TokenKind::Bang => {
                let op = if token.kind == TokenKind::Minus { UnaryOperator::Negate } else { UnaryOperator::Not };
                let right = self.parse_precedence(Precedence::Unary)?;
                Ok(Expr::Unary(op, Box::new(right)))
            }
            TokenKind::LParen => {
                let expr = self.parse_precedence(Precedence::Assignment)?;
                self.consume(TokenKind::RParen, "Expect ')' after expression.")?;
                Ok(Expr::Grouping(Box::new(expr)))
            }
            TokenKind::LBracket => {
                self.cursor -= 1; // Step back to re-process the bracket
                self.parse_list()
            }
            _ => Err(format!("Unexpected token for prefix expression: {:?}", token.kind)),
        }
    }

    fn parse_infix(&mut self, left: Expr) -> Result<Expr, String> {
        let token = self.peek();
        let precedence = self.get_precedence(token.kind);

        self.advance(); // Consume operator

        let right = self.parse_precedence(precedence)?;

        // Check if this is a logical operator
        match token.kind {
            TokenKind::AndAnd => {
                Ok(Expr::Logical(Box::new(left), LogicalOperator::And, Box::new(right)))
            }
            TokenKind::OrOr => {
                Ok(Expr::Logical(Box::new(left), LogicalOperator::Or, Box::new(right)))
            }
            _ => {
                let operator = self.get_binary_operator(token.kind)?;
                Ok(Expr::Binary(Box::new(left), operator, Box::new(right)))
            }
        }
    }

    fn get_precedence(&self, kind: TokenKind) -> Precedence {
        match kind {
            TokenKind::Plus | TokenKind::Minus => Precedence::Term,
            TokenKind::Star | TokenKind::Slash => Precedence::Factor,
            TokenKind::EqualEqual | TokenKind::BangEqual => Precedence::Equality,
            TokenKind::Less | TokenKind::LessEqual | TokenKind::Greater | TokenKind::GreaterEqual => Precedence::Comparison,
            TokenKind::AndAnd => Precedence::And,
            TokenKind::OrOr => Precedence::Or,
            TokenKind::Dot | TokenKind::LParen => Precedence::Call,
            TokenKind::LBracket => Precedence::Index,
            _ => Precedence::None,
        }
    }

    fn get_binary_operator(&self, kind: TokenKind) -> Result<BinaryOperator, String> {
        match kind {
            TokenKind::Plus => Ok(BinaryOperator::Add),
            TokenKind::Minus => Ok(BinaryOperator::Subtract),
            TokenKind::Star => Ok(BinaryOperator::Multiply),
            TokenKind::Slash => Ok(BinaryOperator::Divide),
            TokenKind::EqualEqual => Ok(BinaryOperator::Equal),
            TokenKind::BangEqual => Ok(BinaryOperator::NotEqual),
            TokenKind::Less => Ok(BinaryOperator::Less),
            TokenKind::LessEqual => Ok(BinaryOperator::LessEqual),
            TokenKind::Greater => Ok(BinaryOperator::Greater),
            TokenKind::GreaterEqual => Ok(BinaryOperator::GreaterEqual),
            _ => Err(format!("Not a binary operator: {:?}", kind)),
        }
    }

    fn advance(&mut self) -> &'a Token {
        let token = &self.tokens[self.cursor];
        self.cursor += 1;
        token
    }

    fn peek(&self) -> &'a Token {
        &self.tokens[self.cursor]
    }

    fn consume(&mut self, kind: TokenKind, message: &str) -> Result<(), String> {
        if self.peek().kind == kind {
            self.advance();
            Ok(())
        } else {
            Err(message.to_string())
        }
    }

    fn parse_get_expression(&mut self, left: Expr) -> Result<Expr, String> {
        self.advance(); // Consume dot
        let token = self.advance();
        if token.kind == TokenKind::Identifier {
            Ok(Expr::Get(Box::new(left), token.value.clone()))
        } else {
            Err("Expect property name after '.'.".to_string())
        }
    }

    fn parse_call_expression(&mut self, callee: Expr) -> Result<Expr, String> {
        // current token is '('
        self.advance();
        let mut args: Vec<Expr> = Vec::new();
        // handle empty argument list
        if self.cursor < self.tokens.len() && self.peek().kind == TokenKind::RParen {
            self.advance();
            return Ok(Expr::Call(Box::new(callee), args));
        }
        loop {
            let arg = self.parse_precedence(Precedence::Assignment)?;
            args.push(arg);
            if self.cursor >= self.tokens.len() {
                return Err("Unterminated call, missing ')'".to_string());
            }
            match self.peek().kind {
                TokenKind::Comma => { self.advance(); }
                TokenKind::RParen => { self.advance(); break; }
                _ => return Err("Expected ',' or ')' in argument list".to_string()),
            }
        }
        Ok(Expr::Call(Box::new(callee), args))
    }

    fn parse_list(&mut self) -> Result<Expr, String> {
        self.advance(); // consume '['
        let mut items: Vec<Expr> = Vec::new();
        
        // Handle empty list
        if self.peek().kind == TokenKind::RBracket {
            self.advance(); // consume ']'
            return Ok(Expr::List(items));
        }
        
        // Parse list items
        loop {
            let item = self.parse_precedence(Precedence::Assignment)?;
            items.push(item);
            
            if self.cursor >= self.tokens.len() {
                return Err("Unterminated list, missing ']".to_string());
            }
            
            match self.peek().kind {
                TokenKind::Comma => { 
                    self.advance(); 
                    // Allow trailing comma
                    if self.peek().kind == TokenKind::RBracket {
                        self.advance(); // consume ']'
                        return Ok(Expr::List(items));
                    }
                }
                TokenKind::RBracket => { 
                    self.advance(); // consume ']'
                    break; 
                }
                _ => return Err("Expected ',' or ']' in list".to_string()),
            }
        }
        
        Ok(Expr::List(items))
    }

    fn parse_list_get(&mut self, left: Expr) -> Result<Expr, String> {
        self.advance(); // consume '['
        let index = self.parse_precedence(Precedence::Assignment)?;
        self.consume(TokenKind::RBracket, "Expect ']' after index.")?;
        Ok(Expr::ListGet(Box::new(left), Box::new(index)))
    }
}
