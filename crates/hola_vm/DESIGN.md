# HOLA 虚拟机设计文档

## 概述

HOLA 虚拟机是一个栈式虚拟机实现，设计灵感来自 Rune VM。它提供了一个完整的执行环境来运行编译后的 HOLA 字节码。

## 架构

### 栈式设计

虚拟机采用经典的栈式架构，类似于 JVM 和 Rune VM：

```
┌─────────────────────┐
│   Instruction       │
│   Pointer (IP)      │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Instructions      │
│   Sequence          │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Stack             │
│   ┌───────────────┐ │
│   │ Value[n]      │ │
│   │ ...           │ │
│   │ Value[0]      │ │
│   └───────────────┘ │
└─────────────────────┘
```

### 核心组件

#### 1. 操作码 (OpCode)

操作码定义在 `opcode.rs` 中，包括：

**算术运算**
- `Add`: 加法
- `Sub`: 减法
- `Mul`: 乘法
- `Div`: 除法
- `Mod`: 模运算

**比较运算**
- `Eq`: 相等
- `Ne`: 不相等
- `Lt`: 小于
- `Le`: 小于等于
- `Gt`: 大于
- `Ge`: 大于等于

**逻辑运算**
- `And`: 逻辑与
- `Or`: 逻辑或
- `Not`: 逻辑非

**数据操作**
- `LoadConst`: 加载常数
- `Move`: 数据移动
- `MakeArray`: 创建数组
- `IndexGet`: 数组索引访问
- `IndexSet`: 数组索引设置

**控制流**
- `Jump`: 无条件跳转
- `JumpIfTrue`: 条件跳转（真）
- `JumpIfFalse`: 条件跳转（假）
- `Call`: 函数调用
- `Return`: 返回

**栈管理**
- `Allocate`: 分配栈空间
- `Pop`: 弹出栈元素

**其他**
- `Nop`: 无操作
- `Halt`: 停止执行

#### 2. 地址寻址模式

```rust
pub enum Address {
    Stack(usize),   // 栈相对地址
    Const(usize),   // 常数池索引
}
```

#### 3. 输出位置

```rust
pub enum Output {
    Stack(usize),   // 存储到栈
    Discard,        // 丢弃结果
}
```

#### 4. 值类型 (Value)

支持的值类型：

```rust
pub enum Value {
    Integer(i64),              // 整数
    Float(f64),                // 浮点数
    Bool(bool),                // 布尔值
    String(String),            // 字符串
    Array(Vec<Value>),         // 数组
    Object(HashMap<...>),      // 对象
    Null,                       // 空值
}
```

#### 5. 栈 (Stack)

栈实现提供标准操作：

- `push(value)`: 入栈
- `pop()`: 出栈
- `peek()`: 查看栈顶
- `allocate(size)`: 分配空间
- `get(index)`: 获取指定位置的值
- `set(index, value)`: 设置指定位置的值

#### 6. 程序 (Program)

程序包含：

- **常数池**: 编译时确定的常数值
- **指令序列**: 待执行的操作码序列

```rust
pub struct Program {
    pub constants: Vec<Value>,
    pub instructions: Vec<OpCode>,
}
```

#### 7. 虚拟机 (Vm)

主执行引擎，包含：

- 指令指针 (IP): 当前执行位置
- 栈: 数据存储
- 常数池: 快速访问常数
- 全局变量: 全局作用域存储

## 执行模型

### 执行流程

```
1. 初始化虚拟机
   ├─ 加载程序（常数 + 指令）
   ├─ 初始化栈
   └─ 设置 IP = 0

2. 执行循环
   ├─ 检查 IP 是否越界
   ├─ 获取当前指令
   ├─ 执行指令
   │  ├─ 获取操作数
   │  ├─ 执行计算
   │  └─ 存储结果
   ├─ 更新 IP
   ├─ 检查是否返回/停止
   └─ 重复直到程序结束

3. 返回结果
```

### 类型系统

虚拟机实现了**动态类型系统**：

- 运行时类型检查
- 类型转换规则（如 int 到 float 自动转换）
- 强制类型错误报告

### 错误处理

定义了完整的错误类型：

```rust
pub enum VmError {
    StackEmpty,
    InvalidAddress(String),
    TypeError(String),
    RuntimeError(String),
    InstructionPointerOutOfBounds,
    DivisionByZero,
}
```

## 编程示例

### 简单算术

```rust
// 计算: (2 + 3) * 4 - 1 = 19

let mut program = Program::new();
program.add_constant(Value::Integer(2));
program.add_constant(Value::Integer(3));
program.add_constant(Value::Integer(4));
program.add_constant(Value::Integer(1));

program.add_instruction(OpCode::Add {
    lhs: Address::Const(0),
    rhs: Address::Const(1),
    out: Output::Stack(0),
});

program.add_instruction(OpCode::Mul {
    lhs: Address::Stack(0),
    rhs: Address::Const(2),
    out: Output::Stack(1),
});

program.add_instruction(OpCode::Sub {
    lhs: Address::Stack(1),
    rhs: Address::Const(3),
    out: Output::Stack(2),
});

let mut vm = Vm::new(program);
vm.execute().unwrap();
```

### 条件跳转

```rust
// if (10 > 5) { result = 100 } else { result = 200 }

let mut program = Program::new();
program.add_constant(Value::Integer(10));
program.add_constant(Value::Integer(5));
program.add_constant(Value::Integer(100));
program.add_constant(Value::Integer(200));

// 比较: 10 > 5
program.add_instruction(OpCode::Gt {
    lhs: Address::Const(0),
    rhs: Address::Const(1),
    out: Output::Stack(0),
});

// 条件跳转：如果假，跳转到 else 分支
program.add_instruction(OpCode::JumpIfFalse {
    cond: Address::Stack(0),
    offset: 4,
});

// then 分支: result = 100
program.add_instruction(OpCode::Move {
    src: Address::Const(2),
    dst: Output::Stack(1),
});

// 跳转到结束
program.add_instruction(OpCode::Jump { offset: 5 });

// else 分支: result = 200
program.add_instruction(OpCode::Move {
    src: Address::Const(3),
    dst: Output::Stack(1),
});

// 程序结束
program.add_instruction(OpCode::Halt);

let mut vm = Vm::new(program);
vm.execute().unwrap();
```

## 设计特点

### 参考 Rune VM

1. **栈式架构**: 内存高效，适合嵌入式环境
2. **地址寻址**: 灵活的操作数寻址方式
3. **快速常数访问**: 常数池加速常数加载
4. **动态类型**: 运行时类型检查和转换

### 扩展性

架构设计支持未来扩展：

- 新操作码可以简单添加
- 自定义类型系统
- 函数调用支持（栈帧）
- 对象系统支持

## 性能特性

- **O(1) 栈访问**: 直接索引访问
- **O(1) 常数加载**: 直接从常数池加载
- **最小内存开销**: 栈式架构的内存效率
- **快速指令分派**: 枚举匹配的快速分派

## 测试覆盖

项目包含广泛的单元测试：

- 操作码显示和解析
- 栈操作（push/pop/peek）
- 值类型转换
- 算术和比较运算
- 逻辑运算
- 虚拟机执行

运行测试：

```bash
cargo test -p hola_vm
```

## 未来扩展

可能的扩展方向：

1. **函数系统**: 完整的函数定义和调用
2. **局部变量作用域**: 栈帧管理
3. **对象系统**: 自定义类型和方法
4. **异常处理**: try-catch 机制
5. **字节码序列化**: 保存和加载编译后的程序
6. **JIT 编译**: 性能优化
7. **调试器支持**: 代码级调试
