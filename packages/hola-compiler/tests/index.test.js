import { Tokenizer, TokenKind, NodeKind, Parser, Compiler }  from '../src/index'
import { assert, describe, expect, it } from 'vitest'

function compare_tokens(code, desire_tokens) {
    const raw_tokens = new Tokenizer().tokenize(code);
    const tokens = raw_tokens.map(x => [x.kind, x.value]);
    expect(tokens).toEqual(desire_tokens)
}

function compare_nodes(code, desire_nodes) {
    function transform_list_node(list_node) {
        return list_node.map(x => transform_object_node(x));
    }

    function transform_properties(properties) {
        const p = {};
        for (const [k, v] of Object.entries(properties)) {
            p[k] = transform_object_node(v);
        }
        return p;
    }

    function transform_object_node(obj_node) {
        const r = {
            kind: obj_node.kind,
            value: obj_node.value,
            properties: transform_properties(obj_node.properties),
            children: transform_list_node(obj_node.children)
        };
        return r;
    }

    const root_node = new Parser().parse(code);
    const nodes = root_node.children.map(x => transform_object_node(x));

    expect(nodes).toEqual(desire_nodes)
}

function compare_object(code, desire_object) {
    const root_object = new Compiler().compile(code);
    expect(root_object).toEqual(desire_object);
}


it('tokenizer_simple_1', () => {
    compare_tokens('', [])
});

it('tokenizer_simple_2', () => {
    compare_tokens(
        'Page {}',
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.RBrace, '}']
        ]
    );
});

it('tokenizer_simple_3', () => {
    compare_tokens(
        'Page { route: "/" }',
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.StringLiteral, '/'],
            [TokenKind.RBrace, '}']
        ]
    );
});


it('tokenizer_simple_31', () => {
    compare_tokens(
        'Page { route: "/a\nbb" }',
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.StringLiteral, '/a\nbb'],
            [TokenKind.RBrace, '}']
        ]
    );
});

it('tokenizer_simple_4', () => {
    compare_tokens(
        `Page { route: "/"
            size: 5
        }`,
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.StringLiteral, '/'],
            [TokenKind.LineBreak, '\n'],
            [TokenKind.PropertyName, 'size'],
            [TokenKind.Colon, ':'],
            [TokenKind.NumberLiteral, 5],
            [TokenKind.LineBreak, '\n'],
            [TokenKind.RBrace, '}']
        ]
    );
});

it('tokenizer_simple_5', () => {
    compare_tokens(
        `Page { route: /
            size: 5
        }`,
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.Division, '/'],
            [TokenKind.LineBreak, '\n'],
            [TokenKind.PropertyName, 'size'],
            [TokenKind.Colon, ':'],
            [TokenKind.NumberLiteral, 5],
            [TokenKind.LineBreak, '\n'],
            [TokenKind.RBrace, '}']
        ]
    );
});


it('tokenizer_simple_6', () => {
    compare_tokens(
        `Page { route: /"
            size: 5
        }`,
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.Division, '/'],
            [TokenKind.StringLiteral, '\n            size: 5\n        }']
        ]
    );
});


it('tokenizer_simple_7', () => {
    compare_tokens(
        `Page { route: /"
            size: "5"
        }`,
        [
            [TokenKind.Identifier, 'Page'],
            [TokenKind.LBrace, '{'],
            [TokenKind.PropertyName, 'route'],
            [TokenKind.Colon, ':'],
            [TokenKind.Division, '/'],
            [TokenKind.StringLiteral, '\n            size: '],
            [TokenKind.NumberLiteral, 5],
            [TokenKind.StringLiteral, '\n        }'],
        ]
    );
});


it('parser_simple_1', () => {
    compare_nodes(
        'Page {}',
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {},
                children: []
            }
        ]
    );
})

it('parser_simple_2', () => {
    compare_nodes(
        'Page { route: "/abc" }',
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    route: {
                        kind: NodeKind.String,
                        value: '/abc',
                        properties: {},
                        children: []
                    }
                },
                children: []
            }
        ]
    );
})


it('parser_simple_3', () => {
    compare_nodes(
        'Page { popup: true, hide: false}',
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    popup: {
                        kind: NodeKind.Bool,
                        value: true,
                        properties: {},
                        children: []
                    },
                    hide: {
                        kind: NodeKind.Bool,
                        value: false,
                        properties: {},
                        children: []
                    }
                },
                children: []
            }
        ]
    );
})


