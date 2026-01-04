# Hola语言Python实现

## 概述

这是Hola语言的完整Python实现，包括parser、compiler和VM。实现基于PEG语法定义，与Rust实现保持兼容。

## 项目结构

```
hola/
├── __init__.py           # 公共接口
├── tokenizer.py          # 词法分析器
├── parser.py             # 语法分析器
├── expression_parser.py  # 表达式解析器
├── hola_ast.py           # AST定义
├── compiler.py           # 编译器
├── vm.py                 # 虚拟机
├── error.py              # 错误处理
├── SPEC.md               # 设计规范文档
├── tests/
│   └── test_hola.py      # 验证测试
└── README.md             # 本文档
```

## 功能特性

### 已实现的核心功能

- ✅ **Tokenizer** - 词法分析
  - 支持所有token类型（标识符、字面量、运算符等）
  - 状态机处理默认模式和表达式模式
  - 支持注释（单行和块注释）

- ✅ **Parser** - 语法分析
  - 对象定义和嵌套
  - 属性和子对象
  - 列表和空位支持
  - 命名空间支持（如 `System.Collections.Generic.List`）
  - 匿名对象

- ✅ **Expression Parser** - 表达式解析
  - Pratt解析器实现
  - 运算符优先级处理
  - 算术运算：`+`, `-`, `*`, `/`
  - 比较运算：`==`, `!=`, `<`, `<=`, `>`, `>=`, `in`
  - 逻辑运算：`&&`, `||`, `!`
  - 成员访问：`obj.prop`
  - 函数调用：`func(arg1, arg2)`
  - 列表索引：`list[index]`
  - 分组表达式：`(expr)`

- ✅ **Compiler** - 编译器
  - AST到JSON格式转换
  - 表达式序列化
  - 保留完整结构信息

- ✅ **VM** - 虚拟机
  - 表达式求值
  - 动态类型系统
  - 内置函数：`len`, `abs`, `min`, `max`, `str`, `int`, `float`, `bool`
  - 变量上下文支持
  - 短路求值（逻辑运算）

## 使用方法

### 基本使用

```python
from hola import compile

# 编译Hola代码
source = '''
Page {
    title: "Hello World"
    route: "/home"
}
'''

result = compile(source)
print(result)
```

输出：
```json
{
  "objects": [
    {
      "type": "Page",
      "properties": {
        "title": "Hello World",
        "route": "/home"
      },
      "children": []
    }
  ]
}
```

### 表达式求值

```python
from hola import compile, VM

# 编译包含表达式的代码
source = '''
Calculator {
    sum: {{ a + b }}
    product: {{ x * y }}
}
'''

result = compile(source)

# 获取表达式并求值
expr = result['objects'][0]['properties']['sum']
vm = VM({'a': 10, 'b': 20})
value = vm.evaluate(expr)
print(value)  # 输出: 30
```

### 直接使用组件

```python
from hola import Tokenizer, Parser, Compiler, VM

# 1. 词法分析
tokenizer = Tokenizer(source)
tokens = tokenizer.tokenize()

# 2. 语法分析
parser = Parser(tokens)
ast = parser.parse()

# 3. 编译
compiler = Compiler()
json_result = compiler.compile(ast)

# 4. 表达式求值
vm = VM(context)
result = vm.evaluate(expression)
```

## 支持的语言特性

### 对象定义

```hola
Page {
    title: "Hello"
    route: "/home"
}
```

### 嵌套对象

```hola
Page {
    Column {
        PlainText {
            text: "Hello"
        }
        
        Button {
            text: "Click"
        }
    }
}
```

### 列表

```hola
Object {
    values: [1, 2, 3]
    mixed: [true, "text", 3.14]
    with_holes: [1,,3]  # 包含null元素
}
```

### 表达式

```hola
Calculator {
    sum: {{ a + b }}
    condition: {{ x > 10 && y < 20 }}
    method_call: {{ user.getProfile() }}
    nested_property: {{ app.settings.theme }}
    negation: {{ !isActive }}
}
```

### 命名空间

```hola
System.Collections.Generic.List {
    count: 0
}
```

### 注释

```hola
// 单行注释
Page {
    title: "Test"  // 行尾注释
}

/* 块注释 */
```

## 测试

运行完整测试套件：

```bash
cd /home/ubuntu/workspace/highorder/server/highorder/hola
PYTHONPATH=/home/ubuntu/workspace/highorder/server/highorder python tests/test_hola.py
```

测试覆盖：
- Tokenizer测试
- Parser测试
- Expression Parser测试
- Compiler测试
- VM测试
- 复杂示例测试
- 边界情况测试

## 设计文档

详细的设计规范请参考 [SPEC.md](SPEC.md)，包含：
- 语言特性描述
- 架构设计
- 模块详细设计
- 错误处理
- 测试策略
- 性能考虑

## 与Rust实现的兼容性

本Python实现与Rust实现保持兼容：
- 相同的AST结构
- 相同的语法规则
- 相同的表达式求值结果
- 支持相同的语言特性

## 示例

### 完整示例

```python
from hola import compile

source = '''
Page {
    route: "/demo"
    
    Column {
        PlainText {
            text: "Hello"
        }
        
        Button {
            text: "Click"
            events: {
                click: ShowModal { name: "hello-world" }
            }
        }
    }
}
'''

result = compile(source)
print(result)
```

### 表达式示例

```python
from hola import compile, VM

source = '''
Object {
    sum: {{ a + b }}
    condition: {{ x > 10 && y < 20 }}
    length: {{ len(items) }}
}
'''

result = compile(source)

# 求值表达式
vm = VM({'a': 10, 'b': 20, 'x': 15, 'y': 18, 'items': [1, 2, 3]})
sum_expr = result['objects'][0]['properties']['sum']
print(vm.evaluate(sum_expr))  # 输出: 30
```

## 性能说明

- 使用生成器处理token流，避免内存爆炸
- 缓存AST编译结果
- VM使用栈结构优化求值
- 避免不必要的字符串拷贝

## 版本信息

- 版本：0.1.0
- Python要求：>= 3.11
- 状态：所有核心功能已实现并通过测试

## 未来扩展

- 字节码序列化
- 调试器支持
- REPL环境
- 模块导入
- 标准库函数扩展
- 性能优化

## 许可证

与项目整体保持一致。
