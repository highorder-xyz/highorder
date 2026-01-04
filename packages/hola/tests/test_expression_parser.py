"""
Expression Parser单元测试
"""

import sys
import os
import unittest

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

from hola.tokenizer import Tokenizer
from hola.expression_parser import ExpressionParser
from hola.hola_ast import (
    BinaryExpr, LogicalExpr, UnaryExpr, VariableExpr,
    CallExpr, GetExpr, LiteralExpr, GroupingExpr, ListExpr,
    LiteralKind, NumberValue, BinaryOperator, UnaryOperator, LogicalOperator
)


class TestExpressionParser(unittest.TestCase):
    """Expression Parser测试类"""
    
    def _parse_expression(self, source):
        """辅助方法：解析表达式"""
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = ExpressionParser(tokens)
        return parser.parse()
    
    def test_simple_addition(self):
        """测试简单加法"""
        expr = self._parse_expression('a + b')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Plus
        assert isinstance(expr.left, VariableExpr)
        assert expr.left.name == 'a'
        assert isinstance(expr.right, VariableExpr)
        assert expr.right.name == 'b'
    
    def test_simple_subtraction(self):
        """测试减法"""
        expr = self._parse_expression('10 - 4')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Minus
    
    def test_multiplication(self):
        """测试乘法"""
        expr = self._parse_expression('2 * 3')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Star
    
    def test_division(self):
        """测试除法"""
        expr = self._parse_expression('10 / 2')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Slash
    
    def test_operator_precedence(self):
        """测试运算符优先级"""
        expr = self._parse_expression('a + b * c')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Plus
        assert isinstance(expr.left, VariableExpr)
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.operator == BinaryOperator.Star
    
    def test_parentheses(self):
        """测试括号"""
        expr = self._parse_expression('(a + b) * c')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Star
        assert isinstance(expr.left, GroupingExpr)
        assert isinstance(expr.left.expression, BinaryExpr)
        assert expr.left.expression.operator == BinaryOperator.Plus
    
    def test_comparison_operators(self):
        """测试比较运算符"""
        # >
        expr = self._parse_expression('5 > 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Greater
        
        # >=
        expr = self._parse_expression('5 >= 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.GreaterEqual
        
        # <
        expr = self._parse_expression('5 < 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Less
        
        # <=
        expr = self._parse_expression('5 <= 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.LessEqual
        
        # ==
        expr = self._parse_expression('5 == 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.EqualEqual
        
        # !=
        expr = self._parse_expression('5 != 3')
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.BangEqual
    
    def test_logical_and(self):
        """测试逻辑与"""
        expr = self._parse_expression('x > 10 && y < 20')
        
        assert isinstance(expr, LogicalExpr)
        assert expr.operator == LogicalOperator.And
        assert isinstance(expr.left, BinaryExpr)
        assert isinstance(expr.right, BinaryExpr)
    
    def test_logical_or(self):
        """测试逻辑或"""
        expr = self._parse_expression('a || b')
        
        assert isinstance(expr, LogicalExpr)
        assert expr.operator == LogicalOperator.Or
    
    def test_logical_not(self):
        """测试逻辑非"""
        expr = self._parse_expression('!true')
        
        assert isinstance(expr, UnaryExpr)
        assert expr.operator == UnaryOperator.Bang
        assert isinstance(expr.operand, LiteralExpr)
    
    def test_unary_minus(self):
        """测试一元负号"""
        expr = self._parse_expression('-5')
        
        assert isinstance(expr, UnaryExpr)
        assert expr.operator == UnaryOperator.Minus
        assert isinstance(expr.operand, LiteralExpr)
    
    def test_variable(self):
        """测试变量"""
        expr = self._parse_expression('x')
        
        assert isinstance(expr, VariableExpr)
        assert expr.name == 'x'
    
    def test_literal_number(self):
        """测试数字字面量"""
        expr = self._parse_expression('42')
        
        assert isinstance(expr, LiteralExpr)
        assert expr.value.kind == LiteralKind
        assert expr.value.value == NumberValue(42)
    
    def test_literal_string(self):
        """测试字符串字面量"""
        expr = self._parse_expression('"hello"')
        
        assert isinstance(expr, LiteralExpr)
        assert expr.value.value == 'hello'
    
    def test_literal_bool(self):
        """测试布尔字面量"""
        expr = self._parse_expression('true')
        
        assert isinstance(expr, LiteralExpr)
        assert expr.value.value is True
    
    def test_literal_null(self):
        """测试null字面量"""
        expr = self._parse_expression('null')
        
        assert isinstance(expr, LiteralExpr)
        assert expr.value.value is None
    
    def test_function_call(self):
        """测试函数调用"""
        expr = self._parse_expression('func(1, 2)')
        
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.callee, VariableExpr)
        assert expr.callee.name == 'func'
        assert len(expr.arguments) == 2
    
    def test_method_call(self):
        """测试方法调用"""
        expr = self._parse_expression('user.getProfile()')
        
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.callee, GetExpr)
        assert isinstance(expr.callee.object, VariableExpr)
        assert expr.callee.object.name == 'user'
        assert expr.callee.name == 'getProfile'
    
    def test_member_access(self):
        """测试成员访问"""
        expr = self._parse_expression('user.name')
        
        assert isinstance(expr, GetExpr)
        assert isinstance(expr.object, VariableExpr)
        assert expr.object.name == 'user'
        assert expr.name == 'name'
    
    def test_nested_member_access(self):
        """测试嵌套成员访问"""
        expr = self._parse_expression('app.settings.theme')
        
        assert isinstance(expr, GetExpr)
        assert isinstance(expr.object, GetExpr)
    
    def test_list_index(self):
        """测试列表索引"""
        expr = self._parse_expression('list[0]')
        
        assert isinstance(expr, ListGetExpr)
        assert isinstance(expr.object, VariableExpr)
        assert expr.object.name == 'list'
        assert isinstance(expr.index, LiteralExpr)
    
    def test_list_literal(self):
        """测试列表字面量"""
        expr = self._parse_expression('[1, 2, 3]')
        
        assert isinstance(expr, ListExpr)
        assert len(expr.elements) == 3
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        expr = self._parse_expression('(a + b) * c > 10 && d != null')
        
        assert isinstance(expr, LogicalExpr)
        assert expr.operator == LogicalOperator.And
        assert isinstance(expr.left, BinaryExpr)
        assert expr.left.operator == BinaryOperator.Greater
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.operator == BinaryOperator.BangEqual
    
    def test_function_call_with_expressions(self):
        """测试带表达式的函数调用"""
        expr = self._parse_expression('func(a + b, c * d)')
        
        assert isinstance(expr, CallExpr)
        assert len(expr.arguments) == 2
        assert isinstance(expr.arguments[0], BinaryExpr)
        assert isinstance(expr.arguments[1], BinaryExpr)
    
    def test_chained_calls(self):
        """测试链式调用"""
        expr = self._parse_expression('obj.method1().method2()')
        
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.callee, GetExpr)
        assert isinstance(expr.callee.object, CallExpr)
    
    def test_complex_precedence(self):
        """测试复杂优先级"""
        expr = self._parse_expression('a + b * c - d / e')
        
        assert isinstance(expr, BinaryExpr)
        assert expr.operator == BinaryOperator.Minus
        # 乘除应该先计算
        assert isinstance(expr.left, BinaryExpr)
        assert isinstance(expr.right, BinaryExpr)
