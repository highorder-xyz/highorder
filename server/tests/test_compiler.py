
from highorder.base.compiler import Tokenizer, TokenKind, NodeKind, Parser, Compiler
import pprint
pp = pprint.PrettyPrinter(indent=4)

def compare_tokens(code, desire_tokens):
    raw_tokens = Tokenizer().tokenize(code)
    tokens = list(map(lambda x: (x.kind, x.value), raw_tokens))
    assert tokens == desire_tokens

def compare_nodes(code, desire_nodes):
    def transform_list_node(list_node):
        return [transform_object_node(x) for x in list_node]

    def transform_properties(properties):
        p = {}
        for k,v in properties.items():
            p[k] = transform_object_node(v)
        return p

    def transform_object_node(obj_node):
        r = {
            'kind': obj_node.kind,
            'value': obj_node.value,
            'properties': transform_properties(obj_node.properties),
            'children': transform_list_node(obj_node.children)
        }
        return r

    root_node = Parser().parse(code)
    nodes = list(map(lambda x: transform_object_node(x), root_node.children))
    #pp.pprint(nodes)
    assert nodes == desire_nodes

def compare_object(code, desire_object):
    root_object = Compiler().compile(code)
    assert root_object == desire_object

def test_tokenizer_simple_1():
    compare_tokens(
        '''''',
        []
    )

def test_tokenizer_simple_2():
    compare_tokens(
        '''Page {}''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_3():
    compare_tokens(
        '''Page { route: "/" }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_31():
    compare_tokens(
        '''Page { route: "/a
bb" }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/a\nbb'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_4():
    compare_tokens(
        '''Page { route: "/"
            size: 5
        }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.StringLiteral, '/'),
            (TokenKind.LineBreak, '\n'),
            (TokenKind.PropertyName, 'size'),
            (TokenKind.Colon, ':'),
            (TokenKind.NumberLiteral, 5),
            (TokenKind.LineBreak, '\n'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_5():
    compare_tokens(
        '''Page { route: /
            size: 5
        }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.Division, '/'),
            (TokenKind.LineBreak, '\n'),
            (TokenKind.PropertyName, 'size'),
            (TokenKind.Colon, ':'),
            (TokenKind.NumberLiteral, 5),
            (TokenKind.LineBreak, '\n'),
            (TokenKind.RBrace, '}')
        ]
    )

def test_tokenizer_simple_6():
    compare_tokens(
        '''Page { route: /"
            size: 5
        }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.Division, '/'),
            (TokenKind.StringLiteral, '\n            size: 5\n        }')
        ]
    )


def test_tokenizer_simple_7():
    compare_tokens(
        '''Page { route: /"
            size: "5"
        }''',
        [
            (TokenKind.Identifier, 'Page'),
            (TokenKind.LBrace, '{'),
            (TokenKind.PropertyName, 'route'),
            (TokenKind.Colon, ':'),
            (TokenKind.Division, '/'),
            (TokenKind.StringLiteral, '\n            size: '),
            (TokenKind.NumberLiteral, 5),
            (TokenKind.StringLiteral, '\n        }'),
        ]
    )


def test_parser_simple_1():
    compare_nodes(
        '''Page {}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {},
                "children":[]
            }
        ]
    )

def test_parser_simple_2():
    compare_nodes(
        '''Page { route: "/abc" }''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    }
                },
                "children":[]
            }
        ]
    )

def test_parser_simple_3():
    compare_nodes(
        '''Page { popup: true, hide: false}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "popup": {
                        "kind": NodeKind.Bool,
                        "value": True,
                        "properties": {},
                        "children": []
                    },
                    "hide": {
                        "kind": NodeKind.Bool,
                        "value": False,
                        "properties": {},
                        "children": []
                    }
                },
                "children":[]
            }
        ]
    )


def test_parser_simple_4():
    compare_nodes(
        '''Page { text: null }''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "text": {
                        "kind": NodeKind.Null,
                        "value": None,
                        "properties": {},
                        "children": []
                    }
                },
                "children":[]
            }
        ]
    )

