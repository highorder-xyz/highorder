# Hola 语言规范（草案）

> 说明：本规范基于当前 Hola 编译器实现（`components/hola-compiler/src/index.js`）以及示例 `examples/hellworld/.../main.hola` 总结而来，只描述已经被实现且在示例中使用的语法特性。

## 1. 基本约定

- **文件扩展名**：`.hola`
- **编码**：UTF-8
- **结构**：一个 Hola 文件由一个或多个「对象（Object）」构成，例如：

```hola
Modal {
    name: "hello-world"
    title: "Hello Hola"
}

Page {
    route: "/"
}
```

- **大小写**：
  - 对象名（如 `Modal`、`Page`、`Column` 等）区分大小写，通常首字母大写。
  - 属性名（如 `name`、`title`、`route`、`text` 等）区分大小写，通常首字母小写。

- **换行与逗号**：
  - 属性和子对象通常各占一行。
  - 属性和列表元素可以通过换行或逗号分隔，编译器会将换行和逗号都视作分隔符。

## 2. 基本数据类型

Hola 支持以下基础数据类型，对应到内部的 AST 节点类型：

1. **Null**
   - 关键字：`null`
   - 示例：

   ```hola
   foo: null
   ```

2. **布尔（Bool）**
   - 关键字：`true` / `false`
   - 示例：

   ```hola
   trigger: false
   visible: true
   ```

3. **字符串（String）**
   - 使用单引号 `'` 或双引号 `"` 包裹。
   - 支持常见转义字符：`\n`、`\r`、`\t`、`\v`、`\b`、`\f`、`\a` 等。
   - 示例：

   ```hola
   title: "Hello Hola"
   text: 'This is a Modal. Click OK to close.'
   ```

4. **数字（Number）**
   - 支持整数与小数。
   - 数字内部允许使用下划线 `_` 作为分隔符（编译时会被忽略）。
   - 示例：

   ```hola
   initial_value: 100
   price: 99.9
   big_number: 1_000_000
   ```

5. **对象（Object）**
   - 见后文「对象」章节。

6. **列表（List）**
   - 见后文「数组 / 列表」章节。

## 3. 注释

- 使用 `//` 开头的单行注释。
- 从 `//` 到本行末尾的内容会被忽略。

```hola
// 这是一个 Modal 定义
Modal {
    name: "hello-world" // 行尾注释也是允许的
}
```

> 当前实现中没有多行注释语法。

## 4. 对象（Object）

### 4.1 对象定义语法

对象是 Hola 文件的核心构成单元，语法为：

```hola
ObjectName {
    property1: value1
    property2: value2

    SubObjectName {
        // 子对象定义
    }
}
```

- **对象名（`ObjectName`）**：
  - 语法上是一个标识符（首字符为字母或下划线，后续可以包含字母、数字或下划线）。
  - 不同对象名在运行时对应不同的语义，由 HighOrder/Hola 运行时定义。
  - 示例中包含：`Modal`、`Page`、`Column`、`PlainText`、`Button`、`ShowModal` 等。

- **花括号**：
  - 左花括号 `{` 写在对象名之后。
  - 右花括号 `}` 单独成行或位于最后一条属性/子对象之后。

### 4.2 对象属性（Properties）

属性语法：

```hola
property_name: value
```

- **属性名**：
  - 首字符为小写字母或下划线，后续可为字母、数字或下划线。
  - 在语法分析时，会被识别为 `PropertyName` 类型。

- **属性值 `value`**：
  可以是：

  - 基本字面量：`null`、`true`、`false`、字符串、数字
  - 列表：`[ ... ]`
  - 子对象：`ObjectName { ... }` 或匿名对象 `{ ... }`

示例（节选自 `main.hola`）：

```hola
Modal {
    name: "hello-world"
    title: "Hello Hola"
    confirm: {
        text: "OK"
        trigger: false
    }
}
```

这里：

- `name`、`title`、`confirm` 为属性名。
- `confirm` 的属性值是一个匿名对象 `{ ... }`，内部再次包含 `text`、`trigger` 属性。

### 4.3 子对象（Children）

对象内部除了属性以外，还可以包含子对象：

```hola
Page {
    route: "/"

    Column {
        PlainText {
            text: "Hello Hol"
        }
        Button {
            text: "hello"
        }
    }
}
```

在语法上：

- 属性和子对象可以混合出现。
- 编译器会根据当前 token 是 `PropertyName/字符串` 还是 `Identifier/LBrace` 来区分「属性」和「子对象」。

## 5. 数组 / 列表（List）

列表语法使用方括号 `[...]`：

```hola
items: [
    "a",
    "b",
    "c"
]
``;

- 列表元素之间可以用逗号 `,` 或换行分隔。
- 列表元素本身可以是任意合法值：字面量、对象、嵌套列表等。
- 空位（例如连续的逗号）会被视为 `null` 元素。

示例：

```hola
values: [1, 2, 3]
widgets: [
    PlainText { text: "A" },
    PlainText { text: "B" },
]
```

## 6. 标识符与关键字

- **关键字**：`null`、`true`、`false` 被识别为特殊字面量。
- **属性名（PropertyName）**：
  - 以小写字母开头的标识符，在作为属性名使用时被解析为 `PropertyName`。

- **标识符（Identifier）**：
  - 以大写字母或下划线开头，一般用于对象名，如 `Modal`、`Page`。

命名规则（正则形式）：

- 标识符首字符：`[A-Za-z_]`
- 后续字符：`[A-Za-z0-9_]*`

## 7. 空白与格式

- 空格、制表符等空白字符在大多数位置会被忽略，用于排版和缩进。
- 换行符 `\n` 在某些语境中作为分隔符（类似逗号）。
- 花括号、方括号与冒号周边的空格不是语法必须，但推荐保持统一风格，例如：

```hola
Column {
    style: {
        justify: "center"
    }
}
```

在示例 `main.hola` 中，也允许：

```hola
style: {
    justify:"center"
}
```

## 8. 示例：Hello World

示例文件 `examples/hellworld/APP_AP789DPITC1SSUD4/app/main.hola`：

```hola
Modal {
    name: "hello-world"
    title: "Hello Hola"
    confirm: {
        text: "OK"
        trigger: false
    }
    PlainText {
        text: "This is a Modal. Click OK to close."
    }
}

Page {
    route: "/"

    Column {
        style: {
            justify:"center"
        }
        PlainText {
            text: "Hello Hol"
        }
        Button {
            text: "hello"
            events: {
                click: ShowModal {
                    name: "hello-world"
                }
            }
        }
    }
}
```

这个示例展示了：

- 顶层存在两个对象：`Modal` 与 `Page`。
- 对象中包含：
  - 简单属性（`name`、`title`、`route`、`text` 等）。
  - 属性值为匿名对象（`confirm`、`style`、`events`）。
  - 子对象（`PlainText`、`Button`、`Column` 等）。
- 通过 `events` 属性中的 `click: ShowModal { ... }`，将界面事件与动作对象关联。

## 9. 与 HighOrder 的关系

- Hola 语言本身只定义**结构和语法**（对象、属性、列表、字面量等）。
- 各种对象名（如 `Page`、`Modal`、`Button` 等）以及属性含义，由 HighOrder 运行时和配置模型定义。
- 编写 Hola 文件时：
  - 语法需符合本规范；
  - 语义需遵守 HighOrder 提供的对象与属性文档。

---

本规范是根据当前代码实现整理的「草案版」，未来如有语法扩展或编译器行为变更，应同步更新本文件。
