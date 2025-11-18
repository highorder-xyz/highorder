//! 元组和范围示例

use hola_vm::{Address, OpCode, Output, Value, Program, Vm};

fn main() {
    println!("=== 元组示例 ===");
    
    // 创建一个元组 (1, 2, 3)
    let mut program = Program::new();
    program.add_constant(Value::Integer(1));
    program.add_constant(Value::Integer(2));
    program.add_constant(Value::Integer(3));

    // 使用优化的 Tuple3 创建三元组
    program.add_instruction(OpCode::Tuple3 {
        addr1: Address::Const(0),
        addr2: Address::Const(1),
        addr3: Address::Const(2),
        out: Output::Stack(0),
    });

    // 获取元组的第二个元素（索引为 1）
    program.add_instruction(OpCode::TupleIndexGetAt {
        addr: Address::Stack(0),
        index: 1,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("元组创建成功！");
            println!("元组: {}", vm.stack().get(0).unwrap());
            println!("第二个元素: {}", vm.stack().get(1).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }

    println!("\n=== 范围示例 ===");

    // 创建一个范围 0..10
    let mut program = Program::new();
    program.add_constant(Value::Integer(0));
    program.add_constant(Value::Integer(10));

    program.add_instruction(OpCode::Range {
        start: Some(Address::Const(0)),
        end: Some(Address::Const(1)),
        inclusive: false,
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("范围创建成功！");
            println!("范围: {}", vm.stack().get(0).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }

    println!("\n=== 包含范围示例 ===");

    // 创建一个包含范围 1..=5
    let mut program = Program::new();
    program.add_constant(Value::Integer(1));
    program.add_constant(Value::Integer(5));

    program.add_instruction(OpCode::Range {
        start: Some(Address::Const(0)),
        end: Some(Address::Const(1)),
        inclusive: true,
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("包含范围创建成功！");
            println!("范围: {}", vm.stack().get(0).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }

    println!("\n=== 函数引用示例 ===");

    // 加载函数引用
    let mut program = Program::new();
    program.add_instruction(OpCode::LoadFn {
        hash: 0x1234567890abcdef,
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("函数引用加载成功！");
            println!("函数: {}", vm.stack().get(0).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }

    println!("\n=== 元组索引修改示例 ===");

    // 创建元组并修改其中一个元素
    let mut program = Program::new();
    program.add_constant(Value::Integer(10));
    program.add_constant(Value::Integer(20));
    program.add_constant(Value::Integer(30));
    program.add_constant(Value::Integer(999)); // 新值

    // 创建元组 (10, 20, 30)
    program.add_instruction(OpCode::Tuple3 {
        addr1: Address::Const(0),
        addr2: Address::Const(1),
        addr3: Address::Const(2),
        out: Output::Stack(0),
    });

    // 将元组的第二个元素修改为 999
    program.add_instruction(OpCode::TupleIndexSet {
        target: Address::Stack(0),
        index: 1,
        value: Address::Const(3),
    });

    // 获取修改后的第二个元素
    program.add_instruction(OpCode::TupleIndexGetAt {
        addr: Address::Stack(0),
        index: 1,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("元组修改成功！");
            println!("修改后的第二个元素: {}", vm.stack().get(1).unwrap());
        }
        Err(e) => {
            eprintln!("执行失败：{}", e);
        }
    }
}
