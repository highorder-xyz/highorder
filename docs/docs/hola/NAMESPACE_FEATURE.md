# Hola 语言 Namespace 功能

## 概述

Hola语言现在支持在TypeName中使用namespace，允许多个标识符用点号(.)组合来表示层次化的类型名称。

## 语法规则

```
typeName = upperIdent , { dot , upperIdent } ;
```

这意味着：
- 必须以`upperIdent`开头（大写字母或下划线开头）
- 后面可以跟零个或多个`dot upperIdent`组合

## 使用示例

### 1. 单个标识符
```hola
String {
    value: "hello world"
    length: 11
}
```

### 2. 两部分namespace
```hola
System.String {
    value: "example"
    length: 7
}
```

### 3. 三部分namespace
```hola
System.Collections.Generic.List {
    items: ["item1", "item2", "item3"]
    count: 3
}
```

### 4. 四部分namespace
```hola
Microsoft.AspNetCore.Mvc.Controller {
    name: "HomeController"
    actions: ["Index", "About", "Contact"]
}
```

### 5. 复杂嵌套对象
```hola
MyApp.Models.User {
    id: 1
    name: "John Doe"
    email: "john@example.com"
    profile: {
        firstName: "John"
        lastName: "Doe"
        age: 30
    }
}
```

### 6. 服务配置
```hola
MyApp.Services.AuthService {
    provider: "OAuth2"
    config: {
        clientId: "abc123"
        redirectUri: "https://example.com/callback"
        scopes: ["openid", "profile", "email"]
    }
}
```

## 优势

1. **层次化组织**: 可以更好地组织和管理复杂的类型结构
2. **语义清晰**: 通过namespace可以清楚地表达类型的归属关系
3. **扩展性强**: 支持任意层级的嵌套
4. **向后兼容**: 单个标识符的用法保持不变

## 命名约定

- **推荐使用**: PascalCase命名约定
- **示例**: `MyApp.Models.User`, `System.Collections.Generic.List`
- **避免**: 小写字母开头的标识符

## 语法验证

所有namespace必须：
- 以大写字母或下划线开头
- 每个部分之间用点号(.)分隔
- 不能包含空格或特殊字符

## 示例文件

查看 `examples/namespace_examples.hola` 文件获取更多完整示例。

---

**更新日期**: 2025-12-10  
**版本**: Hola v1.1+  
**兼容性**: 向后兼容现有语法
