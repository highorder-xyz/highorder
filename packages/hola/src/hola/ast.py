"""
Hola语言AST定义
"""

from dataclasses import dataclass, field
from typing import Dict, List, Union, Any
from enum import Enum, auto


# ========== 字面量类型 ==========

class NumberValue:
    """数字值"""
    
    def __init__(self, value: Union[int, float]):
        if isinstance(value, int):
            self.value = value
            self.is_int = True
        else:
            self.value = value
            self.is_int = False
    
    def __eq__(self, other):
        if not isinstance(other, NumberValue):
            return False
        return self.value == other.value
    
    def __repr__(self):
        return f"NumberValue({self.value})"
    
    def __hash__(self):
        return hash(self.value)


class LiteralKind:
    """字面量类型"""
    
    def __init__(self, value: Any):
        self.value = value
        
        # 判断具体类型
        if isinstance(value, str) and value.startswith('#'):
            self.type = 'color'
        elif isinstance(value, bool):
            self.type = 'bool'
        elif value is None:
            self.type = 'null'
        elif isinstance(value, NumberValue):
            self.type = 'number'
        elif isinstance(value, str):
            self.type = 'string'
        else:
            self.type = 'unknown'
    
    def __eq__(self, other):
        if not isinstance(other, LiteralKind):
            return False
        return self.value == other.value
    
    def __repr__(self):
        return f"LiteralKind.{self.type.title()}({repr(self.value)})"
    
    def __hash__(self):
        return hash((self.type, str(self.value)))


# ========== 表达式AST ==========

class BinaryOperator(Enum):
    """二元运算符"""
    Add = auto()
    Subtract = auto()
    Multiply = auto()
    Divide = auto()
    Equal = auto()
    NotEqual = auto()
    Less = auto()
    LessEqual = auto()
    Greater = auto()
    GreaterEqual = auto()
    
    def __str__(self):
        return {
            BinaryOperator.Add: '+',
            BinaryOperator.Subtract: '-',
            BinaryOperator.Multiply: '*',
            BinaryOperator.Divide: '/',
            BinaryOperator.Equal: '==',
            BinaryOperator.NotEqual: '!=',
            BinaryOperator.Less: '<',
            BinaryOperator.LessEqual: '<=',
            BinaryOperator.Greater: '>',
            BinaryOperator.GreaterEqual: '>=',
        }[self]


class UnaryOperator(Enum):
    """一元运算符"""
    Not = auto()
    Negate = auto()
    
    def __str__(self):
        return {
            UnaryOperator.Not: '!',
            UnaryOperator.Negate: '-',
        }[self]


class LogicalOperator(Enum):
    """逻辑运算符"""
    And = auto()
    Or = auto()
    
    def __str__(self):
        return {
            LogicalOperator.And: '&&',
            LogicalOperator.Or: '||',
        }[self]


class Expr:
    """表达式基类"""
    
    def __eq__(self, other):
        return isinstance(other, Expr) and self.__dict__ == other.__dict__
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._repr_args()})"
    
    def _repr_args(self):
        return ""


@dataclass
class BinaryExpr(Expr):
    """二元表达式"""
    left: Expr
    operator: BinaryOperator
    right: Expr
    
    def _repr_args(self):
        return f"{self.left}, {self.operator}, {self.right}"


@dataclass
class LogicalExpr(Expr):
    """逻辑表达式"""
    left: Expr
    operator: LogicalOperator
    right: Expr
    
    def _repr_args(self):
        return f"{self.left}, {self.operator}, {self.right}"


@dataclass
class UnaryExpr(Expr):
    """一元表达式"""
    operator: UnaryOperator
    operand: Expr
    
    def _repr_args(self):
        return f"{self.operator}, {self.operand}"


@dataclass
class VariableExpr(Expr):
    """变量表达式"""
    name: str
    
    def _repr_args(self):
        return f'"{self.name}"'


@dataclass
class CallExpr(Expr):
    """函数调用表达式"""
    callee: Expr
    arguments: List[Expr]
    
    def _repr_args(self):
        return f"{self.callee}, [{', '.join(map(str, self.arguments))}]"


@dataclass
class GetExpr(Expr):
    """成员访问表达式"""
    object: Expr
    name: str
    
    def _repr_args(self):
        return f"{self.object}, \"{self.name}\""


@dataclass
class LiteralExpr(Expr):
    """字面量表达式"""
    value: LiteralKind
    
    def _repr_args(self):
        return f"{self.value}"


@dataclass
class GroupingExpr(Expr):
    """分组表达式"""
    expression: Expr
    
    def _repr_args(self):
        return f"{self.expression}"


@dataclass
class ListExpr(Expr):
    """列表表达式"""
    elements: List[Expr]
    
    def _repr_args(self):
        return f"[{', '.join(map(str, self.elements))}]"


@dataclass
class ListGetExpr(Expr):
    """列表索引表达式"""
    list: Expr
    index: Expr
    
    def _repr_args(self):
        return f"{self.list}, {self.index}"


# ========== 属性值类型 ==========

class PropertyValue:
    """属性值"""
    
    def __init__(self, value: Any):
        if isinstance(value, LiteralKind):
            self.type = 'literal'
            self.value = value
        elif isinstance(value, list):
            self.type = 'list'
            self.value = value
        elif isinstance(value, ObjectNode):
            self.type = 'object'
            self.value = value
        elif isinstance(value, Expr):
            self.type = 'expression'
            self.value = value
        else:
            raise TypeError(f"Invalid property value type: {type(value)}")
    
    def __eq__(self, other):
        if not isinstance(other, PropertyValue):
            return False
        return self.type == other.type and self.value == other.value
    
    def __repr__(self):
        return f"PropertyValue.{self.type.title()}({self.value})"


# ========== 对象节点 ==========

@dataclass
class ObjectNode:
    """对象节点"""
    name: str  # 类型名，匿名对象为空字符串
    properties: Dict[str, PropertyValue] = field(default_factory=dict)
    children: List['ObjectNode'] = field(default_factory=list)
    
    def __eq__(self, other):
        if not isinstance(other, ObjectNode):
            return False
        return (self.name == other.name and 
                self.properties == other.properties and 
                self.children == other.children)
    
    def __repr__(self):
        props = ', '.join(f'{k}={v}' for k, v in self.properties.items())
        children = ', '.join(str(c) for c in self.children)
        if self.name:
            return f"ObjectNode({self.name}, {{{props}}}, [{children}])"
        else:
            return f"ObjectNode({{{props}}}, [{children}])"


# ========== AST根节点 ==========

@dataclass
class AstRoot:
    """AST根节点"""
    objects: List[ObjectNode] = field(default_factory=list)
    
    def __eq__(self, other):
        if not isinstance(other, AstRoot):
            return False
        return self.objects == other.objects
    
    def __repr__(self):
        return f"AstRoot([{', '.join(map(str, self.objects))}])"
