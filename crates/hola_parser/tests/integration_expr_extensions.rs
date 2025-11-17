#[cfg(test)]
mod tests {
    use hola_parser::{compile};

    #[test]
    fn test_grouping_in_hola_document() {
        let source = r#"
        Page {
            result: {{ (2 + 3) * 4 }}
        }
        "#;
        
        let ast = hola_parser::parser::Parser::new(source).parse().expect("Parsing failed");
        
        // Check that we have one object
        assert_eq!(ast.objects.len(), 1);
        
        let page = &ast.objects[0];
        assert_eq!(page.name, "Page");
        
        // Check that we have the result property
        assert!(page.properties.contains_key("result"));
        
        // Compile to JSON to verify the expression is correctly parsed
        let json_result = compile(source).expect("Compilation failed");
        println!("Compiled JSON: {:#?}", json_result);
    }

    #[test]
    fn test_list_literal_in_hola_document() {
        let source = r#"
        Page {
            items: {{ [1, 2, 3, 4, 5] }}
        }
        "#;
        
        let ast = hola_parser::parser::Parser::new(source).parse().expect("Parsing failed");
        
        // Check that we have one object
        assert_eq!(ast.objects.len(), 1);
        
        let page = &ast.objects[0];
        assert_eq!(page.name, "Page");
        
        // Check that we have the items property
        assert!(page.properties.contains_key("items"));
        
        // Compile to JSON to verify the expression is correctly parsed
        let json_result = compile(source).expect("Compilation failed");
        println!("Compiled JSON: {:#?}", json_result);
    }

    #[test]
    fn test_list_access_in_hola_document() {
        let source = r#"
        Page {
            firstItem: {{ [10, 20, 30][0] }}
        }
        "#;
        
        let ast = hola_parser::parser::Parser::new(source).parse().expect("Parsing failed");
        
        // Check that we have one object
        assert_eq!(ast.objects.len(), 1);
        
        let page = &ast.objects[0];
        assert_eq!(page.name, "Page");
        
        // Check that we have the firstItem property
        assert!(page.properties.contains_key("firstItem"));
        
        // Compile to JSON to verify the expression is correctly parsed
        let json_result = compile(source).expect("Compilation failed");
        println!("Compiled JSON: {:#?}", json_result);
    }

    #[test]
    fn test_complex_expressions_with_new_features() {
        let source = r#"
        Page {
            complexResult: {{ ([1, 2, 3][1] + 5) * 2 }}
        }
        "#;
        
        let ast = hola_parser::parser::Parser::new(source).parse().expect("Parsing failed");
        
        // Check that we have one object
        assert_eq!(ast.objects.len(), 1);
        
        let page = &ast.objects[0];
        assert_eq!(page.name, "Page");
        
        // Check that we have the complexResult property
        assert!(page.properties.contains_key("complexResult"));
        
        // Compile to JSON to verify the expression is correctly parsed
        let json_result = compile(source).expect("Compilation failed");
        println!("Compiled JSON: {:#?}", json_result);
    }
}