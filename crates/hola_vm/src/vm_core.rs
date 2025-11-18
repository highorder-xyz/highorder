//! HOLA 虚拟机核心实现

use std::collections::HashMap;
use crate::opcode::{Address, OpCode, Output};
use crate::stack::Stack;
use crate::value::Value;

/// VM 执行错误
#[derive(Debug, Clone)]
pub enum VmError {
    /// 栈为空
    StackEmpty,
    /// 无效的地址
    InvalidAddress(String),
    /// 类型错误
    TypeError(String),
    /// 运行时错误
    RuntimeError(String),
    /// 指令指针越界
    InstructionPointerOutOfBounds,
    /// 除以零
    DivisionByZero,
}

impl std::fmt::Display for VmError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            VmError::StackEmpty => write!(f, "Stack is empty"),
            VmError::InvalidAddress(msg) => write!(f, "Invalid address: {}", msg),
            VmError::TypeError(msg) => write!(f, "Type error: {}", msg),
            VmError::RuntimeError(msg) => write!(f, "Runtime error: {}", msg),
            VmError::InstructionPointerOutOfBounds => write!(f, "Instruction pointer out of bounds"),
            VmError::DivisionByZero => write!(f, "Division by zero"),
        }
    }
}

impl std::error::Error for VmError {}

/// 虚拟机程序
#[derive(Debug, Clone)]
pub struct Program {
    /// 常数池
    pub constants: Vec<Value>,
    /// 指令序列
    pub instructions: Vec<OpCode>,
}

impl Program {
    /// 创建一个新的程序
    pub fn new() -> Self {
        Self {
            constants: Vec::new(),
            instructions: Vec::new(),
        }
    }

    /// 添加一个常数到常数池
    pub fn add_constant(&mut self, value: Value) -> usize {
        let index = self.constants.len();
        self.constants.push(value);
        index
    }

    /// 添加一个指令
    pub fn add_instruction(&mut self, opcode: OpCode) {
        self.instructions.push(opcode);
    }

    /// 获取常数
    pub fn get_constant(&self, index: usize) -> Option<&Value> {
        self.constants.get(index)
    }

    /// 获取指令
    pub fn get_instruction(&self, index: usize) -> Option<&OpCode> {
        self.instructions.get(index)
    }
}

impl Default for Program {
    fn default() -> Self {
        Self::new()
    }
}

/// 虚拟机执行器
pub struct Vm {
    /// 当前执行的程序
    program: Program,
    /// 栈
    stack: Stack,
    /// 指令指针
    ip: usize,
    /// 常数池（快速访问）
    constants: Vec<Value>,
    /// 全局变量
    #[allow(dead_code)]
    globals: HashMap<String, Value>,
}

impl Vm {
    /// 创建一个新的虚拟机
    pub fn new(program: Program) -> Self {
        let constants = program.constants.clone();
        Self {
            program,
            stack: Stack::new(),
            ip: 0,
            constants,
            globals: HashMap::new(),
        }
    }

    /// 获取值（从地址）
    fn get_value(&self, addr: &Address) -> Result<Value, VmError> {
        match addr {
            Address::Stack(idx) => {
                self.stack.get(*idx)
                    .cloned()
                    .ok_or_else(|| VmError::InvalidAddress(format!("Stack index out of bounds: {}", idx)))
            }
            Address::Const(idx) => {
                self.constants.get(*idx)
                    .cloned()
                    .ok_or_else(|| VmError::InvalidAddress(format!("Constant index out of bounds: {}", idx)))
            }
        }
    }

    /// 设置值（到地址）
    fn set_value(&mut self, value: Value, output: &Output) -> Result<(), VmError> {
        match output {
            Output::Stack(idx) => {
                // 确保栈足够大
                while self.stack.len() <= *idx {
                    self.stack.push(Value::Null);
                }
                if let Some(slot) = self.stack.values_mut().get_mut(*idx) {
                    *slot = value;
                    Ok(())
                } else {
                    Err(VmError::InvalidAddress(format!("Stack index out of bounds: {}", idx)))
                }
            }
            Output::Discard => Ok(()),
        }
    }

