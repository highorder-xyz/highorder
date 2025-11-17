#[cfg(test)]
mod tests {
    use hola_parser::tokenizer::{Tokenizer, TokenKind};

    #[test]
    fn test_tokenizer_in_expression_mode() {
        let source = "{{ (1 + 2) }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        
        println!("Tokens:");
        for (i, token) in tokens.iter().enumerate() {
            println!("  {}: {:?} - '{}'", i, token.kind, token.value);
        }
        
        // Check that we have the expected tokens
        assert_eq!(tokens.len(), 7); // {{, (, 1, +, 2, ), }}, Eof
        assert_eq!(tokens[0].kind, TokenKind::LBraceLBrace);
        assert_eq!(tokens[1].kind, TokenKind::LParen);  // This should be LParen
        assert_eq!(tokens[2].kind, TokenKind::NumberLiteral);
        assert_eq!(tokens[3].kind, TokenKind::Plus);
        assert_eq!(tokens[4].kind, TokenKind::NumberLiteral);
        assert_eq!(tokens[5].kind, TokenKind::RParen);
        assert_eq!(tokens[6].kind, TokenKind::RBraceRBrace);
    }
    
    #[test]
    fn test_tokenizer_list_tokens() {
        let source = "{{ [1, 2] }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        
        println!("List Tokens:");
        for (i, token) in tokens.iter().enumerate() {
            println!("  {}: {:?} - '{}'", i, token.kind, token.value);
        }
        
        // Check that we have the expected tokens
        assert_eq!(tokens.len(), 7); // {{, [, 1, ,, 2, ], }}, Eof
        assert_eq!(tokens[0].kind, TokenKind::LBraceLBrace);
        assert_eq!(tokens[1].kind, TokenKind::LBracket);  // This should be LBracket
        assert_eq!(tokens[2].kind, TokenKind::NumberLiteral);
        assert_eq!(tokens[3].kind, TokenKind::Comma);
        assert_eq!(tokens[4].kind, TokenKind::NumberLiteral);
        assert_eq!(tokens[5].kind, TokenKind::RBracket);
        assert_eq!(tokens[6].kind, TokenKind::RBraceRBrace);
    }
}