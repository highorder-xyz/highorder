"""
Compiler单元测试
"""

import sys
import os
import unittest
import json

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

from hola import compile
from hola.tokenizer import Tokenizer
from hola.parser import Parser
from hola.compiler import Compiler


class TestCompiler(unittest.TestCase):
    """Compiler测试类"""
    
    def test_compile_simple_object(self):
        """测试编译简单对象"""
        source = 'Page { title: "Hello" }'
        result = compile(source)
        
        assert 'objects' in result
        assert len(result['objects']) == 1
        obj = result['objects'][0]
        assert obj['type'] == 'Page'
        assert 'properties' in obj
        assert obj['properties']['title'] == 'Hello'
        assert 'children' in obj
        assert obj['children'] == []
    
    def test_compile_multiple_properties(self):
        """测试编译多个属性"""
        source = 'Object { a: 1, b: 2, c: 3 }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['a'] == 1
        assert obj['properties']['b'] == 2
        assert obj['properties']['c'] == 3
    
    def test_compile_nested_objects(self):
        """测试编译嵌套对象"""
        source = 'Page { Column { text: "Hi" } }'
        result = compile(source)
        
        page = result['objects'][0]
        assert page['type'] == 'Page'
        assert len(page['children']) == 1
        
        column = page['children'][0]
        assert column['type'] == 'Column'
        assert column['properties']['text'] == 'Hi'
    
    def test_compile_multiple_objects(self):
        """测试编译多个对象"""
        source = 'Page { } Modal { }'
        result = compile(source)
        
        assert len(result['objects']) == 2
        assert result['objects'][0]['type'] == 'Page'
        assert result['objects'][1]['type'] == 'Modal'
    
    def test_compile_empty_object(self):
        """测试编译空对象"""
        source = 'Page { }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['type'] == 'Page'
        assert obj['properties'] == {}
        assert obj['children'] == []
    
    def test_compile_anonymous_object(self):
        """测试编译匿名对象"""
        source = '{ title: "Test" }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['type'] == ''
        assert obj['properties']['title'] == 'Test'
    
    def test_compile_string_property(self):
        """测试编译字符串属性"""
        source = 'Page { title: "Hello World" }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['title'] == 'Hello World'
    
    def test_compile_number_property(self):
        """测试编译数字属性"""
        source = 'Object { count: 42 }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['count'] == 42
    
    def test_compile_float_property(self):
        """测试编译浮点数属性"""
        source = 'Object { price: 99.9 }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['price'] == 99.9
    
    def test_compile_bool_property(self):
        """测试编译布尔属性"""
        source = 'Object { active: true }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['active'] is True
    
    def test_compile_null_property(self):
        """测试编译null属性"""
        source = 'Object { value: null }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['value'] is None
    
    def test_compile_color_property(self):
        """测试编译颜色属性"""
        source = 'Object { color: #FF0000 }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['properties']['color'] == '#FF0000'
    
    def test_compile_list_property(self):
        """测试编译列表属性"""
        source = 'Object { items: [1, 2, 3] }'
        result = compile(source)
        
        obj = result['objects'][0]
        items = obj['properties']['items']
        assert items == [1, 2, 3]
    
    def test_compile_list_with_holes(self):
        """测试编译带空位的列表"""
        source = 'Object { items: [1,,3] }'
        result = compile(source)
        
        obj = result['objects'][0]
        items = obj['properties']['items']
        assert items == [1, None, 3]
    
    def test_compile_mixed_list(self):
        """测试编译混合类型列表"""
        source = 'Object { mixed: [true, "text", 3.14] }'
        result = compile(source)
        
        obj = result['objects'][0]
        mixed = obj['properties']['mixed']
        assert mixed == [True, 'text', 3.14]
    
    def test_compile_nested_object_property(self):
        """测试编译嵌套对象属性"""
        source = 'Page { events: { click: ShowModal } }'
        result = compile(source)
        
        obj = result['objects'][0]
        events = obj['properties']['events']
        assert isinstance(events, dict)
        assert 'type' in events
    
    def test_compile_expression(self):
        """测试编译表达式"""
        source = 'Object { sum: {{ a + b }} }'
        result = compile(source)
        
        obj = result['objects'][0]
        expr = obj['properties']['sum']
        assert isinstance(expr, dict)
        assert 'type' in expr
    
    def test_compile_namespace(self):
        """测试编译命名空间"""
        source = 'System.Collections.Generic.List { count: 0 }'
        result = compile(source)
        
        obj = result['objects'][0]
        assert obj['type'] == 'System.Collections.Generic.List'
    
    def test_compile_deeply_nested_objects(self):
        """测试编译深层嵌套对象"""
        source = 'A { B { C { D { value: 1 } } } }'
        result = compile(source)
        
        a = result['objects'][0]
        b = a['children'][0]
        c = b['children'][0]
        d = c['children'][0]
        assert d['type'] == 'D'
        assert d['properties']['value'] == 1
    
    def test_compile_result_is_json_serializable(self):
        """测试编译结果可序列化为JSON"""
        source = 'Page { title: "Hello", Column { text: "Hi" } }'
        result = compile(source)
        
        # 应该能够序列化为JSON
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
        
        # 应该能够从JSON反序列化
        parsed = json.loads(json_str)
        assert parsed == result
    
    def test_compile_with_compiler_class(self):
        """测试使用Compiler类"""
        source = 'Page { title: "Test" }'
        
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        compiler = Compiler()
        result = compiler.compile(ast)
        
        assert 'objects' in result
        assert len(result['objects']) == 1
    
    def test_compile_expression_structure(self):
        """测试表达式编译结构"""
        source = 'Object { expr: {{ a + b }} }'
        result = compile(source)
        
        expr = result['objects'][0]['properties']['expr']
        assert expr['type'] == 'Binary'
        assert expr['operator'] == '+'
        assert 'left' in expr
        assert 'right' in expr
        assert expr['left']['type'] == 'Variable'
        assert expr['left']['name'] == 'a'
        assert expr['right']['type'] == 'Variable'
        assert expr['right']['name'] == 'b'
