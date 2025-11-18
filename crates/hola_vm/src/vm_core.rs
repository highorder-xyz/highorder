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
    /// 本地变量栈（每个帐框一个）
    local_stack: Vec<HashMap<usize, Value>>,
    /// 需要处理的异常
    exception: Option<Value>,
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
            local_stack: Vec::new(),
            exception: None,
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

            OpCode::BitwiseAnd { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a & b),
                    _ => return Err(VmError::TypeError("Bitwise AND requires two integers".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::BitwiseOr { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a | b),
                    _ => return Err(VmError::TypeError("Bitwise OR requires two integers".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::BitwiseXor { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => Value::Integer(a ^ b),
                    _ => return Err(VmError::TypeError("Bitwise XOR requires two integers".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::BitwiseNot { addr, out } => {
                let val = self.get_value(addr)?;

                let result = match val {
                    Value::Integer(a) => Value::Integer(!a),
                    _ => return Err(VmError::TypeError("Bitwise NOT requires an integer".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::ShiftLeft { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => {
                        if b < 0 || b >= 64 {
                            return Err(VmError::RuntimeError("Shift amount must be between 0 and 63".to_string()));
                        }
                        Value::Integer(a << b)
                    }
                    _ => return Err(VmError::TypeError("Shift left requires two integers".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::ShiftRight { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::Integer(a), Value::Integer(b)) => {
                        if b < 0 || b >= 64 {
                            return Err(VmError::RuntimeError("Shift amount must be between 0 and 63".to_string()));
                        }
                        Value::Integer(a >> b)
                    }
                    _ => return Err(VmError::TypeError("Shift right requires two integers".to_string())),
                };

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

            OpCode::LoadFn { hash, out } => {
                let func = Value::Function(*hash);
                self.set_value(func, out)?;
                Ok(None)
            }

            OpCode::CallFn { function, args_count: _, out } => {
                let _fn_val = self.get_value(function)?;
                // 简化版：暂不实现实际的函数调用机制
                // 这需要更复杂的栈帧管理
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::CallOffset { offset: _, args_count: _, out } => {
                // 简化版：暂不实现
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::ReturnUnit => {
                Ok(Some(Value::Null))
            }

            OpCode::Tuple { addr, len, out } => {
                let mut tuple_vals = Vec::new();
                for i in 0..*len {
                    match addr {
                        Address::Stack(idx) => {
                            if let Some(val) = self.stack.get(idx + i) {
                                tuple_vals.push(val.clone());
                            } else {
                                return Err(VmError::InvalidAddress(format!("Stack index out of bounds: {}", idx + i)));
                            }
                        }
                        Address::Const(idx) => {
                            if let Some(val) = self.constants.get(idx + i) {
                                tuple_vals.push(val.clone());
                            } else {
                                return Err(VmError::InvalidAddress(format!("Constant index out of bounds: {}", idx + i)));
                            }
                        }
                    }
                }
                self.set_value(Value::Tuple(tuple_vals), out)?;
                Ok(None)
            }

            OpCode::Tuple1 { addr, out } => {
                let val = self.get_value(addr)?;
                self.set_value(Value::Tuple(vec![val]), out)?;
                Ok(None)
            }

            OpCode::Tuple2 { addr1, addr2, out } => {
                let val1 = self.get_value(addr1)?;
                let val2 = self.get_value(addr2)?;
                self.set_value(Value::Tuple(vec![val1, val2]), out)?;
                Ok(None)
            }

            OpCode::Tuple3 { addr1, addr2, addr3, out } => {
                let val1 = self.get_value(addr1)?;
                let val2 = self.get_value(addr2)?;
                let val3 = self.get_value(addr3)?;
                self.set_value(Value::Tuple(vec![val1, val2, val3]), out)?;
                Ok(None)
            }

            OpCode::TupleIndexGetAt { addr, index, out } => {
                let tuple_val = self.get_value(addr)?;
                match tuple_val {
                    Value::Tuple(t) => {
                        let val = t.get(*index)
                            .cloned()
                            .ok_or_else(|| VmError::RuntimeError(format!("Tuple index out of bounds: {}", index)))?;
                        self.set_value(val, out)?;
                    }
                    _ => return Err(VmError::TypeError("Cannot index non-tuple types".to_string())),
                }
                Ok(None)
            }

            OpCode::TupleIndexSet { target, index, value } => {
                let mut tuple_val = self.get_value(target)?;
                let new_val = self.get_value(value)?;
                
                match &mut tuple_val {
                    Value::Tuple(t) => {
                        if *index < t.len() {
                            t[*index] = new_val;
                        } else {
                            return Err(VmError::RuntimeError(format!("Tuple index out of bounds: {}", index)));
                        }
                    }
                    _ => return Err(VmError::TypeError("Cannot index non-tuple types".to_string())),
                }
                Ok(None)
            }

            OpCode::Range { start, end, inclusive, out } => {
                let start_val = if let Some(addr) = start {
                    match self.get_value(addr)? {
                        Value::Integer(i) => Some(i),
                        _ => return Err(VmError::TypeError("Range bounds must be integers".to_string())),
                    }
                } else {
                    None
                };
                
                let end_val = if let Some(addr) = end {
                    match self.get_value(addr)? {
                        Value::Integer(i) => Some(i),
                        _ => return Err(VmError::TypeError("Range bounds must be integers".to_string())),
                    }
                } else {
                    None
                };
                
                let range = Value::Range(start_val, end_val, *inclusive);
                self.set_value(range, out)?;
                Ok(None)
            }

            OpCode::Copy { src, out } => {
                let value = self.get_value(src)?;
                self.set_value(value, out)?;
                Ok(None)
            }

            OpCode::Drop { addr } => {
                let _ = self.get_value(addr)?;
                Ok(None)
            }

            OpCode::Swap { addr1, addr2 } => {
                let val1 = self.get_value(addr1)?;
                let val2 = self.get_value(addr2)?;
                match addr1 {
                    Address::Stack(idx1) => {
                        while self.stack.len() <= *idx1 {
                            self.stack.push(Value::Null);
                        }
                        if let Some(slot) = self.stack.values_mut().get_mut(*idx1) {
                            *slot = val2;
                        }
                    }
                    Address::Const(_) => return Err(VmError::RuntimeError("Cannot write to constant".to_string())),
                }
                match addr2 {
                    Address::Stack(idx2) => {
                        while self.stack.len() <= *idx2 {
                            self.stack.push(Value::Null);
                        }
                        if let Some(slot) = self.stack.values_mut().get_mut(*idx2) {
                            *slot = val1;
                        }
                    }
                    Address::Const(_) => return Err(VmError::RuntimeError("Cannot write to constant".to_string())),
                }
                Ok(None)
            }

            OpCode::StrConcat { lhs, rhs, out } => {
                let lhs_val = self.get_value(lhs)?;
                let rhs_val = self.get_value(rhs)?;

                let result = match (lhs_val, rhs_val) {
                    (Value::String(a), Value::String(b)) => Value::String(format!("{}{}", a, b)),
                    _ => return Err(VmError::TypeError("String concatenation requires two strings".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::StrLen { addr, out } => {
                let val = self.get_value(addr)?;
                match val {
                    Value::String(s) => {
                        self.set_value(Value::Integer(s.len() as i64), out)?;
                    }
                    _ => return Err(VmError::TypeError("StrLen requires a string".to_string())),
                }
                Ok(None)
            }

            OpCode::StrIndexGet { addr, index, out } => {
                let str_val = self.get_value(addr)?;
                let idx_val = self.get_value(index)?;

                match (str_val, idx_val) {
                    (Value::String(s), Value::Integer(idx)) => {
                        let idx = idx as usize;
                        if idx < s.len() {
                            let c = s.chars().nth(idx)
                                .ok_or_else(|| VmError::RuntimeError(format!("String index out of bounds: {}", idx)))?
                                .to_string();
                            self.set_value(Value::String(c), out)?;
                        } else {
                            return Err(VmError::RuntimeError(format!("String index out of bounds: {}", idx)));
                        }
                    }
                    _ => return Err(VmError::TypeError("StrIndexGet requires string and integer".to_string())),
                }
                Ok(None)
            }

            OpCode::StrSlice { addr, start, end, out } => {
                let str_val = self.get_value(addr)?;
                let start_val = self.get_value(start)?;
                let end_val = self.get_value(end)?;

                match (str_val, start_val, end_val) {
                    (Value::String(s), Value::Integer(st), Value::Integer(e)) => {
                        let st = (st as usize).min(s.len());
                        let e = (e as usize).min(s.len());
                        if st <= e {
                            let sliced = s.chars().skip(st).take(e - st).collect::<String>();
                            self.set_value(Value::String(sliced), out)?;
                        } else {
                            return Err(VmError::RuntimeError("Invalid slice range".to_string()));
                        }
                    }
                    _ => return Err(VmError::TypeError("StrSlice requires string and two integers".to_string())),
                }
                Ok(None)
            }

            OpCode::StrFind { haystack, needle, out } => {
                let haystack_val = self.get_value(haystack)?;
                let needle_val = self.get_value(needle)?;

                match (haystack_val, needle_val) {
                    (Value::String(h), Value::String(n)) => {
                        if let Some(pos) = h.find(&n) {
                            self.set_value(Value::Integer(pos as i64), out)?;
                        } else {
                            self.set_value(Value::Integer(-1), out)?;
                        }
                    }
                    _ => return Err(VmError::TypeError("StrFind requires two strings".to_string())),
                }
                Ok(None)
            }

            OpCode::StrReplace { text, from, to, out } => {
                let text_val = self.get_value(text)?;
                let from_val = self.get_value(from)?;
                let to_val = self.get_value(to)?;

                match (text_val, from_val, to_val) {
                    (Value::String(t), Value::String(f), Value::String(r)) => {
                        let replaced = t.replace(&f, &r);
                        self.set_value(Value::String(replaced), out)?;
                    }
                    _ => return Err(VmError::TypeError("StrReplace requires three strings".to_string())),
                }
                Ok(None)
            }

            OpCode::TypeCheck { addr, expected_type, out } => {
                let val = self.get_value(addr)?;
                let matches = match (expected_type.as_str(), &val) {
                    ("integer", Value::Integer(_)) => true,
                    ("float", Value::Float(_)) => true,
                    ("bool", Value::Bool(_)) => true,
                    ("string", Value::String(_)) => true,
                    ("array", Value::Array(_)) => true,
                    ("object", Value::Object(_)) => true,
                    ("tuple", Value::Tuple(_)) => true,
                    ("range", Value::Range(_, _, _)) => true,
                    ("function", Value::Function(_)) => true,
                    ("null", Value::Null) => true,
                    _ => false,
                };
                self.set_value(Value::Bool(matches), out)?;
                Ok(None)
            }

            OpCode::DestructTuple { addr, pattern_size, out } => {
                let val = self.get_value(addr)?;
                match val {
                    Value::Tuple(t) => {
                        if t.len() == *pattern_size {
                            self.set_value(Value::Tuple(t), out)?;
                        } else {
                            return Err(VmError::RuntimeError(
                                format!("Tuple size mismatch: expected {}, got {}", pattern_size, t.len())
                            ));
                        }
                    }
                    _ => return Err(VmError::TypeError("DestructTuple requires a tuple".to_string())),
                }
                Ok(None)
            }

            OpCode::Match { value, patterns, offsets, default_offset } => {
                let _val = self.get_value(value)?;
                // 简化版本：模式匹配的完整实现需要复杂的模式识别逻辑
                // 这里仅演示基础结构
                if patterns.is_empty() {
                    if let Some(offset) = default_offset {
                        self.ip = *offset;
                    }
                } else if let Some(&offset) = offsets.first() {
                    self.ip = offset;
                }
                Ok(None)
            }

            OpCode::MatchTest { value, pattern, out } => {
                let val = self.get_value(value)?;
                // 简化的模式测试
                let matches = match (pattern.as_str(), &val) {
                    ("null", Value::Null) => true,
                    ("integer", Value::Integer(_)) => true,
                    ("string", Value::String(_)) => true,
                    ("_", _) => true,  // 通配符匹配
                    _ => false,
                };
                self.set_value(Value::Bool(matches), out)?;
                Ok(None)
            }

            OpCode::PushFrame { params_count } => {
                // 创建新的帐框用于存储本地变量
                let mut frame = HashMap::new();
                // 保留参数数量信息
                frame.insert(usize::MAX, Value::Integer(*params_count as i64));
                self.local_stack.push(frame);
                Ok(None)
            }

            OpCode::PopFrame => {
                // 弹出帐框
                self.local_stack.pop();
                Ok(None)
            }

            OpCode::SetLocal { index, value } => {
                let val = self.get_value(value)?;
                if let Some(frame) = self.local_stack.last_mut() {
                    frame.insert(*index, val);
                    Ok(None)
                } else {
                    Err(VmError::RuntimeError("No active frame for local variable".to_string()))
                }
            }

            OpCode::GetLocal { index, out } => {
                if let Some(frame) = self.local_stack.last() {
                    if let Some(val) = frame.get(index) {
                        self.set_value(val.clone(), out)?;
                        Ok(None)
                    } else {
                        Err(VmError::RuntimeError(format!("Local variable {} not found", index)))
                    }
                } else {
                    Err(VmError::RuntimeError("No active frame for local variable".to_string()))
                }
            }

            OpCode::SetGlobal { name, value } => {
                let val = self.get_value(value)?;
                self.globals.insert(name.clone(), val);
                Ok(None)
            }

            OpCode::GetGlobal { name, out } => {
                if let Some(val) = self.globals.get(name) {
                    self.set_value(val.clone(), out)?;
                    Ok(None)
                } else {
                    Err(VmError::RuntimeError(format!("Global variable {} not found", name)))
                }
            }

            OpCode::FuncCall { func_addr, args_count, out } => {
                // 正式函数调用（收鱬一号全部参数并推送帐框）
                let _func = self.get_value(func_addr)?;
                
                // 推送帐框
                let mut frame = HashMap::new();
                frame.insert(usize::MAX, Value::Integer(*args_count as i64));
                self.local_stack.push(frame);
                
                // 简化版本：暂不干正于跳中转
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::FuncReturn { value } => {
                // 从帐框返回并恢复前一个执行位置
                self.local_stack.pop();
                
                let ret_val = if let Some(addr) = value {
                    self.get_value(addr)?
                } else {
                    Value::Null
                };
                
                Ok(Some(ret_val))
            }

            OpCode::Throw { exception_type, message } => {
                let msg = self.get_value(message)?;
                let msg_str = match msg {
                    Value::String(s) => s,
                    _ => msg.to_string(),
                };
                
                let exception = Value::Exception(exception_type.clone(), msg_str);
                self.exception = Some(exception.clone());
                Err(VmError::RuntimeError(format!("Exception: {} ", exception)))
            }

            OpCode::TryCatch { try_offset: _, catch_offset: _, finally_offset: _ } => {
                // 这是一个标记器，具体的try-catch处理需要由程序下一级处理
                Ok(None)
            }

            OpCode::GuardException { guarded_op: _, catch_offset: _ } => {
                // 此个操作应由程序下一级处理
                Ok(None)
            }

            OpCode::CatchException { exception_out } => {
                // 稍微简化版本：输出异常值
                if let Some(exc) = self.exception.take() {
                    self.set_value(exc, exception_out)?;
                    Ok(None)
                } else {
                    self.set_value(Value::Null, exception_out)?;
                    Ok(None)
                }
            }

            OpCode::ClearException => {
                self.exception = None;
                Ok(None)
            }

            OpCode::ObjectCreate { out } => {
                let obj = Value::Object(HashMap::new());
                self.set_value(obj, out)?;
                Ok(None)
            }

            OpCode::ObjectSet { object, key, value } => {
                let key_val = self.get_value(key)?;
                let val = self.get_value(value)?;
                let obj_val = self.get_value(object)?;

                match (obj_val, key_val) {
                    (Value::Object(mut obj), Value::String(k)) => {
                        obj.insert(k, val);
                        // 更新原始对象
                        match object {
                            Address::Stack(idx) => {
                                if let Some(slot) = self.stack.values_mut().get_mut(*idx) {
                                    *slot = Value::Object(obj);
                                } else {
                                    return Err(VmError::InvalidAddress(format!("Stack index out of bounds: {}", idx)));
                                }
                            }
                            Address::Const(_) => {
                                return Err(VmError::RuntimeError("Cannot modify constant objects".to_string()));
                            }
                        }
                        Ok(None)
                    }
                    (Value::Object(_), _) => {
                        Err(VmError::TypeError("Object key must be a string".to_string()))
                    }
                    _ => Err(VmError::TypeError("Cannot set property on non-object".to_string())),
                }
            }

            OpCode::ObjectGet { object, key, out } => {
                let key_val = self.get_value(key)?;
                let obj_val = self.get_value(object)?;

                match (obj_val, key_val) {
                    (Value::Object(obj), Value::String(k)) => {
                        let val = obj.get(&k)
                            .cloned()
                            .unwrap_or(Value::Null);
                        self.set_value(val, out)?;
                        Ok(None)
                    }
                    (Value::Object(_), _) => {
                        Err(VmError::TypeError("Object key must be a string".to_string()))
                    }
                    _ => Err(VmError::TypeError("Cannot get property from non-object".to_string())),
                }
            }

            OpCode::FloatPow { base, exponent, out } => {
                let base_val = self.get_value(base)?;
                let exp_val = self.get_value(exponent)?;

                let result = match (base_val, exp_val) {
                    (Value::Float(b), Value::Float(e)) => Value::Float(b.powf(e)),
                    (Value::Integer(b), Value::Integer(e)) => {
                        if e < 0 {
                            Value::Float((b as f64).powf(e as f64))
                        } else {
                            Value::Integer(b.pow(e as u32))
                        }
                    }
                    (Value::Float(b), Value::Integer(e)) => Value::Float(b.powf(e as f64)),
                    (Value::Integer(b), Value::Float(e)) => Value::Float((b as f64).powf(e)),
                    _ => return Err(VmError::TypeError("Float power requires numeric types".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::FloatSqrt { addr, out } => {
                let val = self.get_value(addr)?;

                let result = match val {
                    Value::Float(f) => {
                        if f < 0.0 {
                            return Err(VmError::RuntimeError("Cannot take square root of negative number".to_string()));
                        }
                        Value::Float(f.sqrt())
                    }
                    Value::Integer(i) => {
                        if i < 0 {
                            return Err(VmError::RuntimeError("Cannot take square root of negative number".to_string()));
                        }
                        Value::Float((i as f64).sqrt())
                    }
                    _ => return Err(VmError::TypeError("Float sqrt requires a numeric value".to_string())),
                };

                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Clone { addr, out } => {
                let val = self.get_value(addr)?;
                // 深复制支持的类型
                let cloned = match val {
                    Value::Array(arr) => Value::Array(arr.clone()),
                    Value::Object(obj) => Value::Object(obj.clone()),
                    Value::Tuple(tuple) => Value::Tuple(tuple.clone()),
                    // 基本类型直接复制
                    other => other,
                };
                self.set_value(cloned, out)?;
                Ok(None)
            }

            OpCode::Typeof { addr, out } => {
                let val = self.get_value(addr)?;
                let type_name = match val {
                    Value::Integer(_) => "integer",
                    Value::Float(_) => "float",
                    Value::Bool(_) => "bool",
                    Value::String(_) => "string",
                    Value::Array(_) => "array",
                    Value::Object(_) => "object",
                    Value::Tuple(_) => "tuple",
                    Value::Range(_, _, _) => "range",
                    Value::Function(_) => "function",
                    Value::Exception(_, _) => "exception",
                    Value::Null => "null",
                };
                self.set_value(Value::String(type_name.to_string()), out)?;
                Ok(None)
            }

            // 第 1 阶段：核心操作码
            OpCode::Neg { addr, out } => {
                let val = self.get_value(addr)?;
                let result = match val {
                    Value::Integer(i) => Value::Integer(-i),
                    Value::Float(f) => Value::Float(-f),
                    _ => return Err(VmError::TypeError("Negation requires a numeric value".to_string())),
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::As { value, expected_type, out } => {
                let val = self.get_value(value)?;
                // 简化版本：简单的类型转换
                let result = match (expected_type.as_str(), val) {
                    ("integer", Value::Float(f)) => Value::Integer(f as i64),
                    ("float", Value::Integer(i)) => Value::Float(i as f64),
                    ("string", v) => Value::String(v.to_string()),
                    ("bool", Value::Integer(i)) => Value::Bool(i != 0),
                    (_, v) => v,
                };
                self.set_value(result, out)?;
                Ok(None)
            }

            OpCode::Is { value, expected_type, out } => {
                let val = self.get_value(value)?;
                let is_type = match (expected_type.as_str(), &val) {
                    ("integer", Value::Integer(_)) => true,
                    ("float", Value::Float(_)) => true,
                    ("string", Value::String(_)) => true,
                    ("bool", Value::Bool(_)) => true,
                    ("array", Value::Array(_)) => true,
                    ("object", Value::Object(_)) => true,
                    ("tuple", Value::Tuple(_)) => true,
                    ("null", Value::Null) => true,
                    _ => false,
                };
                self.set_value(Value::Bool(is_type), out)?;
                Ok(None)
            }

            OpCode::IsNot { value, expected_type, out } => {
                let val = self.get_value(value)?;
                let is_type = match (expected_type.as_str(), &val) {
                    ("integer", Value::Integer(_)) => true,
                    ("float", Value::Float(_)) => true,
                    ("string", Value::String(_)) => true,
                    ("bool", Value::Bool(_)) => true,
                    ("array", Value::Array(_)) => true,
                    ("object", Value::Object(_)) => true,
                    ("tuple", Value::Tuple(_)) => true,
                    ("null", Value::Null) => true,
                    _ => false,
                };
                self.set_value(Value::Bool(!is_type), out)?;
                Ok(None)
            }

            OpCode::Try { addr, out } => {
                let val = self.get_value(addr)?;
                // 简化版本：检查是否是异常，如果是则傟讯
                if let Value::Exception(exc_type, msg) = &val {
                    return Err(VmError::RuntimeError(format!("Exception: {} - {}", exc_type, msg)));
                }
                self.set_value(val, out)?;
                Ok(None)
            }

            // 第 2 阶段：OOP 支持
            OpCode::CallAssociated { instance, method_name, args_count, out } => {
                let _inst = self.get_value(instance)?;
                // 简化版本：就上下文返回 null
                let mut frame = HashMap::new();
                frame.insert(usize::MAX, Value::Integer(*args_count as i64));
                self.local_stack.push(frame);
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::LoadInstanceFn { instance, method_name, out } => {
                let _inst = self.get_value(instance)?;
                // 简化版本：作为函数引用返回
                let hash = method_name.len() as u64;
                self.set_value(Value::Function(hash), out)?;
                Ok(None)
            }

            OpCode::Struct { addr: _, struct_name, field_count: _, out } => {
                // 简化版本：创建空对象
                let obj = Value::Object(HashMap::new());
                self.set_value(obj, out)?;
                Ok(None)
            }

            // 第 3 阶段：迭代和高级功能
            OpCode::IterNext { iterator_addr, jump_offset, out } => {
                let _iter = self.get_value(iterator_addr)?;
                // 简化版本：直接跳转
                self.ip = *jump_offset;
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::Closure { func_hash, capture_addr, capture_count, out } => {
                let _captures = self.get_value(capture_addr)?;
                // 简化版本：返回函数引用
                self.set_value(Value::Function(*func_hash), out)?;
                Ok(None)
            }

            OpCode::Environment { tuple_addr, expected_count, out } => {
                let tuple = self.get_value(tuple_addr)?;
                match tuple {
                    Value::Tuple(items) => {
                        if items.len() != *expected_count {
                            return Err(VmError::RuntimeError(format!("Expected {} items, got {}", expected_count, items.len())));
                        }
                        // 简化版本：直接返回元组
                        self.set_value(Value::Tuple(items), out)?;
                        Ok(None)
                    }
                    _ => Err(VmError::TypeError("Environment expects a tuple".to_string())),
                }
            }

            OpCode::Format { value_addr, format_spec, out } => {
                let val = self.get_value(value_addr)?;
                // 简化版本：直接格式化为字符串
                let formatted = format!("{}", val);
                self.set_value(Value::String(formatted), out)?;
                Ok(None)
            }

            // 第 4 阶段：异步支持
            OpCode::Await { future_addr, out } => {
                let _future = self.get_value(future_addr)?;
                // 简化版本：直接返回 null
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::Yield { value_addr, out } => {
                let val = self.get_value(value_addr)?;
                // 简化版本：简单地返回 yield 值
                self.set_value(val, out)?;
                Ok(None)
            }

            OpCode::YieldUnit { out } => {
                // 简化版本：Yield unit
                self.set_value(Value::Null, out)?;
                Ok(None)
            }

            OpCode::Select { futures_addr, futures_count, value_out } => {
                let _futures = self.get_value(futures_addr)?;
                let _count = futures_count;
                // 简化版本：直接返回 null
                self.set_value(Value::Null, value_out)?;
                Ok(None)
            }

            OpCode::Nop => Ok(None),

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
