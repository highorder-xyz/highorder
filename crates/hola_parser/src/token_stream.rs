use crate::tokenizer::{Token, TokenKind};

/// TokenStream provides a convenient wrapper around a vector of tokens
/// with powerful navigation and consumption capabilities.
#[derive(Debug)]
pub struct TokenStream {
    tokens: Vec<Token>,
    idx: usize,
}

impl TokenStream {
    /// Create a new TokenStream from a vector of tokens
    pub fn new(tokens: Vec<Token>) -> Self {
        TokenStream { tokens, idx: 0 }
    }

    /// Peek at the current token without consuming it
    pub fn peek(&self) -> Option<&Token> {
        if self.idx >= self.tokens.len() {
            return None;
        }
        Some(&self.tokens[self.idx])
    }

    /// Peek ahead at the token at current position + num
    /// 
    /// # Examples
    /// ```
    /// // peek_next(0) is same as peek()
    /// // peek_next(1) looks at next token
    /// // peek_next(2) looks at token after next
    /// ```
    pub fn peek_next(&self, num: usize) -> Option<&Token> {
        let new_idx = self.idx + num;
        if new_idx >= self.tokens.len() {
            return None;
        }
        Some(&self.tokens[new_idx])
    }

    /// Consume consecutive tokens of the given kind
    /// Returns the number of tokens consumed
    /// 
    /// # Examples
    /// ```
    /// # use hola_parser::token_stream::TokenStream;
    /// # use hola_parser::tokenizer::TokenKind;
    /// // Consume all consecutive line breaks
    /// // stream.consume(TokenKind::LineBreak);
    /// ```
    pub fn consume(&mut self, kind: TokenKind) -> usize {
        let old_idx = self.idx;
        while self.idx < self.tokens.len() && self.tokens[self.idx].kind == kind {
            self.idx += 1;
        }
        self.idx - old_idx
    }

    /// Consume consecutive tokens that match any of the given kinds
    /// Returns the number of tokens consumed
    /// 
    /// # Examples
    /// ```
    /// # use hola_parser::token_stream::TokenStream;
    /// # use hola_parser::tokenizer::TokenKind;
    /// // Consume all line breaks and commas
    /// // stream.consume_any(&[TokenKind::LineBreak, TokenKind::Comma]);
    /// ```
    pub fn consume_any(&mut self, kinds: &[TokenKind]) -> usize {
        let old_idx = self.idx;
        while self.idx < self.tokens.len() && kinds.contains(&self.tokens[self.idx].kind) {
            self.idx += 1;
        }
        self.idx - old_idx
    }

    /// Expect a token of the given kind, consume it if found, otherwise return error
    /// 
    /// # Examples
    /// ```
    /// # use hola_parser::token_stream::TokenStream;
    /// # use hola_parser::tokenizer::TokenKind;
    /// // stream.expect(TokenKind::LBrace)?;
    /// ```
    pub fn expect(&mut self, token_kind: TokenKind) -> Result<Token, String> {
        match self.peek() {
            Some(token) if token.kind == token_kind => {
                let token = token.clone();
                self.next();
                Ok(token)
            }
            Some(token) => Err(format!(
                "Expected {:?}, but found {:?}",
                token_kind, token.kind
            )),
            None => Err(format!("Expected {:?}, but reached end of input", token_kind)),
        }
    }

    /// Advance to the next token
    pub fn next(&mut self) -> Option<Token> {
        if self.idx < self.tokens.len() {
            let token = self.tokens[self.idx].clone();
            self.idx += 1;
            Some(token)
        } else {
            None
        }
    }

    /// Move forward by a given number of steps
    pub fn move_num(&mut self, steps: usize) {
        self.idx = (self.idx + steps).min(self.tokens.len());
    }

    /// Check if we've reached the end of the token stream
    pub fn eof(&self) -> bool {
        self.idx >= self.tokens.len()
    }

    /// Get the current position in the token stream
    pub fn position(&self) -> usize {
        self.idx
    }

    /// Reset position to a saved position
    pub fn set_position(&mut self, pos: usize) {
        self.idx = pos.min(self.tokens.len());
    }

