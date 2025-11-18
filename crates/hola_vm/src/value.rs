//! HOLA VM 值类型定义

use std::fmt;
use std::collections::HashMap;

/// HOLA 虚拟机支持的值类型
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    /// 整数类型
    Integer(i64),
    /// 浮点数类型
    Float(f64),
    /// 布尔类型
    Bool(bool),
    /// 字符串类型
    String(String),
    /// 数组类型
    Array(Vec<Value>),
    /// 对象类型（哈希表）
    Object(HashMap<String, Value>),
    /// 元组类型
    Tuple(Vec<Value>),
    /// 范围类型（起始值，结束值，是否包含结束值）
    Range(Option<i64>, Option<i64>, bool),
    /// 函数引用
    Function(u64),
    /// 异常值（异常类型，消息）
    Exception(String, String),
    /// 空值
    Null,
}

impl Value {
    /// 检查值是否为真
    pub fn is_truthy(&self) -> bool {
        match self {
            Value::Bool(b) => *b,
            Value::Null => false,
            Value::Integer(i) => *i != 0,
            Value::Float(f) => *f != 0.0,
            Value::String(s) => !s.is_empty(),
            Value::Array(a) => !a.is_empty(),
            Value::Object(o) => !o.is_empty(),
            Value::Tuple(t) => !t.is_empty(),
            Value::Range(_, _, _) => true,
            Value::Function(_) => true,
            Value::Exception(_, _) => false,
        }
    }

    /// 尝试转换为整数
    pub fn as_integer(&self) -> Option<i64> {
        match self {
            Value::Integer(i) => Some(*i),
            _ => None,
        }
    }

    /// 尝试转换为浮点数
    pub fn as_float(&self) -> Option<f64> {
        match self {
            Value::Float(f) => Some(*f),
            Value::Integer(i) => Some(*i as f64),
            _ => None,
        }
    }

    /// 尝试转换为布尔值
    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Value::Bool(b) => Some(*b),
            _ => None,
        }
    }

    /// 尝试转换为字符串
    pub fn as_string(&self) -> Option<&String> {
        match self {
            Value::String(s) => Some(s),
            _ => None,
        }
    }

    /// 尝试转换为数组
    pub fn as_array(&self) -> Option<&Vec<Value>> {
        match self {
            Value::Array(a) => Some(a),
            _ => None,
        }
    }

    /// 尝试转换为可变数组
    pub fn as_array_mut(&mut self) -> Option<&mut Vec<Value>> {
        match self {
            Value::Array(a) => Some(a),
            _ => None,
        }
    }

    /// 尝试转换为元组
    pub fn as_tuple(&self) -> Option<&Vec<Value>> {
        match self {
            Value::Tuple(t) => Some(t),
            _ => None,
        }
    }

    /// 尝试转换为可变元组
    pub fn as_tuple_mut(&mut self) -> Option<&mut Vec<Value>> {
        match self {
            Value::Tuple(t) => Some(t),
            _ => None,
        }
    }

    /// 尝试转换为函数
    pub fn as_function(&self) -> Option<u64> {
        match self {
            Value::Function(hash) => Some(*hash),
            _ => None,
        }
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Value::Integer(i) => write!(f, "{}", i),
            Value::Float(fl) => write!(f, "{}", fl),
            Value::Bool(b) => write!(f, "{}", b),
            Value::String(s) => write!(f, "\"{}\"", s),
            Value::Array(arr) => {
                write!(f, "[")?;
                for (i, v) in arr.iter().enumerate() {
                    if i > 0 {
                        write!(f, ", ")?;
                    }
                    write!(f, "{}", v)?;
                }
                write!(f, "]")
            }
            Value::Object(obj) => {
                write!(f, "{{")?;
                for (i, (k, v)) in obj.iter().enumerate() {
                    if i > 0 {
                        write!(f, ", ")?;
                    }
                    write!(f, "{}: {}", k, v)?;
                }
                write!(f, "}}")
            }
            Value::Tuple(t) => {
                write!(f, "(")?;
                for (i, v) in t.iter().enumerate() {
                    if i > 0 {
                        write!(f, ", ")?;
                    }
                    write!(f, "{}", v)?;
                }
                write!(f, ")")
            }
            Value::Range(start, end, inclusive) => {
                match (start, end) {
                    (Some(s), Some(e)) => {
                        if *inclusive {
                            write!(f, "{}..={}", s, e)
                        } else {
                            write!(f, "{}..{}", s, e)
                        }
                    }
                    (Some(s), None) => write!(f, "{}..", s),
                    (None, Some(e)) => {
                        if *inclusive {
                            write!(f, "..={}", e)
                        } else {
                            write!(f, "..<{}", e)
                        }
                    }
                    (None, None) => write!(f, ".."),
                }
            }
            Value::Function(hash) => write!(f, "fn({:x})", hash),
            Value::Exception(exc_type, msg) => write!(f, "Exception[{}]: {}", exc_type, msg),
            Value::Null => write!(f, "null"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_value_truthy() {
        assert!(Value::Bool(true).is_truthy());
        assert!(!Value::Bool(false).is_truthy());
        assert!(!Value::Null.is_truthy());
        assert!(Value::Integer(1).is_truthy());
        assert!(!Value::Integer(0).is_truthy());
    }

    #[test]
    fn test_value_as_integer() {
        assert_eq!(Value::Integer(42).as_integer(), Some(42));
        assert_eq!(Value::Bool(true).as_integer(), None);
    }

    #[test]
    fn test_value_display() {
        assert_eq!(Value::Integer(42).to_string(), "42");
        assert_eq!(Value::Bool(true).to_string(), "true");
        assert_eq!(Value::String("hello".to_string()).to_string(), "\"hello\"");
        assert_eq!(
            Value::Array(vec![Value::Integer(1), Value::Integer(2)]).to_string(),
            "[1, 2]"
        );
    }
}
