/// HOLA VM 对象操作、浮点数特殊操作和内存管理演示

use hola_vm::opcode::{Address, OpCode, Output};
use hola_vm::vm_core::{Program, Vm};
use hola_vm::value::Value;

fn main() {
    println!("=== HOLA VM 对象、数学和内存管理操作码演示 ===\n");

    // 对象操作演示
    demo_object_create();
    demo_object_set_get();
    demo_object_operations();

    // 浮点数特殊操作演示
    demo_float_pow();
    demo_float_sqrt();
    demo_math_operations();

    // 内存管理操作演示
    demo_clone();
    demo_typeof();
    demo_complex_scenario();
}

fn demo_object_create() {
    println!("示例 1: 创建空对象 (ObjectCreate)");
    let mut program = Program::new();
    
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("创建的对象: {:?}", vm.stack().get(0));
            println!("✓ 对象创建成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_object_set_get() {
    println!("示例 2: 对象字段设置和获取 (ObjectSet/ObjectGet)");
    let mut program = Program::new();
    
    program.add_constant(Value::String("name".to_string()));
    program.add_constant(Value::String("Alice".to_string()));
    program.add_constant(Value::String("age".to_string()));
    program.add_constant(Value::Integer(30));
    
    // 创建对象
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });
    
    // 设置 name 字段
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(0),
        value: Address::Const(1),
    });
    
    // 设置 age 字段
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(2),
        value: Address::Const(3),
    });
    
    // 获取 name 字段
    program.add_instruction(OpCode::ObjectGet {
        object: Address::Stack(0),
        key: Address::Const(0),
        out: Output::Stack(1),
    });
    
    // 获取 age 字段
    program.add_instruction(OpCode::ObjectGet {
        object: Address::Stack(0),
        key: Address::Const(2),
        out: Output::Stack(2),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("对象: {:?}", vm.stack().get(0));
            println!("获取的 name: {:?}", vm.stack().get(1));
            println!("获取的 age: {:?}", vm.stack().get(2));
            println!("✓ 对象操作成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_object_operations() {
    println!("示例 3: 复杂对象操作 (用户信息)");
    let mut program = Program::new();
    
    // 常数
    program.add_constant(Value::String("user".to_string()));
    program.add_constant(Value::String("username".to_string()));
    program.add_constant(Value::String("bob".to_string()));
    program.add_constant(Value::String("email".to_string()));
    program.add_constant(Value::String("bob@example.com".to_string()));
    program.add_constant(Value::String("active".to_string()));
    program.add_constant(Value::Bool(true));
    
    // 创建用户对象
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });
    
    // 设置 username
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(1),
        value: Address::Const(2),
    });
    
    // 设置 email
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(3),
        value: Address::Const(4),
    });
    
    // 设置 active
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(5),
        value: Address::Const(6),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("用户对象: {:?}", vm.stack().get(0));
            println!("✓ 复杂对象操作成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_float_pow() {
    println!("示例 4: 幂运算 (FloatPow)");
    println!("计算: 2 ** 10 = 1024 (整数幂)");
    println!("计算: 2.0 ** 3.0 = 8.0 (浮点幂)");
    
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(2));
    program.add_constant(Value::Integer(10));
    program.add_constant(Value::Float(2.0));
    program.add_constant(Value::Float(3.0));
    
    // 整数幂运算
    program.add_instruction(OpCode::FloatPow {
        base: Address::Const(0),
        exponent: Address::Const(1),
        out: Output::Stack(0),
    });
    
    // 浮点幂运算
    program.add_instruction(OpCode::FloatPow {
        base: Address::Const(2),
        exponent: Address::Const(3),
        out: Output::Stack(1),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("2 ** 10 = {:?}", vm.stack().get(0));
            println!("2.0 ** 3.0 = {:?}", vm.stack().get(1));
            println!("✓ 幂运算成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_float_sqrt() {
    println!("示例 5: 平方根 (FloatSqrt)");
    println!("计算: sqrt(16) = 4.0");
    println!("计算: sqrt(2.0) ≈ 1.414");
    
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(16));
    program.add_constant(Value::Float(2.0));
    
    // 整数平方根
    program.add_instruction(OpCode::FloatSqrt {
        addr: Address::Const(0),
        out: Output::Stack(0),
    });
    
    // 浮点平方根
    program.add_instruction(OpCode::FloatSqrt {
        addr: Address::Const(1),
        out: Output::Stack(1),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("sqrt(16) = {:?}", vm.stack().get(0));
            println!("sqrt(2.0) = {:?}", vm.stack().get(1));
            println!("✓ 平方根成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_math_operations() {
    println!("示例 6: 几何计算 (圆的面积和周长)");
    println!("半径: 5");
    println!("周长 = 2πr = 2 * 3.14159 * 5 ≈ 31.4159");
    println!("面积 = πr² = 3.14159 * 5 ** 2 ≈ 78.54");
    
    let mut program = Program::new();
    
    let pi = 3.14159;
    let radius = 5.0;
    
    program.add_constant(Value::Float(2.0));
    program.add_constant(Value::Float(pi));
    program.add_constant(Value::Float(radius));
    program.add_constant(Value::Integer(2));
    
    // 计算周长: 2 * pi * r
    program.add_instruction(OpCode::Mul {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    program.add_instruction(OpCode::Mul {
        lhs: Address::Stack(0),
        rhs: Address::Const(2),
        out: Output::Stack(1),
    });
    
    // 计算面积: pi * r^2
    program.add_instruction(OpCode::FloatPow {
        base: Address::Const(2),
        exponent: Address::Const(3),
        out: Output::Stack(2),
    });
    
    program.add_instruction(OpCode::Mul {
        lhs: Address::Const(1),
        rhs: Address::Stack(2),
        out: Output::Stack(3),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("周长 ≈ {:?}", vm.stack().get(1));
            println!("面积 ≈ {:?}", vm.stack().get(3));
            println!("✓ 几何计算成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_clone() {
    println!("示例 7: 深复制 (Clone)");
    let mut program = Program::new();
    
    // 创建数组
    program.add_instruction(OpCode::MakeArray {
        len: 3,
        out: Output::Stack(0),
    });
    
    // 复制数组
    program.add_instruction(OpCode::Clone {
        addr: Address::Stack(0),
        out: Output::Stack(1),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("原数组: {:?}", vm.stack().get(0));
            println!("复制的数组: {:?}", vm.stack().get(1));
            println!("✓ 深复制成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_typeof() {
    println!("示例 8: 类型检查 (Typeof)");
    let mut program = Program::new();
    
    program.add_constant(Value::Integer(42));
    program.add_constant(Value::Float(3.14));
    program.add_constant(Value::String("hello".to_string()));
    program.add_constant(Value::Bool(true));
    program.add_constant(Value::Null);
    
    // 检查所有类型
    for (i, _) in (0..5).enumerate() {
        program.add_instruction(OpCode::Typeof {
            addr: Address::Const(i),
            out: Output::Stack(i),
        });
    }
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            let types = vec!["integer", "float", "string", "bool", "null"];
            for (i, type_name) in types.iter().enumerate() {
                println!("{}: {:?}", type_name, vm.stack().get(i));
            }
            println!("✓ 类型检查成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_complex_scenario() {
    println!("示例 9: 综合场景 (员工数据库)");
    let mut program = Program::new();
    
    // 常数定义
    program.add_constant(Value::String("name".to_string()));
    program.add_constant(Value::String("John Doe".to_string()));
    program.add_constant(Value::String("salary".to_string()));
    program.add_constant(Value::Float(50000.0));
    program.add_constant(Value::String("bonus_rate".to_string()));
    program.add_constant(Value::Float(0.1));
    program.add_constant(Value::Float(1.0));
    
    // 创建员工对象
    program.add_instruction(OpCode::ObjectCreate {
        out: Output::Stack(0),
    });
    
    // 设置 name
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(0),
        value: Address::Const(1),
    });
    
    // 设置 salary
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(2),
        value: Address::Const(3),
    });
    
    // 设置 bonus_rate
    program.add_instruction(OpCode::ObjectSet {
        object: Address::Stack(0),
        key: Address::Const(4),
        value: Address::Const(5),
    });
    
    // 获取 salary
    program.add_instruction(OpCode::ObjectGet {
        object: Address::Stack(0),
        key: Address::Const(2),
        out: Output::Stack(1),
    });
    
    // 计算奖金: salary * bonus_rate
    program.add_instruction(OpCode::Mul {
        lhs: Address::Stack(1),
        rhs: Address::Const(5),
        out: Output::Stack(2),
    });
    
    // 克隆员工对象用于存档
    program.add_instruction(OpCode::Clone {
        addr: Address::Stack(0),
        out: Output::Stack(3),
    });
    
    // 获取员工对象的类型
    program.add_instruction(OpCode::Typeof {
        addr: Address::Stack(0),
        out: Output::Stack(4),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("员工对象: {:?}", vm.stack().get(0));
            println!("基本工资: {:?}", vm.stack().get(1));
            println!("年度奖金: {:?}", vm.stack().get(2));
            println!("存档副本: {:?}", vm.stack().get(3));
            println!("对象类型: {:?}", vm.stack().get(4));
            println!("✓ 综合场景成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}
