# Hola Python实现 - 设计规范文档

## 1. 概述

Hola是一个声明式配置语言，支持对象、表达式、列表等结构。本文档描述使用Python实现Hola语言的parser、compiler和VM的完整规范。

## 2. 语言特性

### 2.1 核心语法

- **对象定义**: `TypeName { properties }`
- **匿名对象**: `{ properties }`
- **命名空间**: `System.Collections.Generic.List`
- **子对象**: 对象内嵌套其他对象
- **属性**: `key: value`
- **列表**: `[item1, item2, ...]`
- **表达式**: `{{ expression }}`

### 2.2 值类型

- **null**: `null`
- **布尔**: `true`, `false`
- **字符串**: `"text"`, `'text'` (支持转义)
- **数字**: `123`, `99.9`, `1_000_000`
- **颜色**: `#FF0000`, `#abc`, `#RRGGBBAA`
- **列表**: `[1, 2, 3]`
- **对象**: `Object { name: "value" }`

### 2.3 表达式语法

支持完整的表达式语法，包括：

- **算术运算**: `+`, `-`, `*`, `/`
- **比较运算**: `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`
- **逻辑运算**: `&&`, `||`, `!`
- **成员访问**: `obj.prop`, `list[index]`
- **函数调用**: `func(arg1, arg2)`
- **分组**: `(expression)`

### 2.4 分隔符

- 逗号 `,`
- 换行 `\n`
- 列表支持空位: `[1,,3]` (中间的逗号表示null)

### 2.5 注释

- 单行注释: `// comment`
- 块注释: `/* comment */` (仅支持在默认模式，不支持表达式块内)

## 3. 架构设计

### 3.1 模块组成

```
hola/
├── __init__.py          # 公共接口
├── tokenizer.py         # 词法分析器
├── parser.py            # 语法分析器
├── expression_parser.py # 表达式解析器
├── ast.py               # AST定义
├── compiler.py          # 编译器 (AST -> JSON)
├── vm.py                # 虚拟机 (表达式求值)
├── error.py             # 错误处理
└── tests/
    ├── test_tokenizer.py
    ├── test_parser.py
    ├── test_compiler.py
    └── test_vm.py
```

### 3.2 数据流

```
源代码 -> Tokenizer -> Tokens -> Parser -> AST -> Compiler -> JSON/VM
                                                      |
                                                      v
                                                 表达式求值
```

## 4. 模块详细设计

### 4.1 Tokenizer (tokenizer.py)

**职责**: 将源代码转换为token流

**Token定义**:
```python
@dataclass
class Token:
    kind: TokenKind
    value: str
    position: Position
```

**TokenKind枚举**:
- 结构token: Identifier, PropertyName, StringLiteral, NumberLiteral, ColorLiteral, BoolLiteral, NullLiteral
- 分隔符: LBrace, RBrace, LBracket, RBracket, Colon, Comma, LineBreak
- 运算符: Plus, Minus, Star, Slash, Bang, Equal, LParen, RParen, Dot
- 复合运算符: BangEqual, EqualEqual, Greater, GreaterEqual, Less, LessEqual, AndAnd, OrOr
- 表达式标记: LBraceLBrace, RBraceRBrace
- 其他: Comment, Eof, Unknown

**状态机**:
- Default模式: 解析对象结构
- InExpression模式: 解析表达式块内的内容

**关键方法**:
- `tokenize(source: str) -> List[Token]`
- `read_string(quote: char) -> Token`
- `read_number() -> Token`
- `read_identifier() -> Token`
- `read_color() -> Token`

### 4.2 AST定义 (ast.py)

**核心节点**:
```python
@dataclass
class AstRoot:
    objects: List[ObjectNode]

@dataclass
class ObjectNode:
    name: str  # 类型名，匿名对象为空字符串
    properties: Dict[str, PropertyValue]
    children: List[ObjectNode]

class PropertyValue:
    Literal(LiteralKind)
    List(List[PropertyValue])
    Object(ObjectNode)
    Expression(Expr)

class LiteralKind:
    String(str)
    Number(Int | Float)
    Color(str)
    Bool(bool)
    Null
```

**表达式AST**:
```python
class Expr:
    Binary(Expr, BinaryOperator, Expr)
    Logical(Expr, LogicalOperator, Expr)
    Unary(UnaryOperator, Expr)
    Variable(str)
    Call(Expr, List[Expr])
    Get(Expr, str)
    Literal(LiteralKind)
    Grouping(Expr)
    List(List[Expr])
    ListGet(Expr, Expr)
```