def test_parser_simple_5():
    compare_nodes(
        '''Page { int: 1234
          float: 1223.23
              }''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "int": {
                        "kind": NodeKind.Number,
                        "value": 1234,
                        "properties": {},
                        "children": []
                    },
                    "float": {
                        "kind": NodeKind.Number,
                        "value": 1223.23,
                        "properties": {},
                        "children": []
                    }
                },
                "children":[]
            }
        ]
    )

def test_parser_complex_1():
    compare_nodes(
        '''Page { route: "/abc", valid: ["111", "222"] }''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    },
                    "valid": {
                        "kind": NodeKind.List,
                        "value": None,
                        "properties": {},
                        "children": [
                            {
                                "kind": NodeKind.String,
                                "value": "111",
                                "properties": {},
                                "children": []
                            },
                            {
                                "kind": NodeKind.String,
                                "value": "222",
                                "properties": {},
                                "children": []
                            }
                        ]
                    }
                },
                "children":[]
            }
        ]
    )


def test_parser_complex_2():
    compare_nodes(
        '''Page {
    route: "/abc", valid: ["111", "222"]
    Hero {
        "text": "Welcome"
    }

}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    },
                    "valid": {
                        "kind": NodeKind.List,
                        "value": None,
                        "properties": {},
                        "children": [
                            {
                                "kind": NodeKind.String,
                                "value": "111",
                                "properties": {},
                                "children": []
                            },
                            {
                                "kind": NodeKind.String,
                                "value": "222",
                                "properties": {},
                                "children": []
                            }
                        ]
                    }
                },
                "children":[{
                    "kind": NodeKind.Object,
                    "value": "Hero",
                    "properties": {
                        "text": {
                            "kind": NodeKind.String,
                            "value": "Welcome",
                            "properties": {},
                            "children": []
                        }
                    },
                    "children":[]
                }]
            }
        ]
    )


def test_parser_complex_3():
    compare_nodes(
        '''Page {
    route: "/abc", valid: ["111", Hero {
        "text": "Welcome"
    }]
}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    },
                    "valid": {
                        "kind": NodeKind.List,
                        "value": None,
                        "properties": {},
                        "children": [
                            {
                                "kind": NodeKind.String,
                                "value": "111",
                                "properties": {},
                                "children": []
                            },
                            {
                                "kind": NodeKind.Object,
                                "value": "Hero",
                                "properties": {
                                    "text": {
                                        "kind": NodeKind.String,
                                        "value": "Welcome",
                                        "properties": {},
                                        "children": []
                                    }
                                },
                                "children":[]
                            }
                        ]
                    }
                },
                "children":[]
            }
        ]
    )

def test_parser_complex_4():
    compare_nodes(
        '''Page {
    route: "/abc", valid: ["111", {
        "text": "Welcome"
    }]
}''',
        [
            {
                "kind": NodeKind.Object,
                "value": "Page",
                "properties": {
                    "route": {
                        "kind": NodeKind.String,
                        "value": "/abc",
                        "properties": {},
                        "children": []
                    },
                    "valid": {
                        "kind": NodeKind.List,
                        "value": None,
                        "properties": {},
                        "children": [
                            {
                                "kind": NodeKind.String,
                                "value": "111",
                                "properties": {},
                                "children": []
                            },
                            {
                                "kind": NodeKind.Object,
                                "value": '',
                                "properties": {
                                    "text": {
                                        "kind": NodeKind.String,
                                        "value": "Welcome",
                                        "properties": {},
                                        "children": []
                                    }
                                },
                                "children":[]
                            }
                        ]
                    }
                },
                "children":[]
            }
        ]
    )

def test_compiler_simple_1():
    compare_object(
        '''Page {}''',
        {
            "interfaces": [{
                "type": "page"
            }]
        }
    )


def test_compiler_simple_2():
    compare_object(
        '''Page { route: "/home" }''',
        {
            "interfaces": [{
                "type": "page",
                "route": "/home"
            }]
        }
    )


def test_compiler_simple_3():
    compare_object(
        '''Page { route: "/home"
         name: "home" }''',
        {
            "interfaces": [{
                "type": "page",
                "route": "/home",
                "name": "home"
            }]
        }
    )