use serde_json::{Value, Map, Number};
use crate::ast::{AstRoot, ObjectNode, PropertyValue, LiteralKind, Expr};

pub struct Compiler {}

impl Compiler {
    pub fn new() -> Self {
        Compiler {}
    }

    pub fn compile(&self, root: &AstRoot) -> Value {
        let mut compiled_root = Map::new();
        // This part might need to be adjusted based on the desired final JSON structure.
        // For now, let's assume a simple list of objects.
        let objects: Vec<Value> = root.objects.iter().map(|obj| self.compile_object(obj)).collect();
        compiled_root.insert("objects".to_string(), Value::Array(objects));
        Value::Object(compiled_root)
    }

    fn compile_object(&self, node: &ObjectNode) -> Value {
        let mut obj = Map::new();
        obj.insert("type".to_string(), Value::String(node.name.clone()));

        let mut properties_map = Map::new();
        for (key, value) in &node.properties {
            properties_map.insert(key.clone(), self.compile_property_value(value));
        }
        obj.insert("properties".to_string(), Value::Object(properties_map));

        let children: Vec<Value> = node.children.iter().map(|child| self.compile_object(child)).collect();
        obj.insert("children".to_string(), Value::Array(children));

        Value::Object(obj)
    }

    fn compile_property_value(&self, value: &PropertyValue) -> Value {
        match value {
            PropertyValue::Literal(lit) => self.compile_literal(lit),
            PropertyValue::List(items) => {
                let compiled_items: Vec<Value> = items.iter().map(|item| self.compile_property_value(item)).collect();
                Value::Array(compiled_items)
            }
            PropertyValue::Object(obj_node) => self.compile_object(obj_node),
            PropertyValue::Expression(expr) => self.compile_expression(expr),
        }
    }

    fn compile_literal(&self, literal: &LiteralKind) -> Value {
        match literal {
            LiteralKind::String(s) => Value::String(s.clone()),
            LiteralKind::Number(crate::ast::NumberValue::Int(i)) => Value::Number(Number::from(*i)),
            LiteralKind::Number(crate::ast::NumberValue::Float(f)) => {
                // serde_json::Number::from_f64 returns Option
                Number::from_f64(*f).map(Value::Number).unwrap_or(Value::Null)
            }
            LiteralKind::Bool(b) => Value::Bool(*b),
            LiteralKind::Null => Value::Null,
        }
    }

    // This is a simple serialization of the expression.
    // A more advanced compiler might convert it to bytecode or another intermediate representation.
    fn compile_expression(&self, expr: &Expr) -> Value {
        let mut expr_map = Map::new();
        // We serialize the expression into a string format that a runtime could potentially evaluate.
        // This is a placeholder; a real implementation would be more robust.
        expr_map.insert("$expr".to_string(), Value::String(format!("{:?}", expr)));
        Value::Object(expr_map)
    }
}
