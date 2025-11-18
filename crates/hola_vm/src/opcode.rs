//! HOLA VM 操作码定义
//!
//! 操作码是虚拟机执行的基本指令单位。
//! 设计灵感来自 Rune VM，采用栈式架构。

use std::fmt;

/// 操作码地址，表示栈上或寄存器中的位置
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Address {
    /// 栈相对地址（相对于当前栈帧）
    Stack(usize),
    /// 常数池中的索引
    Const(usize),
}

impl fmt::Display for Address {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Address::Stack(idx) => write!(f, "stack[{}]", idx),
            Address::Const(idx) => write!(f, "const[{}]", idx),
        }
    }
}

/// 输出位置，指定指令结果的存储位置
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Output {
    /// 将结果存储到栈上
    Stack(usize),
    /// 丢弃结果
    Discard,
}

impl fmt::Display for Output {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Output::Stack(idx) => write!(f, "stack[{}]", idx),
            Output::Discard => write!(f, "discard"),
        }
    }
}

/// HOLA 虚拟机的操作码
#[derive(Debug, Clone, PartialEq)]
pub enum OpCode {
    // 算术运算
    /// 加法: a + b
    Add {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 减法: a - b
    Sub {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 乘法: a * b
    Mul {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 除法: a / b
    Div {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 模运算: a % b
    Mod {
        lhs: Address,
        rhs: Address,
        out: Output,
    },

    // 比较运算
    /// 相等比较: a == b
    Eq {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 不相等比较: a != b
    Ne {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 小于比较: a < b
    Lt {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 小于等于比较: a <= b
    Le {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 大于比较: a > b
    Gt {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 大于等于比较: a >= b
    Ge {
        lhs: Address,
        rhs: Address,
        out: Output,
    },

    // 逻辑运算
    /// 逻辑与: a && b
    And {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 逻辑或: a || b
    Or {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 逻辑非: !a
    Not {
        addr: Address,
        out: Output,
    },

    // 位运算
    /// 按位与: a & b
    BitwiseAnd {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 按位或: a | b
    BitwiseOr {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 按位异或: a ^ b
    BitwiseXor {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 按位非: ~a
    BitwiseNot {
        addr: Address,
        out: Output,
    },
    /// 左移: a << b
    ShiftLeft {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 右移: a >> b
    ShiftRight {
        lhs: Address,
        rhs: Address,
        out: Output,
    },

    // 对象/哈希表操作
    /// 创建空对象
    ObjectCreate {
        out: Output,
    },
    /// 设置对象字段: obj[key] = value
    ObjectSet {
        object: Address,
        key: Address,
        value: Address,
    },
    /// 获取对象字段: obj[key]
    ObjectGet {
        object: Address,
        key: Address,
        out: Output,
    },

    // 浮点数特殊操作
    /// 幂运算: a ** b (a的b次方)
    FloatPow {
        base: Address,
        exponent: Address,
        out: Output,
    },
    /// 平方根: sqrt(a)
    FloatSqrt {
        addr: Address,
        out: Output,
    },

    // 内存管理操作
    /// 深复制对象/数组
    Clone {
        addr: Address,
        out: Output,
    },
    /// 获取值的类型字符串
    Typeof {
        addr: Address,
        out: Output,
    },

    // 数据移动
    /// 将常数值加载到栈中
    LoadConst {
        index: usize,
        out: Output,
    },
    /// 将值从一个位置复制到另一个位置
    Move {
        src: Address,
        dst: Output,
    },

    // 控制流
    /// 无条件跳转
    Jump {
        offset: usize,
    },
    /// 条件跳转（如果条件为真则跳转）
    JumpIfTrue {
        cond: Address,
        offset: usize,
    },
    /// 条件跳转（如果条件为假则跳转）
    JumpIfFalse {
        cond: Address,
        offset: usize,
    },

    // 函数系统
    /// 加载函数引用
    LoadFn {
        hash: u64,
        out: Output,
    },
    /// 调用函数
    Call {
        func_addr: Address,
        args_count: usize,
        out: Output,
    },
    /// 通过函数指针调用
    CallFn {
        function: Address,
        args_count: usize,
        out: Output,
    },
    /// 相对偏移调用（调用同一单元内的函数）
    CallOffset {
        offset: usize,
        args_count: usize,
        out: Output,
    },
    /// 返回值
    Return {
        value: Option<Address>,
    },
    /// 返回单位值
    ReturnUnit,

    // 数组/集合操作
    /// 创建数组
    MakeArray {
        len: usize,
        out: Output,
    },
    /// 数组索引访问
    IndexGet {
        array: Address,
        index: Address,
        out: Output,
    },
    /// 数组索引设置
    IndexSet {
        array: Address,
        index: Address,
        value: Address,
    },

    // 元组操作
    /// 创建元组
    Tuple {
        addr: Address,
        len: usize,
        out: Output,
    },
    /// 创建单元素元组（优化）
    Tuple1 {
        addr: Address,
        out: Output,
    },
    /// 创建双元素元组（优化）
    Tuple2 {
        addr1: Address,
        addr2: Address,
        out: Output,
    },
    /// 创建三元素元组（优化）
    Tuple3 {
        addr1: Address,
        addr2: Address,
        addr3: Address,
        out: Output,
    },
    /// 从地址获取元组的指定索引
    TupleIndexGetAt {
        addr: Address,
        index: usize,
        out: Output,
    },
    /// 设置元组的指定索引
    TupleIndexSet {
        target: Address,
        index: usize,
        value: Address,
    },

    // 范围操作
    /// 创建范围对象
    Range {
        start: Option<Address>,
        end: Option<Address>,
        inclusive: bool,
        out: Output,
    },

    // 栈优化操作
    /// 复制栈顶元素
    Copy {
        src: Address,
        out: Output,
    },
    /// 丢弃栈元素
    Drop {
        addr: Address,
    },
    /// 交换两个栈元素
    Swap {
        addr1: Address,
        addr2: Address,
    },

    // 字符串处理
    /// 字符串连接
    StrConcat {
        lhs: Address,
        rhs: Address,
        out: Output,
    },
    /// 字符串长度
    StrLen {
        addr: Address,
        out: Output,
    },
    /// 字符串索引获取
    StrIndexGet {
        addr: Address,
        index: Address,
        out: Output,
    },
    /// 字符串切片
    StrSlice {
        addr: Address,
        start: Address,
        end: Address,
        out: Output,
    },
    /// 字符串查找
    StrFind {
        haystack: Address,
        needle: Address,
        out: Output,
    },
    /// 字符串替换
    StrReplace {
        text: Address,
        from: Address,
        to: Address,
        out: Output,
    },

    // 模式匹配
    /// 检查值类型
    TypeCheck {
        addr: Address,
        expected_type: String,
        out: Output,
    },
    /// 模式解构元组
    DestructTuple {
        addr: Address,
        pattern_size: usize,
        out: Output,
    },
    /// 模式匹配分支
    Match {
        value: Address,
        patterns: Vec<String>,
        offsets: Vec<usize>,
        default_offset: Option<usize>,
    },
    /// 检查模式是否匹配
    MatchTest {
        value: Address,
        pattern: String,
        out: Output,
    },

    // 完整的函数调用系统
    /// 推送帐框
    PushFrame {
        params_count: usize,
    },
    /// 出棚帐框
    PopFrame,
    /// 设置本地变量
    SetLocal {
        index: usize,
        value: Address,
    },
    /// 获取本地变量
    GetLocal {
        index: usize,
        out: Output,
    },
    /// 设置全局变量
    SetGlobal {
        name: String,
        value: Address,
    },
    /// 获取全局变量
    GetGlobal {
        name: String,
        out: Output,
    },
    /// 正式函数调用（支持加载参数和返回值）
    FuncCall {
        func_addr: Address,
        args_count: usize,
        out: Output,
    },
    /// 正式函数返回
    FuncReturn {
        value: Option<Address>,
    },

    // 异常处理
    /// 抛出异常
    Throw {
        exception_type: String,
        message: Address,
    },
    /// 异常捕获（设置处理器）
    TryCatch {
        try_offset: usize,
        catch_offset: usize,
        finally_offset: Option<usize>,
    },
    /// 需要处理异常的操作
    GuardException {
        guarded_op: Box<OpCode>,
        catch_offset: usize,
    },
    /// 从异常中执行恢复
    CatchException {
        exception_out: Output,
    },
    /// 清理异常改住
    ClearException,

    // 第 1 阶段：核心缺失操作码
    /// 数值取反: -a
    Neg {
        addr: Address,
        out: Output,
    },
    /// 类型强制转换: a as Type
    As {
        value: Address,
        expected_type: String,
        out: Output,
    },
    /// 类型实例检查: a is Type
    Is {
        value: Address,
        expected_type: String,
        out: Output,
    },
    /// 类型实例否定检查: a is not Type
    IsNot {
        value: Address,
        expected_type: String,
        out: Output,
    },
    /// 错误传播: try value
    Try {
        addr: Address,
        out: Output,
    },

    // 第 2 阶段：OOP 支持
    /// 调用对象关联方法
    CallAssociated {
        instance: Address,
        method_name: String,
        args_count: usize,
        out: Output,
    },
    /// 加载实例方法
    LoadInstanceFn {
        instance: Address,
        method_name: String,
        out: Output,
    },
    /// 结构体构造
    Struct {
        addr: Address,
        struct_name: String,
        field_count: usize,
        out: Output,
    },

    // 第 3 阶段：迭代和高级功能
    /// 迭代器推进
    IterNext {
        iterator_addr: Address,
        jump_offset: usize,
        out: Output,
    },
    /// 闭包构造
    Closure {
        func_hash: u64,
        capture_addr: Address,
        capture_count: usize,
        out: Output,
    },
    /// 闭包环境展开
    Environment {
        tuple_addr: Address,
        expected_count: usize,
        out: Output,
    },
    /// 值格式化
    Format {
        value_addr: Address,
        format_spec: String,
        out: Output,
    },

    // 第 4 阶段：异步支持
    /// 等待 Future 完成
    Await {
        future_addr: Address,
        out: Output,
    },
    /// 生成器 yield
    Yield {
        value_addr: Address,
        out: Output,
    },
    /// 生成器 yield unit
    YieldUnit {
        out: Output,
    },
    /// Future 选择
    Select {
        futures_addr: Address,
        futures_count: usize,
        value_out: Output,
    },
    /// 分配栈空间
    Allocate {
        size: usize,
    },
    /// 释放栈空间
    Pop {
        count: usize,
    },

    // 其他
    /// 无操作
    Nop,
    /// 停止执行
    Halt,
}

impl fmt::Display for OpCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            OpCode::Add { lhs, rhs, out } => {
                write!(f, "add {} + {} => {}", lhs, rhs, out)
            }
            OpCode::Sub { lhs, rhs, out } => {
                write!(f, "sub {} - {} => {}", lhs, rhs, out)
            }
            OpCode::Mul { lhs, rhs, out } => {
                write!(f, "mul {} * {} => {}", lhs, rhs, out)
            }
            OpCode::Div { lhs, rhs, out } => {
                write!(f, "div {} / {} => {}", lhs, rhs, out)
            }
            OpCode::Mod { lhs, rhs, out } => {
                write!(f, "mod {} % {} => {}", lhs, rhs, out)
            }
            OpCode::Eq { lhs, rhs, out } => {
                write!(f, "eq {} == {} => {}", lhs, rhs, out)
            }
            OpCode::Ne { lhs, rhs, out } => {
                write!(f, "ne {} != {} => {}", lhs, rhs, out)
            }
            OpCode::Lt { lhs, rhs, out } => {
                write!(f, "lt {} < {} => {}", lhs, rhs, out)
            }
            OpCode::Le { lhs, rhs, out } => {
                write!(f, "le {} <= {} => {}", lhs, rhs, out)
            }
            OpCode::Gt { lhs, rhs, out } => {
                write!(f, "gt {} > {} => {}", lhs, rhs, out)
            }
            OpCode::Ge { lhs, rhs, out } => {
                write!(f, "ge {} >= {} => {}", lhs, rhs, out)
            }
            OpCode::And { lhs, rhs, out } => {
                write!(f, "and {} && {} => {}", lhs, rhs, out)
            }
            OpCode::Or { lhs, rhs, out } => {
                write!(f, "or {} || {} => {}", lhs, rhs, out)
            }
            OpCode::Not { addr, out } => {
                write!(f, "not !{} => {}", addr, out)
            }
            OpCode::BitwiseAnd { lhs, rhs, out } => {
                write!(f, "bitwise_and {} & {} => {}", lhs, rhs, out)
            }
            OpCode::BitwiseOr { lhs, rhs, out } => {
                write!(f, "bitwise_or {} | {} => {}", lhs, rhs, out)
            }
            OpCode::BitwiseXor { lhs, rhs, out } => {
                write!(f, "bitwise_xor {} ^ {} => {}", lhs, rhs, out)
            }
            OpCode::BitwiseNot { addr, out } => {
                write!(f, "bitwise_not ~{} => {}", addr, out)
            }
            OpCode::ShiftLeft { lhs, rhs, out } => {
                write!(f, "shift_left {} << {} => {}", lhs, rhs, out)
            }
            OpCode::ShiftRight { lhs, rhs, out } => {
                write!(f, "shift_right {} >> {} => {}", lhs, rhs, out)
            }
            OpCode::ObjectCreate { out } => {
                write!(f, "object_create => {}", out)
            }
            OpCode::ObjectSet { object, key, value } => {
                write!(f, "object_set {}[{}] = {}", object, key, value)
            }
            OpCode::ObjectGet { object, key, out } => {
                write!(f, "object_get {}[{}] => {}", object, key, out)
            }
            OpCode::FloatPow { base, exponent, out } => {
                write!(f, "float_pow {} ** {} => {}", base, exponent, out)
            }
            OpCode::FloatSqrt { addr, out } => {
                write!(f, "float_sqrt sqrt({}) => {}", addr, out)
            }
            OpCode::Clone { addr, out } => {
                write!(f, "clone {} => {}", addr, out)
            }
            OpCode::Typeof { addr, out } => {
                write!(f, "typeof {} => {}", addr, out)
            }
            OpCode::LoadConst { index, out } => {
                write!(f, "load_const[{}] => {}", index, out)
            }
            OpCode::Move { src, dst } => {
                write!(f, "move {} => {}", src, dst)
            }
            OpCode::Jump { offset } => {
                write!(f, "jump to offset {}", offset)
            }
            OpCode::JumpIfTrue { cond, offset } => {
                write!(f, "jump_if_true {} to offset {}", cond, offset)
            }
            OpCode::JumpIfFalse { cond, offset } => {
                write!(f, "jump_if_false {} to offset {}", cond, offset)
            }
            OpCode::Call { func_addr, args_count, out } => {
                write!(f, "call {}({} args) => {}", func_addr, args_count, out)
            }
            OpCode::Return { value } => {
                if let Some(addr) = value {
                    write!(f, "return {}", addr)
                } else {
                    write!(f, "return")
                }
            }
            OpCode::MakeArray { len, out } => {
                write!(f, "make_array[{}] => {}", len, out)
            }
            OpCode::IndexGet { array, index, out } => {
                write!(f, "index_get {}[{}] => {}", array, index, out)
            }
            OpCode::IndexSet { array, index, value } => {
                write!(f, "index_set {}[{}] = {}", array, index, value)
            }
            OpCode::Allocate { size } => {
                write!(f, "allocate {}", size)
            }
            OpCode::Pop { count } => {
                write!(f, "pop {}", count)
            }
            OpCode::LoadFn { hash, out } => {
                write!(f, "load_fn[{:x}] => {}", hash, out)
            }
            OpCode::CallFn { function, args_count, out } => {
                write!(f, "call_fn {}({} args) => {}", function, args_count, out)
            }
            OpCode::CallOffset { offset, args_count, out } => {
                write!(f, "call_offset[{}]({} args) => {}", offset, args_count, out)
            }
            OpCode::ReturnUnit => {
                write!(f, "return_unit")
            }
            OpCode::Tuple { addr, len, out } => {
                write!(f, "tuple {}({} elems) => {}", addr, len, out)
            }
            OpCode::Tuple1 { addr, out } => {
                write!(f, "tuple1 {} => {}", addr, out)
            }
            OpCode::Tuple2 { addr1, addr2, out } => {
                write!(f, "tuple2 {}, {} => {}", addr1, addr2, out)
            }
            OpCode::Tuple3 { addr1, addr2, addr3, out } => {
                write!(f, "tuple3 {}, {}, {} => {}", addr1, addr2, addr3, out)
            }
            OpCode::TupleIndexGetAt { addr, index, out } => {
                write!(f, "tuple_index_get_at {}[{}] => {}", addr, index, out)
            }
            OpCode::TupleIndexSet { target, index, value } => {
                write!(f, "tuple_index_set {}[{}] = {}", target, index, value)
            }
            OpCode::Range { start, end, inclusive, out } => {
                let start_str = start.map(|a| a.to_string()).unwrap_or("_".to_string());
                let end_str = end.map(|a| a.to_string()).unwrap_or("_".to_string());
                let op = if *inclusive { "..=" } else { ".." };
                write!(f, "range {}{}{}  => {}", start_str, op, end_str, out)
            }
            OpCode::Copy { src, out } => {
                write!(f, "copy {} => {}", src, out)
            }
            OpCode::Drop { addr } => {
                write!(f, "drop {}", addr)
            }
            OpCode::Swap { addr1, addr2 } => {
                write!(f, "swap {} <-> {}", addr1, addr2)
            }
            OpCode::StrConcat { lhs, rhs, out } => {
                write!(f, "str_concat {} + {} => {}", lhs, rhs, out)
            }
            OpCode::StrLen { addr, out } => {
                write!(f, "str_len {} => {}", addr, out)
            }
            OpCode::StrIndexGet { addr, index, out } => {
                write!(f, "str_index_get {}[{}] => {}", addr, index, out)
            }
            OpCode::StrSlice { addr, start, end, out } => {
                write!(f, "str_slice {}[{}:{}] => {}", addr, start, end, out)
            }
            OpCode::StrFind { haystack, needle, out } => {
                write!(f, "str_find {} in {} => {}", needle, haystack, out)
            }
            OpCode::StrReplace { text, from, to, out } => {
                write!(f, "str_replace {} replace {} with {} => {}", text, from, to, out)
            }
            OpCode::TypeCheck { addr, expected_type, out } => {
                write!(f, "type_check {} : {} => {}", addr, expected_type, out)
            }
            OpCode::DestructTuple { addr, pattern_size, out } => {
                write!(f, "destruct_tuple {}({} items) => {}", addr, pattern_size, out)
            }
            OpCode::Match { value, patterns, offsets, default_offset } => {
                write!(f, "match {} [patterns: {:?}] offsets: {:?} default: {:?}", value, patterns, offsets, default_offset)
            }
            OpCode::MatchTest { value, pattern, out } => {
                write!(f, "match_test {} ? {} => {}", value, pattern, out)
            }
            OpCode::PushFrame { params_count } => {
                write!(f, "push_frame [params: {}]", params_count)
            }
            OpCode::PopFrame => {
                write!(f, "pop_frame")
            }
            OpCode::SetLocal { index, value } => {
                write!(f, "set_local[{}] = {}", index, value)
            }
            OpCode::GetLocal { index, out } => {
                write!(f, "get_local[{}] => {}", index, out)
            }
            OpCode::SetGlobal { name, value } => {
                write!(f, "set_global[{}] = {}", name, value)
            }
            OpCode::GetGlobal { name, out } => {
                write!(f, "get_global[{}] => {}", name, out)
            }
            OpCode::FuncCall { func_addr, args_count, out } => {
                write!(f, "func_call {}({} args) => {}", func_addr, args_count, out)
            }
            OpCode::FuncReturn { value } => {
                if let Some(addr) = value {
                    write!(f, "func_return {}", addr)
                } else {
                    write!(f, "func_return")
                }
            }
            OpCode::Throw { exception_type, message } => {
                write!(f, "throw {} {}", exception_type, message)
            }
            OpCode::TryCatch { try_offset, catch_offset, finally_offset } => {
                write!(f, "try_catch try@{} catch@{} finally@{:?}", try_offset, catch_offset, finally_offset)
            }
            OpCode::GuardException { guarded_op, catch_offset } => {
                write!(f, "guard_exception [{}] catch@{}", guarded_op, catch_offset)
            }
            OpCode::CatchException { exception_out } => {
                write!(f, "catch_exception => {}", exception_out)
            }
            OpCode::ClearException => {
                write!(f, "clear_exception")
            }
            OpCode::Neg { addr, out } => {
                write!(f, "neg -{} => {}", addr, out)
            }
            OpCode::As { value, expected_type, out } => {
                write!(f, "as {} as {} => {}", value, expected_type, out)
            }
            OpCode::Is { value, expected_type, out } => {
                write!(f, "is {} is {} => {}", value, expected_type, out)
            }
            OpCode::IsNot { value, expected_type, out } => {
                write!(f, "is_not {} is not {} => {}", value, expected_type, out)
            }
            OpCode::Try { addr, out } => {
                write!(f, "try {} => {}", addr, out)
            }
            OpCode::CallAssociated { instance, method_name, args_count, out } => {
                write!(f, "call_associated {}.{}({} args) => {}", instance, method_name, args_count, out)
            }
            OpCode::LoadInstanceFn { instance, method_name, out } => {
                write!(f, "load_instance_fn {}.{} => {}", instance, method_name, out)
            }
            OpCode::Struct { addr, struct_name, field_count, out } => {
                write!(f, "struct {} ({} fields) => {}", struct_name, field_count, out)
            }
            OpCode::IterNext { iterator_addr, jump_offset, out } => {
                write!(f, "iter_next {} jump@{} => {}", iterator_addr, jump_offset, out)
            }
            OpCode::Closure { func_hash, capture_addr, capture_count, out } => {
                write!(f, "closure fn({:x}) capture {}({} items) => {}", func_hash, capture_addr, capture_count, out)
            }
            OpCode::Environment { tuple_addr, expected_count, out } => {
                write!(f, "environment {} ({} items) => {}", tuple_addr, expected_count, out)
            }
            OpCode::Format { value_addr, format_spec, out } => {
                write!(f, "format {} spec({}) => {}", value_addr, format_spec, out)
            }
            OpCode::Await { future_addr, out } => {
                write!(f, "await {} => {}", future_addr, out)
            }
            OpCode::Yield { value_addr, out } => {
                write!(f, "yield {} => {}", value_addr, out)
            }
            OpCode::YieldUnit { out } => {
                write!(f, "yield_unit => {}", out)
            }
            OpCode::Select { futures_addr, futures_count, value_out } => {
                write!(f, "select {} ({} futures) => {}", futures_addr, futures_count, value_out)
            }
            OpCode::Nop => write!(f, "nop"),
            OpCode::Halt => write!(f, "halt"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_address_display() {
        let stack_addr = Address::Stack(0);
        assert_eq!(stack_addr.to_string(), "stack[0]");

        let const_addr = Address::Const(5);
        assert_eq!(const_addr.to_string(), "const[5]");
    }

    #[test]
    fn test_output_display() {
        let stack_out = Output::Stack(1);
        assert_eq!(stack_out.to_string(), "stack[1]");

        let discard = Output::Discard;
        assert_eq!(discard.to_string(), "discard");
    }

    #[test]
    fn test_opcode_display() {
        let add = OpCode::Add {
            lhs: Address::Stack(0),
            rhs: Address::Stack(1),
            out: Output::Stack(2),
        };
        assert_eq!(add.to_string(), "add stack[0] + stack[1] => stack[2]");
    }
}
