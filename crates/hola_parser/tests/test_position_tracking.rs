#[cfg(test)]
mod tests {
    use hola_parser::tokenizer::Tokenizer;
    use hola_parser::position::{LineOffsets, Diagnostic, DiagnosticLevel, Span, BytePos};

    #[test]
    fn test_tokenizer_with_spans() {
        let source = "{{ x + 1 }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        
        // Check that tokens have correct spans
        assert_eq!(tokens[0].value, "{{");
        assert_eq!(tokens[0].span.start.0, 0);
        assert_eq!(tokens[0].span.end.0, 2);
        
        assert_eq!(tokens[1].value, "x");
        assert_eq!(tokens[1].span.start.0, 3);
        assert_eq!(tokens[1].span.end.0, 4);
        
        assert_eq!(tokens[2].value, "+");
        assert_eq!(tokens[2].span.start.0, 5);
        assert_eq!(tokens[2].span.end.0, 6);
    }

    #[test]
    fn test_line_offsets_calculation() {
        let source = "Page {\n  name: {{ x }}\n}";
        let line_offsets = LineOffsets::new(source);
        
        // Test line numbers
        assert_eq!(line_offsets.line(BytePos(0)), 1); // P
        assert_eq!(line_offsets.line(BytePos(7)), 2); // space before name
        assert_eq!(line_offsets.line(BytePos(23)), 3); // }
        
        // Test columns
        assert_eq!(line_offsets.column(BytePos(0)), 1);
        assert_eq!(line_offsets.column(BytePos(9)), 3); // n in name (line starts at 7, so 9-7+1=3)
        assert_eq!(line_offsets.column(BytePos(15)), 9); // {
    }

    #[test]
    fn test_diagnostic_formatting() {
        let source = "Page {\n  name: 123\n}";
        let line_offsets = LineOffsets::new(source);
        
        // Create a diagnostic for the number 123
        let diagnostic = Diagnostic::error(
            Span::new(BytePos(15), BytePos(18)),
            "Expected string, found number".to_string(),
        );
        
        let formatted = diagnostic.format(source, &line_offsets);
        println!("Formatted diagnostic:\n{}", formatted);
        
        assert!(formatted.contains("error"));
        assert!(formatted.contains("line 2"));
        assert!(formatted.contains("Expected string, found number"));
        assert!(formatted.contains("123"));
    }

    #[test]
    fn test_diagnostic_levels() {
        let span = Span::new(BytePos(0), BytePos(5));
        
        let error = Diagnostic::error(span, "This is an error".to_string());
        assert_eq!(error.level, DiagnosticLevel::Error);
        
        let warning = Diagnostic::warning(span, "This is a warning".to_string());
        assert_eq!(warning.level, DiagnosticLevel::Warning);
        
        let info = Diagnostic::info(span, "This is info".to_string());
        assert_eq!(info.level, DiagnosticLevel::Info);
    }

    #[test]
    fn test_multiline_source_tracking() {
        let source = "Page {\n  title: \"Hello\"\n  items: {{ list }}\n}";
        let line_offsets = LineOffsets::new(source);
        
        assert_eq!(line_offsets.line_count(), 4);
        assert_eq!(line_offsets.line_start(1), 0);
        assert_eq!(line_offsets.line_start(2), 7);
        assert_eq!(line_offsets.line_start(3), 24);
        assert_eq!(line_offsets.line_start(4), 44);
    }

    #[test]
    fn test_span_operations() {
        let span1 = Span::new(BytePos(10), BytePos(20));
        let span2 = Span::new(BytePos(15), BytePos(30));
        
        let union = Span::union_span(span1, span2);
        assert_eq!(union.start.0, 10);
        assert_eq!(union.end.0, 30);
        
        assert_eq!(span1.len(), 10);
        assert!(!span1.is_empty());
        
        let empty = Span::empty();
        assert!(empty.is_empty());
    }

    #[test]
    fn test_complex_expression_with_spans() {
        let source = "{{ (x + y) * z[0] }}";
        let tokens: Vec<_> = Tokenizer::new(source).collect();
        
        println!("Tokens with spans:");
        for (i, token) in tokens.iter().enumerate() {
            println!("  {}: {:?} '{}' [{}-{}]", 
                i, token.kind, token.value, 
                token.span.start.0, token.span.end.0);
        }
        
        // Verify some key tokens
        let left_paren = tokens.iter().find(|t| t.value == "(").unwrap();
        assert!(left_paren.span.start.0 == 3);
        
        let right_bracket = tokens.iter().find(|t| t.value == "]").unwrap();
        assert!(right_bracket.span.start.0 == 16);
    }
}