### 4.3 Parser (parser.py)

**职责**: 解析对象结构和属性

**关键方法**:
- `parse(tokens: List[Token]) -> AstRoot`
- `parse_object() -> ObjectNode`
- `parse_property() -> Tuple[str, PropertyValue]`
- `parse_value() -> PropertyValue`
- `parse_list() -> PropertyValue`
- `parse_expression_block() -> PropertyValue`

**解析规则**:
1. 对象名: 可选的大写标识符，支持点分隔命名空间
2. 对象体: 属性和子对象的混合列表
3. 属性: 键名 + 冒号 + 值
4. 值: 字面量、列表、对象或表达式块

### 4.4 Expression Parser (expression_parser.py)

**职责**: 使用Pratt解析器解析表达式

**优先级** (从低到高):
1. Assignment (=)
2. Or (||)
3. And (&&)
4. Equality (==, !=)
5. Comparison (<, <=, >, >=, in)
6. Term (+, -)
7. Factor (*, /)
8. Unary (!, -)
9. Call (., ())
10. Index ([])
11. Primary

**关键方法**:
- `parse_expression(tokens: List[Token]) -> Expr`
- `parse_prefix() -> Expr`
- `parse_infix(left: Expr) -> Expr`
- `parse_get_expression(left: Expr) -> Expr`
- `parse_call_expression(left: Expr) -> Expr`
- `parse_list_get(left: Expr) -> Expr`

### 4.5 Compiler (compiler.py)

**职责**: 将AST编译为JSON格式

**输出格式**:
```json
{
  "objects": [
    {
      "type": "Page",
      "properties": {
        "title": "Hello"
      },
      "children": []
    }
  ]
}
```

**表达式处理**:
- 字面量: 直接转换为JSON值
- 表达式: 保留为AST结构或字符串表示

**关键方法**:
- `compile(ast: AstRoot) -> dict`
- `compile_object(node: ObjectNode) -> dict`
- `compile_property_value(value: PropertyValue) -> Any`
- `compile_expression(expr: Expr) -> dict`

### 4.6 VM (vm.py)

**职责**: 执行表达式求值

**设计理念**: 基于栈的虚拟机，支持动态类型

**Value类型**:
```python
class Value:
    Integer(int)
    Float(float)
    String(str)
    Bool(bool)
    Null
    List(List[Value])
    Object(Dict[str, Value])
    Function(Callable)
```

**操作码**:
- 算术: Add, Sub, Mul, Div
- 比较: Eq, Ne, Lt, Le, Gt, Ge
- 逻辑: And, Or, Not
- 访问: GetProp, GetIndex, Call
- 栈操作: Push, Pop, LoadConst

**关键方法**:
- `evaluate(expr: Expr, context: Dict[str, Any]) -> Value`
- `eval_binary(op: BinaryOperator, left: Value, right: Value) -> Value`
- `eval_unary(op: UnaryOperator, operand: Value) -> Value`
- `eval_call(func: Value, args: List[Value]) -> Value`

**上下文**:
- 变量作用域
- 内置函数库
- 类型转换规则

## 5. 错误处理

### 5.1 错误类型

```python
class HolaError(Exception):
    pass

class TokenizeError(HolaError):
    pass

class ParseError(HolaError):
    pass

class CompileError(HolaError):
    pass

class RuntimeError(HolaError):
    pass
```

### 5.2 错误信息格式

包含位置信息、错误类型和详细描述:
```
Error at line 5, column 10: ParseError
Expected ':' after property name, found ','
```

## 6. 测试策略

### 6.1 单元测试

- **Tokenizer测试**: 各种token类型的识别
- **Parser测试**: 各种语法结构的解析
- **Compiler测试**: AST到JSON的转换
- **VM测试**: 表达式求值的正确性

### 6.2 集成测试

- **端到端测试**: 从源代码到最终结果的完整流程
- **示例测试**: 验证官方示例的正确解析

### 6.3 边界测试

- 空输入
- 错误语法
- 深度嵌套
- 大型文件

## 7. 性能考虑

- 使用生成器处理token流，避免内存爆炸
- 缓存AST编译结果
- VM使用栈结构优化求值
- 避免不必要的字符串拷贝

## 8. 兼容性

- Python 3.11+
- 与Rust实现保持相同的AST结构
- 表达式求值结果与Rust VM一致

## 9. 未来扩展

- 支持字节码序列化
- 添加调试器支持
- 实现REPL环境
- 支持模块导入
- 添加标准库函数