    /// Get a slice of remaining tokens
    pub fn remaining(&self) -> &[Token] {
        &self.tokens[self.idx..]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::position::{BytePos, Span};

    fn make_token(kind: TokenKind, value: &str) -> Token {
        Token {
            kind,
            value: value.to_string(),
            span: Span::new(BytePos(0), BytePos(0)),
        }
    }

    #[test]
    fn test_peek_and_next() {
        let tokens = vec![
            make_token(TokenKind::Identifier, "Page"),
            make_token(TokenKind::LBrace, "{"),
            make_token(TokenKind::RBrace, "}"),
        ];
        let mut stream = TokenStream::new(tokens);

        assert_eq!(stream.peek().unwrap().kind, TokenKind::Identifier);
        assert_eq!(stream.peek().unwrap().value, "Page");
        
        stream.next();
        assert_eq!(stream.peek().unwrap().kind, TokenKind::LBrace);
    }

    #[test]
    fn test_peek_next() {
        let tokens = vec![
            make_token(TokenKind::Identifier, "Page"),
            make_token(TokenKind::LBrace, "{"),
            make_token(TokenKind::RBrace, "}"),
        ];
        let stream = TokenStream::new(tokens);

        assert_eq!(stream.peek_next(0).unwrap().kind, TokenKind::Identifier);
        assert_eq!(stream.peek_next(1).unwrap().kind, TokenKind::LBrace);
        assert_eq!(stream.peek_next(2).unwrap().kind, TokenKind::RBrace);
        assert!(stream.peek_next(3).is_none());
    }

    #[test]
    fn test_consume() {
        let tokens = vec![
            make_token(TokenKind::LineBreak, "\n"),
            make_token(TokenKind::LineBreak, "\n"),
            make_token(TokenKind::LineBreak, "\n"),
            make_token(TokenKind::Identifier, "Page"),
        ];
        let mut stream = TokenStream::new(tokens);

        let count = stream.consume(TokenKind::LineBreak);
        assert_eq!(count, 3);
        assert_eq!(stream.peek().unwrap().kind, TokenKind::Identifier);
    }

    #[test]
    fn test_consume_any() {
        let tokens = vec![
            make_token(TokenKind::LineBreak, "\n"),
            make_token(TokenKind::Comma, ","),
            make_token(TokenKind::LineBreak, "\n"),
            make_token(TokenKind::Identifier, "Page"),
        ];
        let mut stream = TokenStream::new(tokens);

        let count = stream.consume_any(&[TokenKind::LineBreak, TokenKind::Comma]);
        assert_eq!(count, 3);
        assert_eq!(stream.peek().unwrap().kind, TokenKind::Identifier);
    }

    #[test]
    fn test_expect_success() {
        let tokens = vec![
            make_token(TokenKind::LBrace, "{"),
            make_token(TokenKind::RBrace, "}"),
        ];
        let mut stream = TokenStream::new(tokens);

        assert!(stream.expect(TokenKind::LBrace).is_ok());
        assert_eq!(stream.peek().unwrap().kind, TokenKind::RBrace);
    }

    #[test]
    fn test_expect_failure() {
        let tokens = vec![make_token(TokenKind::LBrace, "{")];
        let mut stream = TokenStream::new(tokens);

        let result = stream.expect(TokenKind::RBrace);
        assert!(result.is_err());
    }

    #[test]
    fn test_eof() {
        let tokens = vec![make_token(TokenKind::Identifier, "Page")];
        let mut stream = TokenStream::new(tokens);

        assert!(!stream.eof());
        stream.next();
        assert!(stream.eof());
    }

    #[test]
    fn test_position_and_set() {
        let tokens = vec![
            make_token(TokenKind::Identifier, "A"),
            make_token(TokenKind::Identifier, "B"),
            make_token(TokenKind::Identifier, "C"),
        ];
        let mut stream = TokenStream::new(tokens);

        assert_eq!(stream.position(), 0);
        stream.next();
        assert_eq!(stream.position(), 1);
        
        stream.set_position(0);
        assert_eq!(stream.peek().unwrap().value, "A");
    }
}
