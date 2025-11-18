//! 基础算术示例

use hola_vm::{Address, OpCode, Output, Value, Program, Vm};

fn main() {
    // 创建一个程序：计算 (2 + 3) * 4 - 1
    let mut program = Program::new();
    
    // 添加常数
    program.add_constant(Value::Integer(2));      // 常数 0
    program.add_constant(Value::Integer(3));      // 常数 1
    program.add_constant(Value::Integer(4));      // 常数 2
    program.add_constant(Value::Integer(1));      // 常数 3

    // 指令序列：
    // stack[0] = 2 + 3 = 5
    program.add_instruction(OpCode::Add {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });

    // stack[1] = stack[0] * 4 = 5 * 4 = 20
    program.add_instruction(OpCode::Mul {
        lhs: Address::Stack(0),
        rhs: Address::Const(2),
        out: Output::Stack(1),
    });

    // stack[2] = stack[1] - 1 = 20 - 1 = 19
    program.add_instruction(OpCode::Sub {
        lhs: Address::Stack(1),
        rhs: Address::Const(3),
        out: Output::Stack(2),
    });

    // 执行程序
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("执行成功！");
            println!("计算结果：(2 + 3) * 4 - 1 = {}", vm.stack().get(2).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }
}
