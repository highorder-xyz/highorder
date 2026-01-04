"""
Hola虚拟机 - 表达式求值
"""

from typing import Any, Dict, Callable, List
from .ast import (
    Expr, BinaryExpr, LogicalExpr, UnaryExpr, VariableExpr,
    CallExpr, GetExpr, LiteralExpr, GroupingExpr, ListExpr, ListGetExpr,
    LiteralKind, NumberValue, BinaryOperator, UnaryOperator, LogicalOperator
)
from .error import RuntimeError


class VMValue:
    """VM值类型"""
    
    def __init__(self, value: Any):
        self.value = value
        
        # 确定类型
        if value is None:
            self.type = 'null'
        elif isinstance(value, bool):
            self.type = 'bool'
        elif isinstance(value, int):
            self.type = 'int'
        elif isinstance(value, float):
            self.type = 'float'
        elif isinstance(value, str):
            self.type = 'string'
        elif isinstance(value, list):
            self.type = 'list'
        elif isinstance(value, dict):
            self.type = 'object'
        elif callable(value):
            self.type = 'function'
        else:
            self.type = 'unknown'
    
    def is_truthy(self) -> bool:
        """判断值是否为真"""
        if self.value is None:
            return False
        if isinstance(self.value, bool):
            return self.value
        if isinstance(self.value, (int, float)):
            return self.value != 0
        if isinstance(self.value, str):
            return len(self.value) > 0
        if isinstance(self.value, (list, dict)):
            return len(self.value) > 0
        return True
    
    def __eq__(self, other):
        if not isinstance(other, VMValue):
            return False
        return self.value == other.value
    
    def __repr__(self):
        return f"VMValue({self.type}: {repr(self.value)})"


