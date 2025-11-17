use hola_parser::tokenizer::{Tokenizer, TokenKind};
use hola_parser::token_stream::TokenStream;
use hola_parser::error::{ExpectError, ParseError};
use hola_parser::name_transform::{pascal_to_kebab, kebab_to_pascal};

fn main() {
    println!("=== Hola Parser New Features Demo ===\n");

    // Demo 1: TokenStream usage
    demo_token_stream();
    
    // Demo 2: ExpectError usage
    demo_expect_error();
    
    // Demo 3: Name transformation
    demo_name_transform();
}

fn demo_token_stream() {
    println!("--- 1. TokenStream Demo ---");
    
    let source = r#"
Page {
    route: "/home"
    name: "HomePage"
}
"#;

    let tokenizer = Tokenizer::new(source);
    let tokens: Vec<_> = tokenizer.collect();
    let mut stream = TokenStream::new(tokens);

    println!("Source code:");
    println!("{}", source);
    println!("\nToken stream operations:");

    // Consume all line breaks at the start
    let consumed = stream.consume(TokenKind::LineBreak);
    println!("Consumed {} line breaks", consumed);

    // Peek ahead without consuming
    if let Some(token) = stream.peek() {
        println!("Current token: {:?} = '{}'", token.kind, token.value);
    }

    if let Some(token) = stream.peek_next(1) {
        println!("Next token: {:?} = '{}'", token.kind, token.value);
    }

    // Expect specific token
    match stream.expect(TokenKind::Identifier) {
        Ok(token) => println!("Successfully got Identifier: '{}'", token.value),
        Err(e) => println!("Error: {}", e),
    }

    // Consume multiple token types at once
    stream.consume_any(&[TokenKind::LineBreak, TokenKind::Comma]);
    
    println!("Position in stream: {}", stream.position());
    println!("Reached end? {}\n", stream.eof());
}

fn demo_expect_error() {
    println!("--- 2. ExpectError Demo ---");
    
    let source = "Page , route: \"/home\"";
    let tokenizer = Tokenizer::new(source);
    let tokens: Vec<_> = tokenizer.collect();
    let mut stream = TokenStream::new(tokens);

    println!("Source code: {}", source);
    
    // Move to the comma token
    stream.next(); // Skip "Page"
    
    if let Some(token) = stream.peek() {
        // Create an ExpectError showing we expected LBrace but got Comma
        let error = ExpectError::single(TokenKind::LBrace, token.clone());
        println!("\nSingle expect error:");
        println!("{}", error.format_message());
        
        // Create an error with multiple expected tokens
        let error_multi = ExpectError::new(
            vec![TokenKind::LBrace, TokenKind::Identifier, TokenKind::StringLiteral],
            token.clone(),
        );
        println!("\nMultiple expect error:");
        println!("{}", error_multi.format_message());

        // Convert to ParseError
        let parse_error: ParseError = error.into();
        println!("\nAs ParseError:");
        println!("{}", parse_error);
    }
    
    println!();
}

fn demo_name_transform() {
    println!("--- 3. Name Transformation Demo ---");
    
    let test_cases = vec![
        "Page",
        "PageModal",
        "UserProfile",
        "HTTPServer",
        "IOError",
        "XMLParser",
        "simpleCase",
    ];

    println!("PascalCase → kebab-case transformations:");
    for name in &test_cases {
        let kebab = pascal_to_kebab(name);
        println!("  {} → {}", name, kebab);
    }

    println!("\nRound-trip test (PascalCase → kebab-case → PascalCase):");
    for name in &test_cases {
        let kebab = pascal_to_kebab(name);
        let back = kebab_to_pascal(&kebab);
        let status = if back == *name { "✓" } else { "✗" };
        println!("  {} {} → {} → {}", status, name, kebab, back);
    }

    println!("\nCommon Hola object type transformations:");
    let object_types = vec![
        ("Page", "page"),
        ("PageModal", "page-modal"),
        ("UserProfile", "user-profile"),
        ("ActionButton", "action-button"),
        ("NavigationBar", "navigation-bar"),
    ];
    
    for (pascal, expected_kebab) in object_types {
        let kebab = pascal_to_kebab(pascal);
        let status = if kebab == expected_kebab { "✓" } else { "✗" };
        println!("  {} {} → {} (expected: {})", status, pascal, kebab, expected_kebab);
    }
    
    println!();
}
