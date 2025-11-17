use hola_parser::tokenizer::{Tokenizer, TokenKind};
use hola_parser::{compile};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_color_tokenization_hex3() {
        let source = "color: #abc";
        let mut tokenizer = Tokenizer::new(source);
        
        let tokens: Vec<_> = tokenizer.collect();
        
        assert!(tokens.iter().any(|t| t.kind == TokenKind::ColorLiteral && t.value == "#abc"));
    }

    #[test]
    fn test_color_tokenization_hex6() {
        let source = "color: #FF0000";
        let mut tokenizer = Tokenizer::new(source);
        
        let tokens: Vec<_> = tokenizer.collect();
        
        assert!(tokens.iter().any(|t| t.kind == TokenKind::ColorLiteral && t.value == "#FF0000"));
    }

    #[test]
    fn test_color_tokenization_hex8() {
        let source = "color: #FF0000FF";
        let mut tokenizer = Tokenizer::new(source);
        
        let tokens: Vec<_> = tokenizer.collect();
        
        assert!(tokens.iter().any(|t| t.kind == TokenKind::ColorLiteral && t.value == "#FF0000FF"));
    }

    #[test]
    fn test_color_in_object() {
        let source = r#"
Page {
    backgroundColor: #FF0000
    textColor: #333
}
"#;
        let result = compile(source);
        assert!(result.is_ok());
        let json = result.unwrap();
        
        // Verify the color values are in the compiled output
        let json_str = json.to_string();
        assert!(json_str.contains("#FF0000"));
        assert!(json_str.contains("#333"));
    }

    #[test]
    fn test_division_operator_in_default_mode() {
        let source = "value: 10 / 2";
        let mut tokenizer = Tokenizer::new(source);
        
        let tokens: Vec<_> = tokenizer.collect();
        
        // Should have Slash token, not Unknown
        assert!(tokens.iter().any(|t| t.kind == TokenKind::Slash && t.value == "/"));
    }

    #[test]
    fn test_division_in_expression() {
        let source = r#"
Page {
    result: {{ 10 / 2 }}
    calculation: {{ (100 / 5) + 3 }}
}
"#;
        let result = compile(source);
        assert!(result.is_ok());
    }

    #[test]
    fn test_comment_vs_division() {
        let source = r#"
Page {
    // This is a comment
    value: 10 / 2
}
"#;
        let mut tokenizer = Tokenizer::new(source);
        let tokens: Vec<_> = tokenizer.collect();
        
        // Should have both Comment and Slash tokens
        assert!(tokens.iter().any(|t| t.kind == TokenKind::Comment));
        assert!(tokens.iter().any(|t| t.kind == TokenKind::Slash));
    }

    #[test]
    fn test_color_in_expression() {
        let source = r#"
Page {
    color: {{ #FF0000 }}
}
"#;
        let result = compile(source);
        assert!(result.is_ok());
        let json = result.unwrap();
        let json_str = json.to_string();
        assert!(json_str.contains("#FF0000"));
    }

    #[test]
    fn test_multiple_colors() {
        let source = r#"
Page {
    primary: #FF0000
    secondary: #00FF00
    tertiary: #0000FF
    alpha: #FF0000AA
}
"#;
        let result = compile(source);
        assert!(result.is_ok());
        let json = result.unwrap();
        let json_str = json.to_string();
        
        assert!(json_str.contains("#FF0000"));
        assert!(json_str.contains("#00FF00"));
        assert!(json_str.contains("#0000FF"));
        assert!(json_str.contains("#FF0000AA"));
    }

    #[test]
    fn test_division_with_other_operators() {
        let source = r#"
Page {
    calc1: {{ 10 / 2 + 3 }}
    calc2: {{ 20 - 10 / 2 }}
    calc3: {{ 100 / 10 * 5 }}
}
"#;
        let result = compile(source);
        assert!(result.is_ok());
    }

    #[test]
    fn test_invalid_color_format() {
        // Colors with invalid lengths should be treated as unknown
        let source = "color: #12";
        let mut tokenizer = Tokenizer::new(source);
        
        let tokens: Vec<_> = tokenizer.collect();
        
        // Should be Unknown, not ColorLiteral
        assert!(tokens.iter().any(|t| t.kind == TokenKind::Unknown && t.value == "#12"));
    }
}
