use std::fs;
use std::path::PathBuf;
use serde_json::Value;

fn read(path: PathBuf) -> String {
    fs::read_to_string(path).expect("failed to read file")
}

fn load_expected(name: &str) -> Value {
    let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    p.push("tests/fixtures/expected");
    p.push(format!("{}.json", name));
    let s = read(p);
    serde_json::from_str(&s).expect("invalid expected json")
}

fn compile_object(name: &str) -> Value {
    let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    p.push("tests/fixtures/objects");
    p.push(format!("{}.hola", name));
    let src = read(p);
    hola_parser::compile(&src).expect("compile failed")
}

#[test]
fn fixtures_simple() {
    let got = compile_object("simple");
    let exp = load_expected("simple");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_with_expression() {
    let got = compile_object("with_expression");
    let exp = load_expected("with_expression");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_list_empty_slots() {
    let got = compile_object("list_empty_slots");
    let exp = load_expected("list_empty_slots");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_nested_objects() {
    let got = compile_object("nested_objects");
    let exp = load_expected("nested_objects");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_primitive_values() {
    let got = compile_object("primitive_values");
    let exp = load_expected("primitive_values");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_complex_expressions() {
    let got = compile_object("complex_expressions");
    let exp = load_expected("complex_expressions");
    assert_eq!(got, exp);
}

#[test]
fn fixtures_anonymous_objects() {
    let got = compile_object("anonymous_objects");
    let exp = load_expected("anonymous_objects");
    assert_eq!(got, exp);
}
