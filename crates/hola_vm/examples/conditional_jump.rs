//! 条件跳转示例
//! 这个示例展示如何使用条件跳转指令

use hola_vm::{Address, OpCode, Output, Value, Program, Vm};

fn main() {
    // 创建一个程序：
    // if (10 > 5) {
    //     result = 100
    // } else {
    //     result = 200
    // }

    let mut program = Program::new();

    // 添加常数
    program.add_constant(Value::Integer(10));      // 常数 0
    program.add_constant(Value::Integer(5));       // 常数 1
    program.add_constant(Value::Integer(100));     // 常数 2
    program.add_constant(Value::Integer(200));     // 常数 3

    // 指令索引：
    // 0: 比较 10 > 5，结果存储在 stack[0]
    program.add_instruction(OpCode::Gt {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });

    // 1: 如果条件为假，跳转到指令 4（else 分支）
    program.add_instruction(OpCode::JumpIfFalse {
        cond: Address::Stack(0),
        offset: 4,
    });

    // 2: 条件为真时执行：stack[1] = 100
    program.add_instruction(OpCode::Move {
        src: Address::Const(2),
        dst: Output::Stack(1),
    });

    // 3: 跳转到指令 5（跳过 else 分支）
    program.add_instruction(OpCode::Jump { offset: 5 });

    // 4: else 分支：stack[1] = 200
    program.add_instruction(OpCode::Move {
        src: Address::Const(3),
        dst: Output::Stack(1),
    });

    // 5: 程序结束
    program.add_instruction(OpCode::Halt);

    // 执行程序
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("执行成功！");
            let result = vm.stack().get(1).unwrap();
            println!("条件表达式 if (10 > 5) 的结果：{}", result);
            assert_eq!(result, &Value::Integer(100));
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }
}
