use hola_vm::{
    opcode::{Address, OpCode, Output},
    value::Value,
    vm_core::{Program, Vm},
};

fn main() {
    println!("=== 字符串处理示例 ===\n");

    let mut program = Program::new();

    // 示例 1: 字符串连接
    println!("示例 1: 字符串连接");
    program.add_constant(Value::String("Hello".to_string()));
    program.add_constant(Value::String(" World".to_string()));
    
    program.add_instruction(OpCode::StrConcat {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("连接结果: {}", val);
    }

    // 示例 2: 字符串长度
    println!("\n示例 2: 字符串长度");
    let mut program = Program::new();
    program.add_constant(Value::String("HOLA".to_string()));
    
    program.add_instruction(OpCode::StrLen {
        addr: Address::Const(0),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("字符串长度: {}", val);
    }

    // 示例 3: 字符串查找
    println!("\n示例 3: 字符串查找");
    let mut program = Program::new();
    program.add_constant(Value::String("Hello World".to_string()));
    program.add_constant(Value::String("World".to_string()));
    
    program.add_instruction(OpCode::StrFind {
        haystack: Address::Const(0),
        needle: Address::Const(1),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("'World' 在位置: {}", val);
    }

    // 示例 4: 字符串替换
    println!("\n示例 4: 字符串替换");
    let mut program = Program::new();
    program.add_constant(Value::String("Hello Rust".to_string()));
    program.add_constant(Value::String("Rust".to_string()));
    program.add_constant(Value::String("Hola".to_string()));
    
    program.add_instruction(OpCode::StrReplace {
        text: Address::Const(0),
        from: Address::Const(1),
        to: Address::Const(2),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("替换后: {}", val);
    }

    // 示例 5: 栈优化 - Copy
    println!("\n示例 5: 栈优化 - Copy");
    let mut program = Program::new();
    program.add_constant(Value::Integer(42));
    
    program.add_instruction(OpCode::Copy {
        src: Address::Const(0),
        out: Output::Stack(0),
    });
    
    program.add_instruction(OpCode::Copy {
        src: Address::Stack(0),
        out: Output::Stack(1),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    println!("Stack[0]: {}", vm.stack().get(0).unwrap());
    println!("Stack[1]: {}", vm.stack().get(1).unwrap());

    // 示例 6: 栈优化 - Swap
    println!("\n示例 6: 栈优化 - Swap");
    let mut program = Program::new();
    program.add_constant(Value::Integer(10));
    program.add_constant(Value::Integer(20));
    
    program.add_instruction(OpCode::Copy {
        src: Address::Const(0),
        out: Output::Stack(0),
    });
    
    program.add_instruction(OpCode::Copy {
        src: Address::Const(1),
        out: Output::Stack(1),
    });
    
    program.add_instruction(OpCode::Swap {
        addr1: Address::Stack(0),
        addr2: Address::Stack(1),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    println!("交换后 Stack[0]: {}", vm.stack().get(0).unwrap());
    println!("交换后 Stack[1]: {}", vm.stack().get(1).unwrap());

    // 示例 7: 类型检查
    println!("\n示例 7: 类型检查");
    let mut program = Program::new();
    program.add_constant(Value::String("test".to_string()));
    
    program.add_instruction(OpCode::TypeCheck {
        addr: Address::Const(0),
        expected_type: "string".to_string(),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("是字符串吗? {}", val);
    }

    // 示例 8: 模式匹配测试
    println!("\n示例 8: 模式匹配测试");
    let mut program = Program::new();
    program.add_constant(Value::Null);
    
    program.add_instruction(OpCode::MatchTest {
        value: Address::Const(0),
        pattern: "null".to_string(),
        out: Output::Stack(0),
    });

    let mut vm = Vm::new(program);
    vm.execute().unwrap();
    
    if let Some(val) = vm.stack().get(0) {
        println!("匹配 null 模式? {}", val);
    }

    println!("\n✓ 所有示例执行完成！");
}
