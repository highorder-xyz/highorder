#[cfg(test)]
mod tests {
    use hola_parser::expression_parser::parse_expression;
    use hola_parser::tokenizer::{Tokenizer, TokenKind};
    use hola_parser::ast::{Expr, LiteralKind, NumberValue};

    #[test]
    fn test_grouping_expression() {
        let source = "{{ (1 + 2) }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        // Extract only the expression tokens (between {{ and }})
        let expr_tokens: Vec<_> = tokens.into_iter().skip(1).take_while(|t| t.kind != TokenKind::RBraceRBrace).collect();
        let expr = parse_expression(&expr_tokens).unwrap();
        
        // Should be a Grouping expression containing a Binary expression
        match expr {
            Expr::Grouping(boxed_expr) => {
                match *boxed_expr {
                    Expr::Binary(_, _, _) => {}, // Correct
                    _ => panic!("Expected Binary expression inside grouping"),
                }
            },
            _ => panic!("Expected Grouping expression"),
        }
    }

    #[test]
    fn test_list_literal() {
        let source = "{{ [1, 2, 3] }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        // Extract only the expression tokens (between {{ and }})
        let expr_tokens: Vec<_> = tokens.into_iter().skip(1).take_while(|t| t.kind != TokenKind::RBraceRBrace).collect();
        let expr = parse_expression(&expr_tokens).unwrap();
        
        match expr {
            Expr::List(items) => {
                assert_eq!(items.len(), 3);
                // Check first item is a literal 1
                match &items[0] {
                    Expr::Literal(LiteralKind::Number(NumberValue::Int(1))) => {},
                    _ => panic!("First item should be literal 1"),
                }
            },
            _ => panic!("Expected List expression"),
        }
    }

    #[test]
    fn test_empty_list() {
        let source = "{{ [] }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        // Extract only the expression tokens (between {{ and }})
        let expr_tokens: Vec<_> = tokens.into_iter().skip(1).take_while(|t| t.kind != TokenKind::RBraceRBrace).collect();
        let expr = parse_expression(&expr_tokens).unwrap();
        
        match expr {
            Expr::List(items) => {
                assert_eq!(items.len(), 0);
            },
            _ => panic!("Expected List expression"),
        }
    }

    #[test]
    fn test_list_access() {
        let source = "{{ arr[0] }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        // Extract only the expression tokens (between {{ and }})
        let expr_tokens: Vec<_> = tokens.into_iter().skip(1).take_while(|t| t.kind != TokenKind::RBraceRBrace).collect();
        let expr = parse_expression(&expr_tokens).unwrap();
        
        match expr {
            Expr::ListGet(_, _) => {}, // Correct
            _ => panic!("Expected ListGet expression"),
        }
    }
}