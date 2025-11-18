//! HOLA VM 操作码定义
//!
//! 操作码是虚拟机执行的基本指令单位。
//! 设计灵感来自 Rune VM，采用栈式架构。

use std::fmt;

/// 操作码地址，表示栈上或寄存器中的位置
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Address {
    /// 栈相对地址（相对于当前栈帧）
    Stack(usize),
    /// 常数池中的索引
    Const(usize),
}

impl fmt::Display for Address {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Address::Stack(idx) => write!(f, "stack[{}]", idx),
            Address::Const(idx) => write!(f, "const[{}]", idx),
        }
    }
}

/// 输出位置，指定指令结果的存储位置
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Output {
    /// 将结果存储到栈上
    Stack(usize),
    /// 丢弃结果
    Discard,
}

impl fmt::Display for Output {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Output::Stack(idx) => write!(f, "stack[{}]", idx),
            Output::Discard => write!(f, "discard"),
        }
    }
}

/// HOLA 虚拟机的操作码
#[derive(Debug, Clone, PartialEq)]
pub enum OpCode {
    // 算术运算
    /// 加法: a + b
    Add {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 减法: a - b
    Sub {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 乘法: a * b
    Mul {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 除法: a / b
    Div {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 模运算: a % b
    Mod {
        lhs: Address,
        rhs: Address,
        out: Output,
    },

    // 比较运算
    /// 相等比较: a == b
    Eq {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 不相等比较: a != b
    Ne {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 小于比较: a < b
    Lt {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 小于等于比较: a <= b
    Le {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 大于比较: a > b
    Gt {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 大于等于比较: a >= b
    Ge {
        lhs: Address,
        rhs: Address,
        out: Output,
    },

    // 逻辑运算
    /// 逻辑与: a && b
    And {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 逻辑或: a || b
    Or {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 逻辑非: !a
    Not {
        addr: Address,
        out: Output,
    },

    // 数据移动
    /// 将常数值加载到栈中
    LoadConst {
        index: usize,
        out: Output,
    },
    /// 将值从一个位置复制到另一个位置
    Move {
        src: Address,
        dst: Output,
    },

    // 控制流
    /// 无条件跳转
    Jump {
        offset: usize,
    },
    /// 条件跳转（如果条件为真则跳转）
    JumpIfTrue {
        cond: Address,
        offset: usize,
    },
    /// 条件跳转（如果条件为假则跳转）
    JumpIfFalse {
        cond: Address,
        offset: usize,
    },

    // 函数调用
    /// 调用函数
    Call {
        func_addr: Address,
        args_count: usize,
        out: Output,
    },
    /// 返回值
    Return {
        value: Option<Address>,
    },

    // 数组/集合操作
    /// 创建数组
    MakeArray {
        len: usize,
        out: Output,
    },
    /// 数组索引访问
    IndexGet {
        array: Address,
        index: Address,
        out: Output,
    },
    /// 数组索引设置
    IndexSet {
        array: Address,
        index: Address,
        value: Address,
    },

    // 栈管理
    /// 分配栈空间
    Allocate {
        size: usize,
    },
    /// 释放栈空间
    Pop {
        count: usize,
    },

    // 其他
    /// 无操作
    Nop,
    /// 停止执行
    Halt,
}

impl fmt::Display for OpCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            OpCode::Add { lhs, rhs, out } => {
                write!(f, "add {} + {} => {}", lhs, rhs, out)
            }
            OpCode::Sub { lhs, rhs, out } => {
                write!(f, "sub {} - {} => {}", lhs, rhs, out)
            }
            OpCode::Mul { lhs, rhs, out } => {
                write!(f, "mul {} * {} => {}", lhs, rhs, out)
            }
            OpCode::Div { lhs, rhs, out } => {
                write!(f, "div {} / {} => {}", lhs, rhs, out)
            }
            OpCode::Mod { lhs, rhs, out } => {
                write!(f, "mod {} % {} => {}", lhs, rhs, out)
            }
            OpCode::Eq { lhs, rhs, out } => {
                write!(f, "eq {} == {} => {}", lhs, rhs, out)
            }
            OpCode::Ne { lhs, rhs, out } => {
                write!(f, "ne {} != {} => {}", lhs, rhs, out)
            }
            OpCode::Lt { lhs, rhs, out } => {
                write!(f, "lt {} < {} => {}", lhs, rhs, out)
            }
            OpCode::Le { lhs, rhs, out } => {
                write!(f, "le {} <= {} => {}", lhs, rhs, out)
            }
            OpCode::Gt { lhs, rhs, out } => {
                write!(f, "gt {} > {} => {}", lhs, rhs, out)
            }
            OpCode::Ge { lhs, rhs, out } => {
                write!(f, "ge {} >= {} => {}", lhs, rhs, out)
            }
            OpCode::And { lhs, rhs, out } => {
                write!(f, "and {} && {} => {}", lhs, rhs, out)
            }
            OpCode::Or { lhs, rhs, out } => {
                write!(f, "or {} || {} => {}", lhs, rhs, out)
            }
            OpCode::Not { addr, out } => {
                write!(f, "not !{} => {}", addr, out)
            }
            OpCode::LoadConst { index, out } => {
                write!(f, "load_const[{}] => {}", index, out)
            }
            OpCode::Move { src, dst } => {
                write!(f, "move {} => {}", src, dst)
            }
            OpCode::Jump { offset } => {
                write!(f, "jump to offset {}", offset)
            }
            OpCode::JumpIfTrue { cond, offset } => {
                write!(f, "jump_if_true {} to offset {}", cond, offset)
            }
            OpCode::JumpIfFalse { cond, offset } => {
                write!(f, "jump_if_false {} to offset {}", cond, offset)
            }
            OpCode::Call { func_addr, args_count, out } => {
                write!(f, "call {}({} args) => {}", func_addr, args_count, out)
            }
            OpCode::Return { value } => {
                if let Some(addr) = value {
                    write!(f, "return {}", addr)
                } else {
                    write!(f, "return")
                }
            }
            OpCode::MakeArray { len, out } => {
                write!(f, "make_array[{}] => {}", len, out)
            }
            OpCode::IndexGet { array, index, out } => {
                write!(f, "index_get {}[{}] => {}", array, index, out)
            }
            OpCode::IndexSet { array, index, value } => {
                write!(f, "index_set {}[{}] = {}", array, index, value)
            }
            OpCode::Allocate { size } => {
                write!(f, "allocate {}", size)
            }
            OpCode::Pop { count } => {
                write!(f, "pop {}", count)
            }
            OpCode::Nop => write!(f, "nop"),
            OpCode::Halt => write!(f, "halt"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_address_display() {
        let stack_addr = Address::Stack(0);
        assert_eq!(stack_addr.to_string(), "stack[0]");

        let const_addr = Address::Const(5);
        assert_eq!(const_addr.to_string(), "const[5]");
    }

    #[test]
    fn test_output_display() {
        let stack_out = Output::Stack(1);
        assert_eq!(stack_out.to_string(), "stack[1]");

        let discard = Output::Discard;
        assert_eq!(discard.to_string(), "discard");
    }

    #[test]
    fn test_opcode_display() {
        let add = OpCode::Add {
            lhs: Address::Stack(0),
            rhs: Address::Stack(1),
            out: Output::Stack(2),
        };
        assert_eq!(add.to_string(), "add stack[0] + stack[1] => stack[2]");
    }
}
