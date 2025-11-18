/// HOLA VM 位运算演示

use hola_vm::opcode::{Address, OpCode, Output};
use hola_vm::vm_core::{Program, Vm};
use hola_vm::value::Value;

fn main() {
    println!("=== HOLA VM 位运算操作码演示 ===\n");

    // 示例 1: 按位与 (Bitwise AND)
    demo_bitwise_and();

    // 示例 2: 按位或 (Bitwise OR)
    demo_bitwise_or();

    // 示例 3: 按位异或 (Bitwise XOR)
    demo_bitwise_xor();

    // 示例 4: 按位非 (Bitwise NOT)
    demo_bitwise_not();

    // 示例 5: 左移 (Shift Left)
    demo_shift_left();

    // 示例 6: 右移 (Shift Right)
    demo_shift_right();

    // 示例 7: 位掩码应用
    demo_bitmask();

    // 示例 8: 权限标志检查
    demo_permission_flags();
}

fn demo_bitwise_and() {
    println!("示例 1: 按位与 (Bitwise AND)");
    println!("计算: 12 & 10");
    println!("二进制: 1100 & 1010 = 1000 (8)");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(12));
    program.add_constant(Value::Integer(10));
    
    program.add_instruction(OpCode::BitwiseAnd {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 按位与成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_bitwise_or() {
    println!("示例 2: 按位或 (Bitwise OR)");
    println!("计算: 12 | 10");
    println!("二进制: 1100 | 1010 = 1110 (14)");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(12));
    program.add_constant(Value::Integer(10));
    
    program.add_instruction(OpCode::BitwiseOr {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 按位或成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_bitwise_xor() {
    println!("示例 3: 按位异或 (Bitwise XOR)");
    println!("计算: 12 ^ 10");
    println!("二进制: 1100 ^ 1010 = 0110 (6)");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(12));
    program.add_constant(Value::Integer(10));
    
    program.add_instruction(OpCode::BitwiseXor {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 按位异或成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_bitwise_not() {
    println!("示例 4: 按位非 (Bitwise NOT)");
    println!("计算: ~5");
    println!("二进制: ~0101 = ...11111010 (-6)");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(5));
    
    program.add_instruction(OpCode::BitwiseNot {
        addr: Address::Const(0),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 按位非成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_shift_left() {
    println!("示例 5: 左移 (Shift Left)");
    println!("计算: 3 << 2");
    println!("二进制: 0011 << 2 = 1100 (12) [乘以 2^2 = 4]");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(3));
    program.add_constant(Value::Integer(2));
    
    program.add_instruction(OpCode::ShiftLeft {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 左移成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_shift_right() {
    println!("示例 6: 右移 (Shift Right)");
    println!("计算: 12 >> 2");
    println!("二进制: 1100 >> 2 = 0011 (3) [除以 2^2 = 4]");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(12));
    program.add_constant(Value::Integer(2));
    
    program.add_instruction(OpCode::ShiftRight {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("结果: {:?}", vm.stack().get(0));
            println!("✓ 右移成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_bitmask() {
    println!("示例 7: 位掩码应用");
    println!("提取二进制数中的特定位");
    println!("原始值: 255 (11111111)");
    println!("掩码: 240 (11110000) - 高 4 位");
    println!("255 & 240 = 240 (高 4 位为 1, 低 4 位为 0)");
    
    let mut program = Program::new();
    program.add_constant(Value::Integer(255));
    program.add_constant(Value::Integer(240));
    
    // 提取高 4 位
    program.add_instruction(OpCode::BitwiseAnd {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    // 右移 4 位得到高 4 位的值
    program.add_constant(Value::Integer(4));
    program.add_instruction(OpCode::ShiftRight {
        lhs: Address::Stack(0),
        rhs: Address::Const(2),
        out: Output::Stack(1),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            println!("掩码后: {:?}", vm.stack().get(0));
            println!("右移后: {:?} (即高 4 位的值)", vm.stack().get(1));
            println!("✓ 位掩码应用成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}

fn demo_permission_flags() {
    println!("示例 8: 权限标志检查 (经典应用)");
    println!("权限定义: READ=1(001), WRITE=2(010), EXECUTE=4(100)");
    println!("用户权限: 5 (101) = READ + EXECUTE");
    println!("检查是否有 READ 权限: 5 & 1 = 1 (有)");
    println!("检查是否有 WRITE 权限: 5 & 2 = 0 (无)");
    
    let mut program = Program::new();
    let read_flag = 1;
    let write_flag = 2;
    let user_permissions = 5; // READ + EXECUTE
    
    program.add_constant(Value::Integer(user_permissions));
    program.add_constant(Value::Integer(read_flag));
    program.add_constant(Value::Integer(write_flag));
    
    // 检查 READ 权限
    program.add_instruction(OpCode::BitwiseAnd {
        lhs: Address::Const(0),
        rhs: Address::Const(1),
        out: Output::Stack(0),
    });
    
    // 检查 WRITE 权限
    program.add_instruction(OpCode::BitwiseAnd {
        lhs: Address::Const(0),
        rhs: Address::Const(2),
        out: Output::Stack(1),
    });
    
    let mut vm = Vm::new(program);
    match vm.execute() {
        Ok(_) => {
            let has_read = vm.stack().get(0);
            let has_write = vm.stack().get(1);
            println!("READ 权限检查结果: {:?} (非零为 true)", has_read);
            println!("WRITE 权限检查结果: {:?} (非零为 true)", has_write);
            println!("✓ 权限标志检查成功\n");
        }
        Err(e) => println!("✗ 错误: {}\n", e),
    }
}
