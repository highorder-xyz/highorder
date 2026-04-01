"""
Parser单元测试
"""

import sys
import os
import unittest

# 添加src目录到路径
src_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, src_dir)

from hola.tokenizer import Tokenizer
from hola.parser import Parser
from hola.hola_ast import LiteralKind, NumberValue


class TestParser(unittest.TestCase):
    """Parser测试类"""
    
    def test_simple_object(self):
        """测试简单对象解析"""
        source = 'Page { title: "Hello" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.objects) == 1
        obj = ast.objects[0]
        assert obj.name == 'Page'
        assert 'title' in obj.properties
        assert obj.properties['title'].value.kind == LiteralKind
        assert obj.properties['title'].value.value == 'Hello'
        assert len(obj.children) == 0
    
    def test_object_with_multiple_properties(self):
        """测试多属性对象"""
        source = 'Object { a: 1, b: 2, c: 3 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert len(obj.properties) == 3
        assert 'a' in obj.properties
        assert 'b' in obj.properties
        assert 'c' in obj.properties
    
    def test_nested_objects(self):
        """测试嵌套对象"""
        source = 'Page { Column { text: "Hi" } }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        page = ast.objects[0]
        assert page.name == 'Page'
        assert len(page.children) == 1
        
        column = page.children[0]
        assert column.name == 'Column'
        assert 'text' in column.properties
        assert column.properties['text'].value.value == 'Hi'
    
    def test_multiple_objects(self):
        """测试多个对象"""
        source = 'Page { } Modal { }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert len(ast.objects) == 2
        assert ast.objects[0].name == 'Page'
        assert ast.objects[1].name == 'Modal'
    
    def test_empty_object(self):
        """测试空对象"""
        source = 'Page { }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.name == 'Page'
        assert len(obj.properties) == 0
        assert len(obj.children) == 0
    
    def test_anonymous_object(self):
        """测试匿名对象"""
        source = '{ title: "Test" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.name == ''
        assert 'title' in obj.properties
    
    def test_property_with_string(self):
        """测试字符串属性"""
        source = 'Page { title: "Hello World" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['title'].value.value == 'Hello World'
    
    def test_property_with_number(self):
        """测试数字属性"""
        source = 'Object { count: 42 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['count'].value.value == NumberValue(42)
    
    def test_property_with_float(self):
        """测试浮点数属性"""
        source = 'Object { price: 99.9 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['price'].value.value == NumberValue(99.9)
    
    def test_property_with_bool(self):
        """测试布尔属性"""
        source = 'Object { active: true }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['active'].value.value is True
    
    def test_property_with_null(self):
        """测试null属性"""
        source = 'Object { value: null }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['value'].value.value is None
    
    def test_property_with_color(self):
        """测试颜色属性"""
        source = 'Object { color: #FF0000 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.properties['color'].value.value == '#FF0000'
    
    def test_property_with_list(self):
        """测试列表属性"""
        source = 'Object { items: [1, 2, 3] }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        items = obj.properties['items'].value
        assert len(items) == 3
    
    def test_property_with_nested_object(self):
        """测试嵌套对象属性"""
        source = 'Page { events: { click: ShowModal } }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        events = obj.properties['events'].value
        assert isinstance(events.value, type(ast.objects[0]))
        assert events.value.name == ''
    
    def test_property_with_expression(self):
        """测试表达式属性"""
        source = 'Object { sum: {{ a + b }} }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        expr = obj.properties['sum'].value.value
        assert expr is not None
    
    def test_list_with_holes(self):
        """测试带空位的列表"""
        source = 'Object { items: [1,,3] }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        items = obj.properties['items'].value
        assert len(items) == 3
        assert items[1].value.value is None
    
    def test_multiline_list(self):
        """测试多行列表"""
        source = 'Object { items: [1\n2\n3] }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        items = obj.properties['items'].value
        assert len(items) == 3
    
    def test_mixed_list(self):
        """测试混合类型列表"""
        source = 'Object { mixed: [true, "text", 3.14] }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        mixed = obj.properties['mixed'].value
        assert len(mixed) == 3
    
    def test_namespace(self):
        """测试命名空间"""
        source = 'System.Collections.Generic.List { count: 0 }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.name == 'System.Collections.Generic.List'
    
    def test_deeply_nested_objects(self):
        """测试深层嵌套对象"""
        source = 'A { B { C { D { value: 1 } } } }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        a = ast.objects[0]
        b = a.children[0]
        c = b.children[0]
        d = c.children[0]
        assert d.name == 'D'
        assert 'value' in d.properties
    
    def test_object_with_comments(self):
        """测试带注释的对象"""
        source = '// comment\nPage { title: "Test" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert obj.name == 'Page'
        assert 'title' in obj.properties
    
    def test_property_key_with_string(self):
        """测试字符串作为属性键"""
        source = 'Page { "title": "Hello" }'
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        obj = ast.objects[0]
        assert 'title' in obj.properties