class VM:
    """Hola虚拟机"""
    
    def __init__(self, context: Dict[str, Any] = None):
        """
        初始化VM
        
        Args:
            context: 变量上下文
        """
        self.context = context or {}
        self._add_builtins()
    
    def _add_builtins(self):
        """添加内置函数"""
        self.context.update({
            'len': self._builtin_len,
            'abs': self._builtin_abs,
            'min': self._builtin_min,
            'max': self._builtin_max,
            'str': self._builtin_str,
            'int': self._builtin_int,
            'float': self._builtin_float,
            'bool': self._builtin_bool,
        })
    
    def evaluate(self, expr: Expr) -> Any:
        """
        求值表达式
        
        Args:
            expr: 表达式AST节点
            
        Returns:
            求值结果
        """
        result = self._eval_expr(expr)
        return result.value if isinstance(result, VMValue) else result
    
    def _eval_expr(self, expr: Expr) -> VMValue:
        """求值表达式并返回VMValue"""
        match expr:
            case BinaryExpr(left, op, right):
                return self._eval_binary(left, op, right)
            
            case LogicalExpr(left, op, right):
                return self._eval_logical(left, op, right)
            
            case UnaryExpr(op, operand):
                return self._eval_unary(op, operand)
            
            case VariableExpr(name):
                return self._eval_variable(name)
            
            case CallExpr(callee, arguments):
                return self._eval_call(callee, arguments)
            
            case GetExpr(object, name):
                return self._eval_get(object, name)
            
            case LiteralExpr(value):
                return self._eval_literal(value)
            
            case GroupingExpr(expression):
                return self._eval_expr(expression)
            
            case ListExpr(elements):
                return self._eval_list(elements)
            
            case ListGetExpr(list, index):
                return self._eval_list_get(list, index)
            
            case _:
                raise RuntimeError(f"Unknown expression type: {type(expr)}")
    
    def _eval_binary(self, left: Expr, op: BinaryOperator, right: Expr) -> VMValue:
        """求值二元表达式"""
        left_val = self._eval_expr(left)
        right_val = self._eval_expr(right)
        
        match op:
            case BinaryOperator.Add:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    result = left_val.value + right_val.value
                    return VMValue(result)
                elif left_val.type == 'string' and right_val.type == 'string':
                    return VMValue(left_val.value + right_val.value)
                else:
                    raise RuntimeError(f"Cannot add {left_val.type} and {right_val.type}")
            
            case BinaryOperator.Subtract:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value - right_val.value)
                else:
                    raise RuntimeError(f"Cannot subtract {right_val.type} from {left_val.type}")
            
            case BinaryOperator.Multiply:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value * right_val.value)
                else:
                    raise RuntimeError(f"Cannot multiply {left_val.type} and {right_val.type}")
            
            case BinaryOperator.Divide:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    if right_val.value == 0:
                        raise RuntimeError("Division by zero")
                    return VMValue(left_val.value / right_val.value)
                else:
                    raise RuntimeError(f"Cannot divide {left_val.type} by {right_val.type}")
            
            case BinaryOperator.Equal:
                return VMValue(left_val.value == right_val.value)
            
            case BinaryOperator.NotEqual:
                return VMValue(left_val.value != right_val.value)
            
            case BinaryOperator.Less:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value < right_val.value)
                else:
                    raise RuntimeError(f"Cannot compare {left_val.type} and {right_val.type}")
            
            case BinaryOperator.LessEqual:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value <= right_val.value)
                else:
                    raise RuntimeError(f"Cannot compare {left_val.type} and {right_val.type}")
            
            case BinaryOperator.Greater:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value > right_val.value)
                else:
                    raise RuntimeError(f"Cannot compare {left_val.type} and {right_val.type}")
            
            case BinaryOperator.GreaterEqual:
                if left_val.type in ('int', 'float') and right_val.type in ('int', 'float'):
                    return VMValue(left_val.value >= right_val.value)
                else:
                    raise RuntimeError(f"Cannot compare {left_val.type} and {right_val.type}")
    
    def _eval_logical(self, left: Expr, op: LogicalOperator, right: Expr) -> VMValue:
        """求值逻辑表达式"""
        left_val = self._eval_expr(left)
        
        match op:
            case LogicalOperator.And:
                # 短路求值
                if not left_val.is_truthy():
                    return left_val
                return self._eval_expr(right)
            
            case LogicalOperator.Or:
                # 短路求值
                if left_val.is_truthy():
                    return left_val
                return self._eval_expr(right)
    
    def _eval_unary(self, op: UnaryOperator, operand: Expr) -> VMValue:
        """求值一元表达式"""
        val = self._eval_expr(operand)
        
        match op:
            case UnaryOperator.Not:
                return VMValue(not val.is_truthy())
            
            case UnaryOperator.Negate:
                if val.type in ('int', 'float'):
                    return VMValue(-val.value)
                else:
                    raise RuntimeError(f"Cannot negate {val.type}")
    
    def _eval_variable(self, name: str) -> VMValue:
        """求值变量"""
        if name in self.context:
            value = self.context[name]
            return VMValue(value)
        else:
            raise RuntimeError(f"Undefined variable: {name}")
    
    def _eval_call(self, callee: Expr, arguments: List[Expr]) -> VMValue:
        """求值函数调用"""
        # 求值被调用对象
        callee_val = self._eval_expr(callee)
        
        # 求值参数
        args = [self._eval_expr(arg).value for arg in arguments]
        
        # 调用函数
        if callable(callee_val.value):
            try:
                result = callee_val.value(*args)
                return VMValue(result)
            except Exception as e:
                raise RuntimeError(f"Function call failed: {e}")
        else:
            raise RuntimeError(f"{callee_val.value} is not callable")
    
    def _eval_get(self, object: Expr, name: str) -> VMValue:
        """求值成员访问"""
        obj_val = self._eval_expr(object)
        
        if obj_val.type == 'object':
            if name in obj_val.value:
                return VMValue(obj_val.value[name])
            else:
                raise RuntimeError(f"Property '{name}' not found on object")
        elif obj_val.type == 'list' and name == 'length':
            return VMValue(len(obj_val.value))
        elif obj_val.type == 'string' and name == 'length':
            return VMValue(len(obj_val.value))
        else:
            raise RuntimeError(f"Cannot access property '{name}' on {obj_val.type}")
    
    def _eval_literal(self, literal: LiteralKind) -> VMValue:
        """求值字面量"""
        match literal.type:
            case 'string':
                return VMValue(literal.value)
            case 'number':
                if literal.value.is_int:
                    return VMValue(literal.value.value)
                else:
                    return VMValue(literal.value.value)
            case 'bool':
                return VMValue(literal.value)
            case 'null':
                return VMValue(None)
            case 'color':
                return VMValue(literal.value)
            case _:
                raise RuntimeError(f"Unknown literal type: {literal.type}")
    
    def _eval_list(self, elements: List[Expr]) -> VMValue:
        """求值列表"""
        values = [self._eval_expr(elem).value for elem in elements]
        return VMValue(values)
    
    def _eval_list_get(self, list_expr: Expr, index_expr: Expr) -> VMValue:
        """求值列表索引"""
        list_val = self._eval_expr(list_expr)
        index_val = self._eval_expr(index_expr)
        
        if list_val.type != 'list':
            raise RuntimeError(f"Cannot index {list_val.type}")
        
        if index_val.type not in ('int', 'float'):
            raise RuntimeError(f"List index must be number, got {index_val.type}")
        
        index = int(index_val.value)
        
        if index < 0 or index >= len(list_val.value):
            raise RuntimeError(f"List index out of range: {index}")
        
        return VMValue(list_val.value[index])
    
    # ========== 内置函数 ==========
    
    def _builtin_len(self, obj: Any) -> int:
        """内置函数: len"""
        if isinstance(obj, (str, list, dict)):
            return len(obj)
        else:
            raise RuntimeError(f"Object of type {type(obj).__name__} has no len()")
    
    def _builtin_abs(self, x: int | float) -> int | float:
        """内置函数: abs"""
        return abs(x)
    
    def _builtin_min(self, *args: int | float) -> int | float:
        """内置函数: min"""
        if len(args) == 0:
            raise RuntimeError("min() requires at least one argument")
        return min(args)
    
    def _builtin_max(self, *args: int | float) -> int | float:
        """内置函数: max"""
        if len(args) == 0:
            raise RuntimeError("max() requires at least one argument")
        return max(args)
    
    def _builtin_str(self, x: Any) -> str:
        """内置函数: str"""
        return str(x)
    
    def _builtin_int(self, x: Any) -> int:
        """内置函数: int"""
        return int(x)
    
    def _builtin_float(self, x: Any) -> float:
        """内置函数: float"""
        return float(x)
    
    def _builtin_bool(self, x: Any) -> bool:
        """内置函数: bool"""
        return bool(x)
