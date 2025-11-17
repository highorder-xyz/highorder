/// Utilities for transforming names between different cases

/// Transform a PascalCase or camelCase name to kebab-case
/// 
/// # Examples
/// ```
/// use hola_parser::name_transform::pascal_to_kebab;
/// assert_eq!(pascal_to_kebab("PageModal"), "page-modal");
/// assert_eq!(pascal_to_kebab("UserProfile"), "user-profile");
/// assert_eq!(pascal_to_kebab("HTTPServer"), "http-server");
/// assert_eq!(pascal_to_kebab("IOError"), "io-error");
/// assert_eq!(pascal_to_kebab("simpleCase"), "simple-case");
/// assert_eq!(pascal_to_kebab("page"), "page");
/// assert_eq!(pascal_to_kebab(""), "");
/// ```
pub fn pascal_to_kebab(name: &str) -> String {
    if name.is_empty() {
        return String::new();
    }

    let mut result = String::new();
    let chars: Vec<char> = name.chars().collect();
    
    for (i, &ch) in chars.iter().enumerate() {
        if ch.is_ascii_uppercase() {
            // Add hyphen before uppercase letter if:
            // 1. Not the first character
            // 2. Previous character is lowercase or next character is lowercase
            if i > 0 {
                let prev_is_lower = chars[i - 1].is_ascii_lowercase();
                let next_is_lower = i + 1 < chars.len() && chars[i + 1].is_ascii_lowercase();
                
                if prev_is_lower || next_is_lower {
                    result.push('-');
                }
            }
            result.push(ch.to_ascii_lowercase());
        } else {
            result.push(ch);
        }
    }
    
    result
}

/// Transform a kebab-case name to PascalCase
/// 
/// # Examples
/// ```
/// use hola_parser::name_transform::kebab_to_pascal;
/// assert_eq!(kebab_to_pascal("page-modal"), "PageModal");
/// assert_eq!(kebab_to_pascal("user-profile"), "UserProfile");
/// assert_eq!(kebab_to_pascal("page"), "Page");
/// assert_eq!(kebab_to_pascal(""), "");
/// ```
pub fn kebab_to_pascal(name: &str) -> String {
    if name.is_empty() {
        return String::new();
    }

    let mut result = String::new();
    let mut capitalize_next = true;
    
    for ch in name.chars() {
        if ch == '-' {
            capitalize_next = true;
        } else if capitalize_next {
            result.push(ch.to_ascii_uppercase());
            capitalize_next = false;
        } else {
            result.push(ch);
        }
    }
    
    result
}

/// Transform a snake_case name to camelCase
/// 
/// # Examples
/// ```
/// use hola_parser::name_transform::snake_to_camel;
/// assert_eq!(snake_to_camel("user_name"), "userName");
/// assert_eq!(snake_to_camel("http_server"), "httpServer");
/// assert_eq!(snake_to_camel("name"), "name");
/// ```
pub fn snake_to_camel(name: &str) -> String {
    if name.is_empty() {
        return String::new();
    }

    let mut result = String::new();
    let mut capitalize_next = false;
    
    for ch in name.chars() {
        if ch == '_' {
            capitalize_next = true;
        } else if capitalize_next {
            result.push(ch.to_ascii_uppercase());
            capitalize_next = false;
        } else {
            result.push(ch);
        }
    }
    
    result
}

/// Transform a camelCase or PascalCase name to snake_case
/// 
/// # Examples
/// ```
/// use hola_parser::name_transform::camel_to_snake;
/// assert_eq!(camel_to_snake("userName"), "user_name");
/// assert_eq!(camel_to_snake("HTTPServer"), "http_server");
/// assert_eq!(camel_to_snake("IOError"), "io_error");
/// ```
pub fn camel_to_snake(name: &str) -> String {
    if name.is_empty() {
        return String::new();
    }

    let mut result = String::new();
    let chars: Vec<char> = name.chars().collect();
    
    for (i, &ch) in chars.iter().enumerate() {
        if ch.is_ascii_uppercase() {
            if i > 0 {
                let prev_is_lower = chars[i - 1].is_ascii_lowercase();
                let next_is_lower = i + 1 < chars.len() && chars[i + 1].is_ascii_lowercase();
                
                if prev_is_lower || next_is_lower {
                    result.push('_');
                }
            }
            result.push(ch.to_ascii_lowercase());
        } else {
            result.push(ch);
        }
    }
    
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_pascal_to_kebab_simple() {
        assert_eq!(pascal_to_kebab("Page"), "page");
        assert_eq!(pascal_to_kebab("PageModal"), "page-modal");
        assert_eq!(pascal_to_kebab("UserProfile"), "user-profile");
    }

    #[test]
    fn test_pascal_to_kebab_consecutive_uppercase() {
        assert_eq!(pascal_to_kebab("HTTPServer"), "http-server");
        assert_eq!(pascal_to_kebab("IOError"), "io-error");
        assert_eq!(pascal_to_kebab("XMLParser"), "xml-parser");
    }

    #[test]
    fn test_pascal_to_kebab_camel_case() {
        assert_eq!(pascal_to_kebab("simpleCase"), "simple-case");
        assert_eq!(pascal_to_kebab("userName"), "user-name");
    }

    #[test]
    fn test_pascal_to_kebab_edge_cases() {
        assert_eq!(pascal_to_kebab(""), "");
        assert_eq!(pascal_to_kebab("page"), "page");
        assert_eq!(pascal_to_kebab("A"), "a");
        assert_eq!(pascal_to_kebab("AB"), "ab");
    }

    #[test]
    fn test_kebab_to_pascal() {
        assert_eq!(kebab_to_pascal("page"), "Page");
        assert_eq!(kebab_to_pascal("page-modal"), "PageModal");
        assert_eq!(kebab_to_pascal("user-profile"), "UserProfile");
        assert_eq!(kebab_to_pascal("http-server"), "HttpServer");
        assert_eq!(kebab_to_pascal(""), "");
    }

    #[test]
    fn test_snake_to_camel() {
        assert_eq!(snake_to_camel("user_name"), "userName");
        assert_eq!(snake_to_camel("http_server"), "httpServer");
        assert_eq!(snake_to_camel("name"), "name");
        assert_eq!(snake_to_camel(""), "");
    }

    #[test]
    fn test_camel_to_snake() {
        assert_eq!(camel_to_snake("userName"), "user_name");
        assert_eq!(camel_to_snake("HTTPServer"), "http_server");
        assert_eq!(camel_to_snake("IOError"), "io_error");
        assert_eq!(camel_to_snake("page"), "page");
        assert_eq!(camel_to_snake(""), "");
    }

    #[test]
    fn test_round_trip_pascal_kebab() {
        let original = "UserProfile";
        let kebab = pascal_to_kebab(original);
        let back = kebab_to_pascal(&kebab);
        assert_eq!(back, original);
    }

    #[test]
    fn test_round_trip_snake_camel() {
        let original = "user_name";
        let camel = snake_to_camel(original);
        let back = camel_to_snake(&camel);
        assert_eq!(back, original);
    }
}
