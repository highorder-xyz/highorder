
pub mod ast;
pub mod tokenizer;
pub mod parser;
pub mod expression_parser;
pub mod compiler;
pub mod position;
pub mod token_stream;
pub mod error;
pub mod name_transform;

use serde_json::Value;
use crate::parser::Parser;
use crate::compiler::Compiler as AstCompiler;
use crate::position::{Diagnostic, LineOffsets};

/// Compilation result with diagnostics
pub struct CompileResult {
    pub value: Option<Value>,
    pub diagnostics: Vec<Diagnostic>,
}

/// Compiles a Hola source string into a serde_json::Value.
///
/// # Panics
///
/// This function will panic if parsing or compiling fails. This is a placeholder
/// and should be replaced with proper error handling.
///
pub fn compile(source: &str) -> Result<Value, String> {
    let mut parser = Parser::new(source);
    let ast_root = parser.parse()?;

    let compiler = AstCompiler::new();
    let json_output = compiler.compile(&ast_root);

    Ok(json_output)
}

/// Compiles a Hola source string with detailed diagnostics.
pub fn compile_with_diagnostics(source: &str) -> CompileResult {
    let mut parser = Parser::new(source);
    let mut diagnostics = Vec::new();
    
    match parser.parse() {
        Ok(ast_root) => {
            let compiler = AstCompiler::new();
            let json_output = compiler.compile(&ast_root);
            CompileResult {
                value: Some(json_output),
                diagnostics,
            }
        }
        Err(error_msg) => {
            // For now, we create a generic error diagnostic
            // In future, parser should return Diagnostic objects
            diagnostics.push(Diagnostic::error(
                crate::position::Span::empty(),
                error_msg,
            ));
            CompileResult {
                value: None,
                diagnostics,
            }
        }
    }
}

/// Format diagnostics with source context
pub fn format_diagnostics(source: &str, diagnostics: &[Diagnostic]) -> String {
    let line_offsets = LineOffsets::new(source);
    let mut result = String::new();
    
    for (i, diagnostic) in diagnostics.iter().enumerate() {
        if i > 0 {
            result.push_str("\n\n");
        }
        result.push_str(&diagnostic.format(source, &line_offsets));
    }
    
    result
}
