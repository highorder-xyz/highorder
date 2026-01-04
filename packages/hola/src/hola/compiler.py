"""
Hola编译器 - 将AST编译为JSON格式
"""

from typing import Any, Dict, List
from .ast import (
    AstRoot, ObjectNode, PropertyValue, LiteralKind, NumberValue,
    Expr, BinaryExpr, LogicalExpr, UnaryExpr, VariableExpr,
    CallExpr, GetExpr, LiteralExpr, GroupingExpr, ListExpr, ListGetExpr,
    BinaryOperator, UnaryOperator, LogicalOperator
)
from .error import CompileError


class Compiler:
    """Hola编译器"""
    
    def __init__(self):
        pass
    
    def compile(self, ast: AstRoot) -> Dict[str, Any]:
        """编译AST为JSON格式"""
        objects = [self._compile_object(obj) for obj in ast.objects]
        return {
            "objects": objects
        }
    
    def _compile_object(self, node: ObjectNode) -> Dict[str, Any]:
        """编译对象节点"""
        result = {
            "type": node.name,
            "properties": {},
            "children": []
        }
        
        # 编译属性
        for key, value in node.properties.items():
            result["properties"][key] = self._compile_property_value(value)
        
        # 编译子对象
        result["children"] = [self._compile_object(child) for child in node.children]
        
        return result
    
    def _compile_property_value(self, value: PropertyValue) -> Any:
        """编译属性值"""
        match value.type:
            case 'literal':
                return self._compile_literal(value.value)
            case 'list':
                return [self._compile_property_value(item) for item in value.value]
            case 'object':
                return self._compile_object(value.value)
            case 'expression':
                return self._compile_expression(value.value)
            case _:
                raise CompileError(f"Unknown property value type: {value.type}")
    
    def _compile_literal(self, literal: LiteralKind) -> Any:
        """编译字面量"""
        match literal.type:
            case 'string':
                return literal.value
            case 'number':
                if literal.value.is_int:
                    return literal.value.value
                else:
                    return literal.value.value
            case 'bool':
                return literal.value
            case 'null':
                return None
            case 'color':
                return literal.value
            case _:
                raise CompileError(f"Unknown literal type: {literal.type}")
    
    def _compile_expression(self, expr: Expr) -> Dict[str, Any]:
        """编译表达式为可序列化的格式"""
        match expr:
            case BinaryExpr(left, op, right):
                return {
                    "type": "Binary",
                    "operator": str(op),
                    "left": self._compile_expression(left),
                    "right": self._compile_expression(right)
                }
            
            case LogicalExpr(left, op, right):
                return {
                    "type": "Logical",
                    "operator": str(op),
                    "left": self._compile_expression(left),
                    "right": self._compile_expression(right)
                }
            
            case UnaryExpr(op, operand):
                return {
                    "type": "Unary",
                    "operator": str(op),
                    "operand": self._compile_expression(operand)
                }
            
            case VariableExpr(name):
                return {
                    "type": "Variable",
                    "name": name
                }
            
            case CallExpr(callee, arguments):
                return {
                    "type": "Call",
                    "callee": self._compile_expression(callee),
                    "arguments": [self._compile_expression(arg) for arg in arguments]
                }
            
            case GetExpr(object, name):
                return {
                    "type": "Get",
                    "object": self._compile_expression(object),
                    "name": name
                }
            
            case LiteralExpr(value):
                return {
                    "type": "Literal",
                    "value": self._compile_literal(value)
                }
            
            case GroupingExpr(expression):
                return {
                    "type": "Grouping",
                    "expression": self._compile_expression(expression)
                }
            
            case ListExpr(elements):
                return {
                    "type": "List",
                    "elements": [self._compile_expression(elem) for elem in elements]
                }
            
            case ListGetExpr(list, index):
                return {
                    "type": "ListGet",
                    "list": self._compile_expression(list),
                    "index": self._compile_expression(index)
                }
            
            case _:
                raise CompileError(f"Unknown expression type: {type(expr)}")