    /// 执行单个指令
    fn execute_instruction(&mut self, opcode: &OpCode) -> Result<Option<Value>, VmError> {
        match opcode {
            OpCode::Add { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a + b),
                    (Value::Float(a), Value::Float(b)) => Value::Float(a + b),
                    (Value::Integer(a), Value::Float(b)) => Value::Float(a as f64 + b),
                    (Value::Float(a), Value::Integer(b)) => Value::Float(a + b as f64),
                    _ => return Err(VmError::TypeError("Cannot add non-numeric types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Sub { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a - b),
                    (Value::Float(a), Value::Float(b)) => Value::Float(a - b),
                    (Value::Integer(a), Value::Float(b)) => Value::Float(a as f64 - b),
                    (Value::Float(a), Value::Integer(b)) => Value::Float(a - b as f64),
                    _ => return Err(VmError::TypeError("Cannot subtract non-numeric types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Mul { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a * b),
                    (Value::Float(a), Value::Float(b)) => Value::Float(a * b),
                    (Value::Integer(a), Value::Float(b)) => Value::Float(a as f64 * b),
                    (Value::Float(a), Value::Integer(b)) => Value::Float(a * b as f64),
                    _ => return Err(VmError::TypeError("Cannot multiply non-numeric types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Div { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => {
                        if b == 0 {
                            return Err(VmError::DivisionByZero);
                        }
                        Value::Integer(a / b)
                    }
                    (Value::Float(a), Value::Float(b)) => {
                        if b == 0.0 {
                            return Err(VmError::DivisionByZero);
                        }
                        Value::Float(a / b)
                    }
                    (Value::Integer(a), Value::Float(b)) => {
                        if b == 0.0 {
                            return Err(VmError::DivisionByZero);
                        }
                        Value::Float(a as f64 / b)
                    }
                    (Value::Float(a), Value::Integer(b)) => {
                        if b == 0 {
                            return Err(VmError::DivisionByZero);
                        }
                        Value::Float(a / b as f64)
                    }
                    _ => return Err(VmError::TypeError("Cannot divide non-numeric types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Eq { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                let result = Value::Bool(lhs_val == rhs_val);
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Ne { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                let result = Value::Bool(lhs_val != rhs_val);
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Lt { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                
                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Bool(a < b),
                    (Value::Float(a), Value::Float(b)) => Value::Bool(a < b),
                    (Value::Integer(a), Value::Float(b)) => Value::Bool((a as f64) < b),
                    (Value::Float(a), Value::Integer(b)) => Value::Bool(a < (b as f64)),
                    _ => return Err(VmError::TypeError("Cannot compare non-numeric types".to_string())),
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Gt { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                
                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Bool(a > b),
                    (Value::Float(a), Value::Float(b)) => Value::Bool(a > b),
                    (Value::Integer(a), Value::Float(b)) => Value::Bool((a as f64) > b),
                    (Value::Float(a), Value::Integer(b)) => Value::Bool(a > (b as f64)),
                    _ => return Err(VmError::TypeError("Cannot compare non-numeric types".to_string())),
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::And { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                let result = Value::Bool(lhs_val.is_truthy() && rhs_val.is_truthy());
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Or { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                let result = Value::Bool(lhs_val.is_truthy() || rhs_val.is_truthy());
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Not { addr, out } => {
                let val = self.get_value(addr)?;
                let result = Value::Bool(!val.is_truthy());
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::LoadConst { index, out } => {
                let value = self.constants.get(*index)
                    .cloned()
                    .ok_or_else(|| VmError::InvalidAddress(format!("Constant index out of bounds: {}", index)))?;
                self.set_value(value, out)?;
                Ok(None)
            }

            OpCode::Move { src, dst } => {
                let value = self.get_value(src)?;
                self.set_value(value, dst)?;
                Ok(None)
            }

            OpCode::Jump { offset } => {
                self.ip = *offset;
                Ok(None)
            }

            OpCode::JumpIfTrue { cond, offset } => {
                let val = self.get_value(cond)?;
                if val.is_truthy() {
                    self.ip = *offset;
                }
                Ok(None)
            }

            OpCode::JumpIfFalse { cond, offset } => {
                let val = self.get_value(cond)?;
                if !val.is_truthy() {
                    self.ip = *offset;
                }
                Ok(None)
            }

            OpCode::Return { value } => {
                match value {
                    Some(addr) => Ok(Some(self.get_value(addr)?)),
                    None => Ok(Some(Value::Null)),
                }
            }

            OpCode::MakeArray { len, out } => {
                let arr = vec![Value::Null; *len];
                self.set_value(Value::Array(arr), out)?;
                Ok(None)
            }

            OpCode::IndexGet { array, index, out } => {
                let arr_val = self.get_value(array)?;
                let idx_val = self.get_value(index)?;

                match (arr_val, idx_val) {
                    (Value::Array(arr), Value::Integer(idx)) => {
                        let idx = idx as usize;
                        let val = arr.get(idx)
                            .cloned()
                            .ok_or_else(|| VmError::RuntimeError(format!("Array index out of bounds: {}", idx)))?;
                        self.set_value(val, out)?;
                    }
                    _ => return Err(VmError::TypeError("Cannot index non-array types".to_string())),
                }
                Ok(None)
            }

            OpCode::Allocate { size } => {
                self.stack.allocate(*size);
                Ok(None)
            }

            OpCode::Pop { count } => {
                for _ in 0..*count {
                    self.stack.pop();
                }
                Ok(None)
            }

            OpCode::Nop => Ok(None),

            OpCode::Halt => Ok(Some(Value::Null)),

            OpCode::Mod { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => {
                        if b == 0 {
                            return Err(VmError::DivisionByZero);
                        }
                        Value::Integer(a % b)
                    }
                    _ => return Err(VmError::TypeError("Cannot modulo non-integer types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Le { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                
                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Bool(a <= b),
                    (Value::Float(a), Value::Float(b)) => Value::Bool(a <= b),
                    (Value::Integer(a), Value::Float(b)) => Value::Bool((a as f64) <= b),
                    (Value::Float(a), Value::Integer(b)) => Value::Bool(a <= (b as f64)),
                    _ => return Err(VmError::TypeError("Cannot compare non-numeric types".to_string())),
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Ge { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;
                
                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Bool(a >= b),
                    (Value::Float(a), Value::Float(b)) => Value::Bool(a >= b),
                    (Value::Integer(a), Value::Float(b)) => Value::Bool((a as f64) >= b),
                    (Value::Float(a), Value::Integer(b)) => Value::Bool(a >= (b as f64)),
                    _ => return Err(VmError::TypeError("Cannot compare non-numeric types".to_string())),
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Call { .. } | OpCode::IndexSet { .. } => {
                Err(VmError::RuntimeError("Unimplemented instruction".to_string()))
            }
        }
    }

    /// 执行程序
    pub fn execute(&mut self) -> Result<Option<Value>, VmError> {
        loop {
            if self.ip >= self.program.instructions.len() {
                break;
            }

            let opcode = self.program.instructions[self.ip].clone();
            self.ip += 1;

            if let Some(return_val) = self.execute_instruction(&opcode)? {
                if matches!(opcode, OpCode::Halt) {
                    return Ok(Some(return_val));
                }
                return Ok(Some(return_val));
            }
        }

        Ok(None)
    }

    /// 获取栈的引用
    pub fn stack(&self) -> &Stack {
        &self.stack
    }

    /// 获取栈的可变引用
    pub fn stack_mut(&mut self) -> &mut Stack {
        &mut self.stack
    }

    /// 获取程序的引用
    pub fn program(&self) -> &Program {
        &self.program
    }

    /// 获取全局变量
    pub fn get_global(&self, name: &str) -> Option<&Value> {
        self.globals.get(name)
    }

    /// 设置全局变量
    pub fn set_global(&mut self, name: String, value: Value) {
        self.globals.insert(name, value);
    }

    /// 重置虚拟机状态
    pub fn reset(&mut self) {
        self.ip = 0;
        self.stack.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_addition() {
        let mut program = Program::new();
        program.add_constant(Value::Integer(2));
        program.add_constant(Value::Integer(3));
        program.add_instruction(OpCode::Add {
            lhs: Address::Const(0),
            rhs: Address::Const(1),
            out: Output::Stack(0),
        });

        let mut vm = Vm::new(program);
        vm.execute().unwrap();

        assert_eq!(vm.stack.get(0), Some(&Value::Integer(5)));
    }

    #[test]
    fn test_comparison() {
        let mut program = Program::new();
        program.add_constant(Value::Integer(5));
        program.add_constant(Value::Integer(3));
        program.add_instruction(OpCode::Lt {
            lhs: Address::Const(1),
            rhs: Address::Const(0),
            out: Output::Stack(0),
        });

        let mut vm = Vm::new(program);
        vm.execute().unwrap();

        assert_eq!(vm.stack.get(0), Some(&Value::Bool(true)));
    }

    #[test]
    fn test_logical_and() {
        let mut program = Program::new();
        program.add_constant(Value::Bool(true));
        program.add_constant(Value::Bool(false));
        program.add_instruction(OpCode::And {
            lhs: Address::Const(0),
            rhs: Address::Const(1),
            out: Output::Stack(0),
        });

        let mut vm = Vm::new(program);
        vm.execute().unwrap();

        assert_eq!(vm.stack.get(0), Some(&Value::Bool(false)));
    }
}
