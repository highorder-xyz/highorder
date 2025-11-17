use crate::tokenizer::{Token, TokenKind};
use crate::position::{Span, Diagnostic, DiagnosticLevel, LineOffsets};

/// Represents a syntax error where specific token kinds were expected
/// but a different token was found.
#[derive(Debug, Clone, PartialEq)]
pub struct ExpectError {
    /// List of token kinds that were expected
    pub expected: Vec<TokenKind>,
    /// The token that was actually found
    pub found: Token,
}

impl ExpectError {
    /// Create a new ExpectError
    pub fn new(expected: Vec<TokenKind>, found: Token) -> Self {
        ExpectError { expected, found }
    }

    /// Create an ExpectError for a single expected token kind
    pub fn single(expected: TokenKind, found: Token) -> Self {
        ExpectError {
            expected: vec![expected],
            found,
        }
    }

    /// Convert to a diagnostic message
    pub fn to_diagnostic(&self) -> Diagnostic {
        let message = self.format_message();
        Diagnostic {
            level: DiagnosticLevel::Error,
            span: self.found.span,
            message,
        }
    }

    /// Format the error message
    pub fn format_message(&self) -> String {
        let expected_str = if self.expected.len() == 1 {
            format!("{:?}", self.expected[0])
        } else if self.expected.len() == 2 {
            format!("{:?} or {:?}", self.expected[0], self.expected[1])
        } else {
            let parts: Vec<String> = self.expected[..self.expected.len() - 1]
                .iter()
                .map(|k| format!("{:?}", k))
                .collect();
            let last = format!("{:?}", self.expected.last().unwrap());
            format!("{}, or {}", parts.join(", "), last)
        };

        format!(
            "Expected {}, but found {:?} '{}'",
            expected_str, self.found.kind, self.found.value
        )
    }

    /// Format the error with source context
    pub fn format(&self, source: &str, line_offsets: &LineOffsets) -> String {
        self.to_diagnostic().format(source, line_offsets)
    }
}

impl std::fmt::Display for ExpectError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.format_message())
    }
}

impl std::error::Error for ExpectError {}

/// General syntax error for Hola parser
#[derive(Debug, Clone, PartialEq)]
pub struct SyntaxError {
    pub message: String,
    pub span: Span,
}

impl SyntaxError {
    pub fn new(message: String, span: Span) -> Self {
        SyntaxError { message, span }
    }

    pub fn to_diagnostic(&self) -> Diagnostic {
        Diagnostic {
            level: DiagnosticLevel::Error,
            span: self.span,
            message: self.message.clone(),
        }
    }

    pub fn format(&self, source: &str, line_offsets: &LineOffsets) -> String {
        self.to_diagnostic().format(source, line_offsets)
    }
}

impl std::fmt::Display for SyntaxError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Syntax Error: {}", self.message)
    }
}

impl std::error::Error for SyntaxError {}

/// Parse error types
#[derive(Debug, Clone, PartialEq)]
pub enum ParseError {
    Expect(ExpectError),
    Syntax(SyntaxError),
    Message(String),
}

impl ParseError {
    pub fn to_diagnostic(&self) -> Diagnostic {
        match self {
            ParseError::Expect(e) => e.to_diagnostic(),
            ParseError::Syntax(e) => e.to_diagnostic(),
            ParseError::Message(msg) => Diagnostic {
                level: DiagnosticLevel::Error,
                span: Span::empty(),
                message: msg.clone(),
            },
        }
    }

    pub fn format(&self, source: &str, line_offsets: &LineOffsets) -> String {
        self.to_diagnostic().format(source, line_offsets)
    }
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ParseError::Expect(e) => write!(f, "{}", e),
            ParseError::Syntax(e) => write!(f, "{}", e),
            ParseError::Message(msg) => write!(f, "{}", msg),
        }
    }
}

impl std::error::Error for ParseError {}

impl From<ExpectError> for ParseError {
    fn from(e: ExpectError) -> Self {
        ParseError::Expect(e)
    }
}

impl From<SyntaxError> for ParseError {
    fn from(e: SyntaxError) -> Self {
        ParseError::Syntax(e)
    }
}

impl From<String> for ParseError {
    fn from(s: String) -> Self {
        ParseError::Message(s)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::position::BytePos;

    fn make_token(kind: TokenKind, value: &str, start: u32, end: u32) -> Token {
        Token {
            kind,
            value: value.to_string(),
            span: Span::new(BytePos(start), BytePos(end)),
        }
    }

    #[test]
    fn test_expect_error_single() {
        let token = make_token(TokenKind::Identifier, "Page", 0, 4);
        let err = ExpectError::single(TokenKind::LBrace, token);
        
        assert_eq!(err.expected.len(), 1);
        assert!(err.format_message().contains("Expected LBrace"));
        assert!(err.format_message().contains("found Identifier"));
    }

    #[test]
    fn test_expect_error_multiple() {
        let token = make_token(TokenKind::Comma, ",", 0, 1);
        let err = ExpectError::new(
            vec![TokenKind::Identifier, TokenKind::LBrace, TokenKind::StringLiteral],
            token,
        );
        
        let msg = err.format_message();
        assert!(msg.contains("Identifier"));
        assert!(msg.contains("LBrace"));
        assert!(msg.contains("StringLiteral"));
        assert!(msg.contains("or"));
    }

    #[test]
    fn test_expect_error_two() {
        let token = make_token(TokenKind::Comma, ",", 0, 1);
        let err = ExpectError::new(
            vec![TokenKind::Identifier, TokenKind::LBrace],
            token,
        );
        
        let msg = err.format_message();
        assert!(msg.contains("Identifier or LBrace"));
    }

    #[test]
    fn test_syntax_error() {
        let span = Span::new(BytePos(0), BytePos(4));
        let err = SyntaxError::new("Invalid syntax".to_string(), span);
        
        assert_eq!(err.message, "Invalid syntax");
        assert_eq!(err.span, span);
    }

    #[test]
    fn test_parse_error_conversion() {
        let token = make_token(TokenKind::Identifier, "test", 0, 4);
        let expect_err = ExpectError::single(TokenKind::LBrace, token);
        let parse_err: ParseError = expect_err.into();
        
        assert!(matches!(parse_err, ParseError::Expect(_)));
    }
}
