"""
VM单元测试
"""

import sys
import os
import unittest

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

from hola.tokenizer import Tokenizer
from hola.parser import Parser
from hola.vm import VM
from hola.hola_ast import LiteralKind, NumberValue


class TestVM(unittest.TestCase):
    """VM测试类"""
    
    def _get_expression(self, source):
        """辅助方法：从源代码获取表达式"""
        wrapped_source = f'Object {{ value: {source} }}'
        tokenizer = Tokenizer(wrapped_source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return ast.objects[0].properties['value'].value
    
    def test_literal_number(self):
        """测试数字字面量"""
        expr = self._get_expression('{{ 42 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 42
    
    def test_literal_string(self):
        """测试字符串字面量"""
        expr = self._get_expression('{{ "hello" }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 'hello'
    
    def test_literal_bool_true(self):
        """测试true字面量"""
        expr = self._get_expression('{{ true }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_literal_bool_false(self):
        """测试false字面量"""
        expr = self._get_expression('{{ false }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is False
    
    def test_literal_null(self):
        """测试null字面量"""
        expr = self._get_expression('{{ null }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is None
    
    def test_addition(self):
        """测试加法"""
        expr = self._get_expression('{{ 1 + 2 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 3
    
    def test_subtraction(self):
        """测试减法"""
        expr = self._get_expression('{{ 10 - 4 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 6
    
    def test_multiplication(self):
        """测试乘法"""
        expr = self._get_expression('{{ 2 * 3 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 6
    
    def test_division(self):
        """测试除法"""
        expr = self._get_expression('{{ 10 / 2 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 5
    
    def test_float_division(self):
        """测试浮点除法"""
        expr = self._get_expression('{{ 7 / 2 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 3.5
    
    def test_operator_precedence(self):
        """测试运算符优先级"""
        expr = self._get_expression('{{ 2 + 3 * 4 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 14
    
    def test_parentheses(self):
        """测试括号"""
        expr = self._get_expression('{{ (2 + 3) * 4 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 20
    
    def test_greater_than(self):
        """测试大于"""
        expr = self._get_expression('{{ 5 > 3 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_less_than(self):
        """测试小于"""
        expr = self._get_expression('{{ 3 < 5 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_greater_equal(self):
        """测试大于等于"""
        expr = self._get_expression('{{ 5 >= 5 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_less_equal(self):
        """测试小于等于"""
        expr = self._get_expression('{{ 3 <= 5 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_equal(self):
        """测试等于"""
        expr = self._get_expression('{{ 5 == 5 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_not_equal(self):
        """测试不等于"""
        expr = self._get_expression('{{ 5 != 3 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_logical_and(self):
        """测试逻辑与"""
        expr = self._get_expression('{{ true && false }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is False
    
    def test_logical_or(self):
        """测试逻辑或"""
        expr = self._get_expression('{{ true || false }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_logical_not(self):
        """测试逻辑非"""
        expr = self._get_expression('{{ !true }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is False
    
    def test_short_circuit_and(self):
        """测试逻辑与短路"""
        expr = self._get_expression('{{ false && func() }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is False
    
    def test_short_circuit_or(self):
        """测试逻辑或短路"""
        expr = self._get_expression('{{ true || func() }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_unary_minus(self):
        """测试一元负号"""
        expr = self._get_expression('{{ -5 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == -5
    
    def test_variable_lookup(self):
        """测试变量查找"""
        expr = self._get_expression('{{ x }}')
        vm = VM({'x': 42})
        result = vm.evaluate(expr)
        assert result == 42
    
    def test_variable_not_found(self):
        """测试变量未找到"""
        expr = self._get_expression('{{ undefined }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is None
    
    def test_function_call_len(self):
        """测试len函数"""
        expr = self._get_expression('{{ len(items) }}')
        vm = VM({'items': [1, 2, 3]})
        result = vm.evaluate(expr)
        assert result == 3
    
    def test_function_call_abs(self):
        """测试abs函数"""
        expr = self._get_expression('{{ abs(-5) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 5
    
    def test_function_call_min(self):
        """测试min函数"""
        expr = self._get_expression('{{ min(1, 2, 3) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 1
    
    def test_function_call_max(self):
        """测试max函数"""
        expr = self._get_expression('{{ max(1, 2, 3) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 3
    
    def test_function_call_str(self):
        """测试str函数"""
        expr = self._get_expression('{{ str(42) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == '42'
    
    def test_function_call_int(self):
        """测试int函数"""
        expr = self._get_expression('{{ int("42") }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 42
    
    def test_function_call_float(self):
        """测试float函数"""
        expr = self._get_expression('{{ float("3.14") }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 3.14
    
    def test_function_call_bool(self):
        """测试bool函数"""
        expr = self._get_expression('{{ bool(1) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_member_access(self):
        """测试成员访问"""
        expr = self._get_expression('{{ user.name }}')
        vm = VM({'user': {'name': 'John'}})
        result = vm.evaluate(expr)
        assert result == 'John'
    
    def test_nested_member_access(self):
        """测试嵌套成员访问"""
        expr = self._get_expression('{{ app.settings.theme }}')
        vm = VM({'app': {'settings': {'theme': 'dark'}}})
        result = vm.evaluate(expr)
        assert result == 'dark'
    
    def test_list_index(self):
        """测试列表索引"""
        expr = self._get_expression('{{ items[0] }}')
        vm = VM({'items': [1, 2, 3]})
        result = vm.evaluate(expr)
        assert result == 1
    
    def test_list_index_negative(self):
        """测试列表负索引"""
        expr = self._get_expression('{{ items[-1] }}')
        vm = VM({'items': [1, 2, 3]})
        result = vm.evaluate(expr)
        assert result == 3
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        expr = self._get_expression('{{ a + b * c }}')
        vm = VM({'a': 10, 'b': 2, 'c': 3})
        result = vm.evaluate(expr)
        assert result == 16
    
    def test_complex_logical_expression(self):
        """测试复杂逻辑表达式"""
        expr = self._get_expression('{{ x > 10 && y < 20 }}')
        vm = VM({'x': 15, 'y': 18})
        result = vm.evaluate(expr)
        assert result is True
    
    def test_function_with_expressions(self):
        """测试带表达式的函数调用"""
        expr = self._get_expression('{{ min(a + b, c * d) }}')
        vm = VM({'a': 5, 'b': 3, 'c': 2, 'd': 4})
        result = vm.evaluate(expr)
        assert result == 7
    
    def test_string_concatenation(self):
        """测试字符串连接"""
        expr = self._get_expression('{{ "Hello" + " " + "World" }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 'Hello World'
    
    def test_mixed_type_operations(self):
        """测试混合类型操作"""
        expr = self._get_expression('{{ 10 + 3.14 }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 13.14
    
    def test_nested_function_calls(self):
        """测试嵌套函数调用"""
        expr = self._get_expression('{{ abs(min(-5, -10)) }}')
        vm = VM({})
        result = vm.evaluate(expr)
        assert result == 10
    
    def test_expression_with_variable_and_function(self):
        """测试变量和函数混合表达式"""
        expr = self._get_expression('{{ len(items) + 1 }}')
        vm = VM({'items': [1, 2, 3]})
        result = vm.evaluate(expr)
        assert result == 4
