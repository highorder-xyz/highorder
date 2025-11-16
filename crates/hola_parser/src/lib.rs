
pub mod ast;
pub mod tokenizer;
pub mod parser;
pub mod expression_parser;
pub mod compiler;

use serde_json::Value;
use crate::parser::Parser;
use crate::compiler::Compiler as AstCompiler;

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
