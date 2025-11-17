#[cfg(test)]
mod tests {
    use hola_parser::{compile_with_diagnostics, format_diagnostics};
    use hola_parser::position::{Diagnostic, Span, BytePos, LineOffsets, DiagnosticLevel};

    #[test]
    fn test_successful_compilation_with_diagnostics() {
        let source = r#"
        Page {
            title: "Hello World"
        }
        "#;
        
        let result = compile_with_diagnostics(source);
        
        // Should succeed with no diagnostics
        assert!(result.value.is_some());
        assert_eq!(result.diagnostics.len(), 0);
    }

    #[test]
    fn test_compilation_error_with_diagnostics() {
        let source = r#"
        Page {
            title: "Hello"
            // Missing closing brace
        "#;
        
        let result = compile_with_diagnostics(source);
        
        // Should fail with diagnostics
        assert!(result.value.is_none());
        assert!(!result.diagnostics.is_empty());
        
        // Print formatted diagnostics
        let formatted = format_diagnostics(source, &result.diagnostics);
        println!("Formatted diagnostics:\n{}", formatted);
        
        // Verify it contains error information
        assert!(formatted.contains("error"));
    }

    #[test]
    fn test_diagnostic_formatting_with_context() {
        let source = "Page {\n  name: 123\n  title: \"test\"\n}";
        let line_offsets = LineOffsets::new(source);
        
        // Create a diagnostic for the number 123
        let diagnostic = Diagnostic::error(
            Span::new(BytePos(15), BytePos(18)),
            "Type mismatch: expected string, found number".to_string(),
        );
        
        let formatted = diagnostic.format(source, &line_offsets);
        println!("\nFormatted diagnostic with context:\n{}", formatted);
        
        // Verify the formatted output contains key information
        assert!(formatted.contains("error"));
        assert!(formatted.contains("line 2"));
        assert!(formatted.contains("Type mismatch"));
        assert!(formatted.contains("123"));
        assert!(formatted.contains("^^^")); // Should highlight the error
    }

    #[test]
    fn test_multiple_diagnostics() {
        let source = "Page {\n  name: 123\n  count: \"abc\"\n}";
        let line_offsets = LineOffsets::new(source);
        
        let diagnostics = vec![
            Diagnostic::error(
                Span::new(BytePos(15), BytePos(18)),
                "Expected string for name".to_string(),
            ),
            Diagnostic::error(
                Span::new(BytePos(30), BytePos(35)),
                "Expected number for count".to_string(),
            ),
        ];
        
        let formatted = format_diagnostics(source, &diagnostics);
        println!("\nMultiple diagnostics:\n{}", formatted);
        
        // Should contain both errors
        assert!(formatted.contains("Expected string for name"));
        assert!(formatted.contains("Expected number for count"));
    }

    #[test]
    fn test_warning_and_error_levels() {
        let source = "Page { title: \"test\" }";
        let line_offsets = LineOffsets::new(source);
        
        let warning = Diagnostic::warning(
            Span::new(BytePos(0), BytePos(4)),
            "Page is deprecated, use Container instead".to_string(),
        );
        
        let error = Diagnostic::error(
            Span::new(BytePos(14), BytePos(20)),
            "Invalid string format".to_string(),
        );
        
        let info = Diagnostic::info(
            Span::new(BytePos(7), BytePos(12)),
            "Property 'title' is optional".to_string(),
        );
        
        let warning_fmt = warning.format(source, &line_offsets);
        let error_fmt = error.format(source, &line_offsets);
        let info_fmt = info.format(source, &line_offsets);
        
        println!("\nWarning:\n{}", warning_fmt);
        println!("\nError:\n{}", error_fmt);
        println!("\nInfo:\n{}", info_fmt);
        
        assert!(warning_fmt.contains("warning"));
        assert!(error_fmt.contains("error"));
        assert!(info_fmt.contains("info"));
    }

    #[test]
    fn test_multiline_diagnostic() {
        let source = "Page {\n  items: [\n    1,\n    2,\n    3\n  ]\n}";
        let line_offsets = LineOffsets::new(source);
        
        // Diagnostic spanning multiple lines
        let diagnostic = Diagnostic::warning(
            Span::new(BytePos(17), BytePos(35)),
            "Large array literal, consider using data binding".to_string(),
        );
        
        let formatted = diagnostic.format(source, &line_offsets);
        println!("\nMultiline diagnostic:\n{}", formatted);
        
        assert!(formatted.contains("warning"));
        assert!(formatted.contains("Large array literal"));
    }

    #[test]
    fn test_exact_token_location() {
        let source = "{{ x + y + z }}";
        let line_offsets = LineOffsets::new(source);
        
        // Error on the second '+' operator
        let diagnostic = Diagnostic::error(
            Span::new(BytePos(9), BytePos(10)),
            "Unexpected operator".to_string(),
        );
        
        let formatted = diagnostic.format(source, &line_offsets);
        println!("\nExact token location:\n{}", formatted);
        
        // Verify it points to the correct position
        assert!(formatted.contains("column 10"));
        assert!(formatted.contains("Unexpected operator"));
    }
}