it('parser_simple_4', () => {
    compare_nodes(
        'Page { text: null }',
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    text: {
                        kind: NodeKind.Null,
                        value: null,
                        properties: {},
                        children: []
                    }
                },
                children: []
            }
        ]
    );
})

it('parser_simple_5', () => {
    compare_nodes(
        `Page { int: 1234
        float: 1223.23
            }`,
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    int: {
                        kind: NodeKind.Number,
                        value: 1234,
                        properties: {},
                        children: []
                    },
                    float: {
                        kind: NodeKind.Number,
                        value: 1223.23,
                        properties: {},
                        children: []
                    }
                },
                children: []
            }
        ]
    );
})



it('parser_complex_1', () => {
    compare_nodes(
        'Page { route: "/abc", valid: ["111", "222"] }',
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    route: {
                        kind: NodeKind.String,
                        value: '/abc',
                        properties: {},
                        children: []
                    },
                    valid: {
                        kind: NodeKind.List,
                        value: null,
                        properties: {},
                        children: [
                            {
                                kind: NodeKind.String,
                                value: '111',
                                properties: {},
                                children: []
                            },
                            {
                                kind: NodeKind.String,
                                value: '222',
                                properties: {},
                                children: []
                            }
                        ]
                    }
                },
                children: []
            }
        ]
    );
});


it('parser_complex_2', () => {
    compare_nodes(
        `Page {
            route: "/abc", valid: ["111", "222"]
            Hero {
                "text": "Welcome"
            }

        }`,
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    route: {
                        kind: NodeKind.String,
                        value: '/abc',
                        properties: {},
                        children: []
                    },
                    valid: {
                        kind: NodeKind.List,
                        value: null,
                        properties: {},
                        children: [
                            {
                                kind: NodeKind.String,
                                value: '111',
                                properties: {},
                                children: []
                            },
                            {
                                kind: NodeKind.String,
                                value: '222',
                                properties: {},
                                children: []
                            }
                        ]
                    }
                },
                children: [{
                    kind: NodeKind.Object,
                    value: 'Hero',
                    properties: {
                        text: {
                            kind: NodeKind.String,
                            value: 'Welcome',
                            properties: {},
                            children: []
                        }
                    },
                    children: []
                }]
            }
        ]
    );
});


it('parser_complex_3', () => {
    compare_nodes(
        `Page {
            route: "/abc", valid: ["111", Hero {
                "text": "Welcome"
            }]
        }`,
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    route: {
                        kind: NodeKind.String,
                        value: '/abc',
                        properties: {},
                        children: []
                    },
                    valid: {
                        kind: NodeKind.List,
                        value: null,
                        properties: {},
                        children: [
                            {
                                kind: NodeKind.String,
                                value: '111',
                                properties: {},
                                children: []
                            },
                            {
                                kind: NodeKind.Object,
                                value: 'Hero',
                                properties: {
                                    text: {
                                        kind: NodeKind.String,
                                        value: 'Welcome',
                                        properties: {},
                                        children: []
                                    }
                                },
                                children: []
                            }
                        ]
                    }
                },
                children: []
            }
        ]
    );
});

it('parser_complex_4', () => {
    compare_nodes(
        `Page {
            route: "/abc", valid: ["111", {
                "text": "Welcome"
            }]
        }`,
        [
            {
                kind: NodeKind.Object,
                value: 'Page',
                properties: {
                    route: {
                        kind: NodeKind.String,
                        value: '/abc',
                        properties: {},
                        children: []
                    },
                    valid: {
                        kind: NodeKind.List,
                        value: null,
                        properties: {},
                        children: [
                            {
                                kind: NodeKind.String,
                                value: '111',
                                properties: {},
                                children: []
                            },
                            {
                                kind: NodeKind.Object,
                                value: '',
                                properties: {
                                    text: {
                                        kind: NodeKind.String,
                                        value: 'Welcome',
                                        properties: {},
                                        children: []
                                    }
                                },
                                children: []
                            }
                        ]
                    }
                },
                children: []
            }
        ]
    );
});

it('compiler_simple_1', () => {
    compare_object(
        'Page {}',
        {
            interfaces: [{
                type: 'page'
            }]
        }
    );
});

it('compiler_simple_2', () => {
    compare_object(
        'Page { route: "/home" }',
        {
            interfaces: [{
                type: 'page',
                route: '/home'
            }]
        }
    );
});

it('compiler_simple_3', () => {
    compare_object(
        `Page { route: "/home"
        name: "home" }`,
        {
            interfaces: [{
                type: 'page',
                route: '/home',
                name: 'home'
            }]
        }
    );
});
