use hola_parser::{compile};

fn main() {
    println!("=== Color Literal and Division Operator Demo ===\n");

    // Demo 1: Color Literals
    demo_color_literals();
    
    // Demo 2: Division Operator
    demo_division_operator();
    
    // Demo 3: Combined Usage
    demo_combined();
}

fn demo_color_literals() {
    println!("--- 1. Color Literals Demo ---");
    
    let source = r#"
Page {
    backgroundColor: #FF0000
    textColor: #333
    borderColor: #00FF00AA
    accentColor: #abc
}
"#;

    println!("Source code:");
    println!("{}", source);

    match compile(source) {
        Ok(json) => {
            println!("Compiled successfully!");
            println!("JSON output:");
            println!("{}\n", serde_json::to_string_pretty(&json).unwrap());
        }
        Err(e) => println!("Error: {}\n", e),
    }
}

fn demo_division_operator() {
    println!("--- 2. Division Operator Demo ---");
    
    let source = r#"
Calculator {
    // Division in expressions
    result1: {{ 20 / 4 }}
    result2: {{ (100 / 5) + 10 }}
    result3: {{ 50 - (30 / 3) }}
    complex: {{ 100 / 2 / 5 }}
}
"#;

    println!("Source code:");
    println!("{}", source);

    match compile(source) {
        Ok(json) => {
            println!("Compiled successfully!");
            println!("JSON output:");
            println!("{}\n", serde_json::to_string_pretty(&json).unwrap());
        }
        Err(e) => println!("Error: {}\n", e),
    }
}

fn demo_combined() {
    println!("--- 3. Combined Usage Demo ---");
    
    let source = r#"
ThemeConfig {
    // Comments work as before
    // This is a single-line comment
    
    // Colors
    primaryColor: #FF5733
    secondaryColor: #3498DB
    
    // Division operations
    spacing: {{ 16 / 2 }}
    padding: {{ 24 / 3 }}
    
    // Colors in expressions
    activeColor: {{ #00FF00 }}
    
    // Complex calculations
    columnWidth: {{ 100 / 3 }}
    
    Button {
        bgColor: #2ECC71
        textColor: #FFF
        height: {{ 48 / 2 }}
    }
}
"#;

    println!("Source code:");
    println!("{}", source);

    match compile(source) {
        Ok(json) => {
            println!("Compiled successfully!");
            println!("JSON output:");
            println!("{}\n", serde_json::to_string_pretty(&json).unwrap());
            
            // Demonstrate features
            println!("Features demonstrated:");
            println!("✓ Hex colors (#FF5733, #3498DB)");
            println!("✓ Short hex colors (#FFF)");
            println!("✓ Division in expressions ({{ 16 / 2 }})");
            println!("✓ Comments still work (// comment)");
            println!("✓ Colors in expressions ({{ #00FF00 }})");
            println!();
        }
        Err(e) => println!("Error: {}\n", e),
    }
}
