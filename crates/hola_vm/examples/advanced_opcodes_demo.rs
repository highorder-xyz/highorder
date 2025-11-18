/// HOLA VM 第 1-4 阶段高级操作码演示

use hola_vm::opcode::{Address, OpCode, Output};
use hola_vm::vm_core::{Program, Vm};
use hola_vm::value::Value;

fn main() {
    println!("=== HOLA VM 第 1-4 阶段高级操作码演示 ===\n");

    // 第 1 阶段
    demo_stage1_core_opcodes();

    // 第 2 阶段
    demo_stage2_oop_opcodes();

    // 第 3 阶段
    demo_stage3_advanced_opcodes();

    // 第 4 阶段
    demo_stage4_async_opcodes();
}

fn demo_stage1_core_opcodes() {
    println!("=== 第 1 阶段：核心缺失操作码 ===\n");

    // Neg - 数值取反
    println!("示例 1: Neg (数值取反)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(42));
    program.add_constant(Value::Float(3.14));

    program.add_instruction(OpCode::Neg {
        addr: Address::Const(0),
        out: Output::Stack(0),
    });

    program.add_instruction(OpCode::Neg {
        addr: Address::Const(1),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  -42 = {:?}", vm.stack().get(0));
            println!("  -3.14 = {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // As - 类型转换
    println!("示例 2: As (类型转换)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(100));
    program.add_constant(Value::Float(50.5));

    program.add_instruction(OpCode::As {
        value: Address::Const(0),
        expected_type: "float".to_string(),
        out: Output::Stack(0),
    });

    program.add_instruction(OpCode::As {
        value: Address::Const(1),
        expected_type: "integer".to_string(),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  100 as float = {:?}", vm.stack().get(0));
            println!("  50.5 as integer = {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Is/IsNot - 类型检查
    println!("示例 3: Is/IsNot (类型检查)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(42));
    program.add_constant(Value::String("hello".to_string()));

    program.add_instruction(OpCode::Is {
        value: Address::Const(0),
        expected_type: "integer".to_string(),
        out: Output::Stack(0),
    });

    program.add_instruction(OpCode::IsNot {
        value: Address::Const(1),
        expected_type: "integer".to_string(),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  42 is integer = {:?}", vm.stack().get(0));
            println!("  \"hello\" is not integer = {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Try - 错误传播
    println!("示例 4: Try (错误传播)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(100));

    program.add_instruction(OpCode::Try {
        addr: Address::Const(0),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  Try 100 = {:?}\n", vm.stack().get(0));
        }
        Err(e) => println!("  捕获异常: {}\n", e),
    }
}

fn demo_stage2_oop_opcodes() {
    println!("=== 第 2 阶段：OOP 支持 ===\n");

    // LoadInstanceFn - 加载实例方法
    println!("示例 5: LoadInstanceFn (加载实例方法)");
    let mut program = Program::new();
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });

    program.add_instruction(OpCode::LoadInstanceFn {
        instance: Address::Stack(0),
        method_name: "to_string".to_string(),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  加载的方法: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // CallAssociated - 调用关联方法
    println!("示例 6: CallAssociated (调用关联方法)");
    let mut program = Program::new();
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });

    program.add_instruction(OpCode::CallAssociated {
        instance: Address::Stack(0),
        method_name: "length".to_string(),
        args_count: 1,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  方法调用结果: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Struct - 结构体构造
    println!("示例 7: Struct (结构体构造)");
    let mut program = Program::new();
    program.add_instruction(OpCode::Struct {
        addr: Address::Stack(0),
        struct_name: "Point".to_string(),
        field_count: 2,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  构造的结构体: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }
}

fn demo_stage3_advanced_opcodes() {
    println!("=== 第 3 阶段：迭代和高级功能 ===\n");

    // Closure - 闭包构造
    println!("示例 8: Closure (闭包构造)");
    let mut program = Program::new();
    program.add_instruction(OpCode::Closure {
        func_hash: 12345,
        capture_addr: Address::Stack(0),
        capture_count: 2,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  构造的闭包: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Environment - 闭包环境展开
    println!("示例 9: Environment (闭包环境展开)");
    let mut program = Program::new();
    program.add_constant(Value::Tuple(vec![Value::Integer(1), Value::Integer(2)]));

    program.add_instruction(OpCode::Environment {
        tuple_addr: Address::Const(0),
        expected_count: 2,
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  展开的环境: {:?}\n", vm.stack().get(0));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Format - 值格式化
    println!("示例 10: Format (值格式化)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(42));

    program.add_instruction(OpCode::Format {
        value_addr: Address::Const(0),
        format_spec: "hex".to_string(),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  格式化后: {:?}\n", vm.stack().get(0));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // IterNext - 迭代器推进
    println!("示例 11: IterNext (迭代器推进)");
    let mut program = Program::new();
    program.add_instruction(OpCode::IterNext {
        iterator_addr: Address::Stack(0),
        jump_offset: 5,
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  迭代器推进成功\n");
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }
}

fn demo_stage4_async_opcodes() {
    println!("=== 第 4 阶段：异步支持 ===\n");

    // Await - 等待 Future
    println!("示例 12: Await (等待 Future)");
    let mut program = Program::new();
    program.add_instruction(OpCode::Await {
        future_addr: Address::Stack(0),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  Await 结果: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Yield - 生成器 yield
    println!("示例 13: Yield (生成器 yield)");
    let mut program = Program::new();
    program.add_constant(Value::Integer(100));

    program.add_instruction(OpCode::Yield {
        value_addr: Address::Const(0),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  Yield 值: {:?}\n", vm.stack().get(0));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // YieldUnit - 生成器 yield unit
    println!("示例 14: YieldUnit (生成器 yield unit)");
    let mut program = Program::new();
    program.add_instruction(OpCode::YieldUnit {
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  Yield unit 结果: {:?}\n", vm.stack().get(0));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    // Select - Future 选择
    println!("示例 15: Select (Future 选择)");
    let mut program = Program::new();
    program.add_instruction(OpCode::Select {
        futures_addr: Address::Stack(0),
        futures_count: 3,
        value_out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("  Select 结果: {:?}\n", vm.stack().get(1));
        }
        Err(e) => println!("  ✗ 错误: {}\n", e),
    }

    println!("=== 所有阶段操作码演示完成！===");
}
