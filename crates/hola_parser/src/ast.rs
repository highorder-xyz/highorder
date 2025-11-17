use std::collections::HashMap;

// The root of a Hola file, containing a list of top-level objects.
#[derive(Debug, PartialEq, Clone)]
pub struct AstRoot {
    pub objects: Vec<ObjectNode>,
}

// Represents a Hola object, like `Page { ... }`
#[derive(Debug, PartialEq, Clone)]
pub struct ObjectNode {
    pub name: String, // e.g., "Page". Empty for anonymous objects.
    pub properties: HashMap<String, PropertyValue>,
    pub children: Vec<ObjectNode>,
}

// Represents the value of a property. It can be a static literal value
// or a dynamic expression to be evaluated.
#[derive(Debug, PartialEq, Clone)]
pub enum PropertyValue {
    Literal(LiteralKind),
    List(Vec<PropertyValue>),
    Object(ObjectNode),      // For anonymous objects as property values
    Expression(Expr),        // For dynamic expressions like `{{ user.name }}`
}

// Represents literal values in Hola.
#[derive(Debug, PartialEq, Clone)]
pub enum LiteralKind {
    String(String),
    Number(NumberValue),
    Bool(bool),
    Null,
    Color(String),  // Color literal like #FF0000, #123, rgb(255,0,0)
}

#[derive(Debug, PartialEq, Clone)]
pub enum NumberValue {
    Int(i64),
    Float(f64),
}


// --- Expression AST (to be populated from expression_parser.rs) ---

// Represents an expression inside `{{ ... }}`
#[derive(Debug, PartialEq, Clone)]
pub enum Expr {
    Binary(Box<Expr>, BinaryOperator, Box<Expr>),
    Logical(Box<Expr>, LogicalOperator, Box<Expr>),
    Unary(UnaryOperator, Box<Expr>),
    Variable(String),
    Call(Box<Expr>, Vec<Expr>), // e.g., function(arg1, arg2)
    Get(Box<Expr>, String),    // e.g., user.name
    Literal(LiteralKind),
    Grouping(Box<Expr>),       // For grouping with parentheses (expr)
    List(Vec<Expr>),           // For list literals [item1, item2, ...]
    ListGet(Box<Expr>, Box<Expr>), // For list access list[index]
}

#[derive(Debug, PartialEq, Copy, Clone)]
pub enum BinaryOperator {
    Add,      // +
    Subtract, // -
    Multiply, // *
    Divide,   // /
    Equal,    // ==
    NotEqual, // !=
    Less,     // <
    LessEqual, // <=
    Greater,  // >
    GreaterEqual, // >=
}

#[derive(Debug, PartialEq, Copy, Clone)]
pub enum UnaryOperator {
    Not,   // !
    Negate, // -
}

#[derive(Debug, PartialEq, Copy, Clone)]
pub enum LogicalOperator {
    And,      // &&
    Or,       // ||
}
