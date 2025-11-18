//! HOLA虚拟机实现
//!
//! 这个库提供了HOLA语言的虚拟机实现，用于执行编译后的字节码。
//! 
//! ## 设计特点
//! 
//! - **栈式虚拟机**：采用栈式架构，参考Rune VM设计
//! - **完整的操作码**：支持算术、比较、逻辑、控制流等操作
//! - **类型系统**：支持整数、浮点数、布尔值、字符串、数组等类型
//! - **动态类型**：运行时类型检查和转换
//!
//! ## 快速开始
//!
//! ```
//! use hola_vm::{
//!     opcode::{Address, OpCode, Output},
//!     value::Value,
//!     vm_core::{Program, Vm},
//! };
//!
//! let mut program = Program::new();
//! program.add_constant(Value::Integer(2));
//! program.add_constant(Value::Integer(3));
//! program.add_instruction(OpCode::Add {
//!     lhs: Address::Const(0),
//!     rhs: Address::Const(1),
//!     out: Output::Stack(0),
//! });
//!
//! let mut vm = Vm::new(program);
//! vm.execute().unwrap();
//!
//! assert_eq!(vm.stack().get(0), Some(&Value::Integer(5)));
//! ```

pub mod opcode;
pub mod value;
pub mod stack;
pub mod vm_core;

pub use opcode::{Address, OpCode, Output};
pub use value::Value;
pub use stack::Stack;
pub use vm_core::{Program, Vm, VmError};