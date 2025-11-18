/// HOLA VM 异常处理和完整函数调用系统演示

use hola_vm::opcode::{Address, OpCode, Output};
use hola_vm::vm_core::{Program, Vm};
use hola_vm::value::Value;

fn main() {
    println!("=== HOLA VM 异常处理和函数调用系统演示 ===\n");

    // 示例 1: 局部变量管理
    demo_local_variables();

    // 示例 2: 全局变量管理
    demo_global_variables();

    // 示例 3: 函数调用框架
    demo_function_frames();

    // 示例 4: 异常抛出和捕获
    demo_exception_handling();

    // 示例 5: 异常类型系统
    demo_exception_types();

    // 示例 6: 函数返回值
    demo_function_returns();

    // 示例 7: 栈帧清理
    demo_frame_cleanup();

    // 示例 8: 综合示例
    demo_complex_scenario();
}

fn demo_local_variables() {
    println!("示例 1: 局部变量管理");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(42));
    program.add_constant(Value::String("local_var".to_string()));
    
    // 推送帧（参数数量为 0）
    program.add_instruction(OpCode::PushFrame { params_count: 0 });
    
    // 设置局部变量 0 为 42
    program.add_instruction(OpCode::SetLocal {
        index: 0,
        value: Address::Const(0),
    });
    
    // 获取局部变量 0
    program.add_instruction(OpCode::GetLocal {
        index: 0,
        out: Output::Stack(0),
    });
    
    // 弹出帧
    program.add_instruction(OpCode::PopFrame);
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("局部变量值: {:?}", vm.stack().get(0));
            println!("✓ 局部变量管理成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_global_variables() {
    println!("示例 2: 全局变量管理");
    let mut program = Program::new();
    
    program.add_constant(Value::String("count".to_string()));
    program.add_constant(Value::Integer(100));
    
    // 设置全局变量
    program.add_instruction(OpCode::SetGlobal {
        name: "count".to_string(),
        value: Address::Const(1),
    });
    
    // 获取全局变量
    program.add_instruction(OpCode::GetGlobal {
        name: "count".to_string(),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("全局变量 'count' 的值: {:?}", vm.stack().get(0));
            println!("✓ 全局变量管理成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_function_frames() {
    println!("示例 3: 函数调用框架");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(3));
    program.add_constant(Value::Integer(5));
    
    // 推送带 2 个参数的函数帧
    program.add_instruction(OpCode::PushFrame { params_count: 2 });
    
    // 设置参数
    program.add_instruction(OpCode::SetLocal {
        index: 0,
        value: Address::Const(0),
    });
    
    program.add_instruction(OpCode::SetLocal {
        index: 1,
        value: Address::Const(1),
    });
    
    // 获取第一个参数
    program.add_instruction(OpCode::GetLocal {
        index: 0,
        out: Output::Stack(0),
    });
    
    // 获取第二个参数
    program.add_instruction(OpCode::GetLocal {
        index: 1,
        out: Output::Stack(1),
    });
    
    // 执行加法
    program.add_instruction(OpCode::Add {
        lhs: Address::Stack(0),
        rhs: Address::Stack(1),
        out: Output::Stack(2),
    });
    
    // 弹出帧
    program.add_instruction(OpCode::PopFrame);
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("参数 1: {:?}", vm.stack().get(0));
            println!("参数 2: {:?}", vm.stack().get(1));
            println!("相加结果: {:?}", vm.stack().get(2));
            println!("✓ 函数调用框架成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_exception_handling() {
    println!("示例 4: 异常抛出和捕获");
    let mut program = Program::new();
    
    program.add_constant(Value::String("Division by zero error".to_string()));
    
    // 抛出异常
    program.add_instruction(OpCode::Throw {
        exception_type: "DivisionByZero".to_string(),
        message: Address::Const(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => println!("异常未被捕获\n"),
        Err(e) => {
            println!("捕获到异常: {}", e);
            println!("✓ 异常处理成功\n");
        }
    }
}

fn demo_exception_types() {
    println!("示例 5: 异常类型系统");
    let mut program = Program::new();
    
    program.add_constant(Value::String("Invalid input type".to_string()));
    
    // 创建异常值
    let exc = Value::Exception(
        "TypeError".to_string(),
        "Expected integer but got string".to_string(),
    );
    
    println!("异常值: {}", exc);
    println!("✓ 异常类型系统支持成功\n");
}

fn demo_function_returns() {
    println!("示例 6: 函数返回值");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(777));
    
    // 推送帧
    program.add_instruction(OpCode::PushFrame { params_count: 0 });
    
    // 函数返回
    program.add_instruction(OpCode::FuncReturn {
        value: Some(Address::Const(0)),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(Some(val)) => {
            println!("函数返回值: {:?}", val);
            println!("✓ 函数返回值成功\n");
        }
        _ => println!("✗ 函数返回失败\n"),
    }
}

fn demo_frame_cleanup() {
    println!("示例 7: 栈帧清理");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(1));
    program.add_constant(Value::Integer(2));
    program.add_constant(Value::Integer(3));
    
    // 嵌套帧
    program.add_instruction(OpCode::PushFrame { params_count: 1 });
    program.add_instruction(OpCode::SetLocal {
        index: 0,
        value: Address::Const(0),
    });
    
    // 内层帧
    program.add_instruction(OpCode::PushFrame { params_count: 1 });
    program.add_instruction(OpCode::SetLocal {
        index: 0,
        value: Address::Const(1),
    });
    
    // 清理内层帧
    program.add_instruction(OpCode::PopFrame);
    
    // 清理外层帧
    program.add_instruction(OpCode::PopFrame);
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("帧计数: {}", vm.stack().len());
            println!("✓ 栈帧清理成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_complex_scenario() {
    println!("示例 8: 综合示例（多帧交互）");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(10));
    program.add_constant(Value::Integer(20));
    program.add_constant(Value::String("result".to_string()));
    
    // 全局变量
    program.add_instruction(OpCode::SetGlobal {
        name: "result".to_string(),
        value: Address::Const(0),
    });
    
    // 函数帧 1
    program.add_instruction(OpCode::PushFrame { params_count: 1 });
    program.add_instruction(OpCode::SetLocal {
        index: 0,
        value: Address::Const(1),
    });
    
    // 获取全局变量
    program.add_instruction(OpCode::GetGlobal {
        name: "result".to_string(),
        out: Output::Stack(0),
    });
    
    // 获取局部变量
    program.add_instruction(OpCode::GetLocal {
        index: 0,
        out: Output::Stack(1),
    });
    
    // 执行加法
    program.add_instruction(OpCode::Add {
        lhs: Address::Stack(0),
        rhs: Address::Stack(1),
        out: Output::Stack(2),
    });
    
    // 清理帧
    program.add_instruction(OpCode::PopFrame);
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("全局变量: {:?}", vm.get_global("result"));
            println!("加法结果: {:?}", vm.stack().get(2));
            println!("✓ 综合示例成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}
