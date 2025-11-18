//! HOLA VM 栈实现

use crate::value::Value;

/// 虚拟机栈
#[derive(Debug, Clone)]
pub struct Stack {
    /// 栈的值
    values: Vec<Value>,
}

impl Stack {
    /// 创建一个新的空栈
    pub fn new() -> Self {
        Self {
            values: Vec::new(),
        }
    }

    /// 创建一个初始化大小为 capacity 的栈
    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            values: Vec::with_capacity(capacity),
        }
    }

    /// 推入一个值到栈
    pub fn push(&mut self, value: Value) {
        self.values.push(value);
    }

    /// 弹出一个值从栈
    pub fn pop(&mut self) -> Option<Value> {
        self.values.pop()
    }

    /// 弹出 n 个值从栈
    pub fn pop_n(&mut self, n: usize) -> Vec<Value> {
        if n == 0 {
            return Vec::new();
        }
        let split_at = self.values.len().saturating_sub(n);
        self.values.drain(split_at..).collect()
    }

    /// 获取栈顶的值但不弹出
    pub fn peek(&self) -> Option<&Value> {
        self.values.last()
    }

    /// 获取栈顶的值的可变引用
    pub fn peek_mut(&mut self) -> Option<&mut Value> {
        self.values.last_mut()
    }

    /// 获取指定索引的值
    pub fn get(&self, index: usize) -> Option<&Value> {
        self.values.get(index)
    }

    /// 获取指定索引的值的可变引用
    pub fn get_mut(&mut self, index: usize) -> Option<&mut Value> {
        self.values.get_mut(index)
    }

    /// 获取栈的长度
    pub fn len(&self) -> usize {
        self.values.len()
    }

    /// 检查栈是否为空
    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }

    /// 清空栈
    pub fn clear(&mut self) {
        self.values.clear();
    }

    /// 分配 n 个栈空间（用 Null 值填充）
    pub fn allocate(&mut self, size: usize) {
        self.values.resize(self.values.len() + size, Value::Null);
    }

    /// 获取所有值的引用
    pub fn values(&self) -> &[Value] {
        &self.values
    }

    /// 获取所有值的可变引用
    pub fn values_mut(&mut self) -> &mut [Value] {
        &mut self.values
    }
}

impl Default for Stack {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_push_and_pop() {
        let mut stack = Stack::new();
        stack.push(Value::Integer(42));
        stack.push(Value::String("hello".to_string()));

        assert_eq!(stack.pop(), Some(Value::String("hello".to_string())));
        assert_eq!(stack.pop(), Some(Value::Integer(42)));
        assert_eq!(stack.pop(), None);
    }

    #[test]
    fn test_peek() {
        let mut stack = Stack::new();
        stack.push(Value::Integer(42));

        assert_eq!(stack.peek(), Some(&Value::Integer(42)));
        assert_eq!(stack.len(), 1);
    }

    #[test]
    fn test_allocate() {
        let mut stack = Stack::new();
        stack.allocate(5);
        assert_eq!(stack.len(), 5);
        
        for i in 0..5 {
            assert_eq!(stack.get(i), Some(&Value::Null));
        }
    }

    #[test]
    fn test_pop_n() {
        let mut stack = Stack::new();
        stack.push(Value::Integer(1));
        stack.push(Value::Integer(2));
        stack.push(Value::Integer(3));

        let popped = stack.pop_n(2);
        assert_eq!(popped.len(), 2);
        assert_eq!(stack.len(), 1);
    }
}
