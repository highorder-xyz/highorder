use hola_parser::{compile_with_diagnostics, format_diagnostics};
use hola_parser::position::{Diagnostic, Span, BytePos, LineOffsets};

fn main() {
    println!("=== Hola Parser Diagnostic System Demo ===\n");

    // Example 1: Successful compilation
    println!("Example 1: Successful Compilation");
    println!("----------------------------------");
    let good_source = r#"
Page {
    title: "Hello World"
    count: 42
}
"#;
    
    let result = compile_with_diagnostics(good_source);
    if result.value.is_some() {
        println!("✓ Compilation successful!");
        println!("Generated JSON: {}", serde_json::to_string_pretty(&result.value.unwrap()).unwrap());
    }
    println!();

    // Example 2: Compilation with errors
    println!("Example 2: Compilation Error");
    println!("-----------------------------");
    let bad_source = r#"
Page {
    title: "Incomplete
"#;
    
    let result = compile_with_diagnostics(bad_source);
    if !result.diagnostics.is_empty() {
        println!("✗ Compilation failed with {} error(s):", result.diagnostics.len());
        let formatted = format_diagnostics(bad_source, &result.diagnostics);
        println!("{}", formatted);
    }
    println!();

    // Example 3: Custom diagnostic creation
    println!("Example 3: Custom Diagnostic Messages");
    println!("-------------------------------------");
    let source = "Page {\n  name: 123\n  age: \"thirty\"\n}";
    let line_offsets = LineOffsets::new(source);
    
    let diagnostics = vec![
        Diagnostic::error(
            Span::new(BytePos(15), BytePos(18)),
            "Type error: 'name' expects a string, but got a number".to_string(),
        ),
        Diagnostic::error(
            Span::new(BytePos(27), BytePos(35)),
            "Type error: 'age' expects a number, but got a string".to_string(),
        ),
        Diagnostic::warning(
            Span::new(BytePos(0), BytePos(4)),
            "Deprecated: 'Page' is deprecated, use 'Container' instead".to_string(),
        ),
    ];
    
    for diagnostic in &diagnostics {
        println!("{}\n", diagnostic.format(source, &line_offsets));
    }

    // Example 4: Position tracking
    println!("Example 4: Position Tracking");
    println!("----------------------------");
    println!("Source: {}", source);
    println!("\nLine/Column information:");
    println!("  Line 1 starts at byte {}", line_offsets.line_start(1));
    println!("  Line 2 starts at byte {}", line_offsets.line_start(2));
    println!("  Line 3 starts at byte {}", line_offsets.line_start(3));
    println!("  Total lines: {}", line_offsets.line_count());
    println!();

    // Example 5: Expression with detailed error location
    println!("Example 5: Detailed Expression Error");
    println!("------------------------------------");
    let expr_source = "{{ (x + y) * }}";
    let expr_line_offsets = LineOffsets::new(expr_source);
    
    let expr_error = Diagnostic::error(
        Span::new(BytePos(13), BytePos(14)),
        "Unexpected token '}', expected an expression".to_string(),
    );
    
    println!("{}", expr_error.format(expr_source, &expr_line_offsets));
}
