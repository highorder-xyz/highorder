
from highorder.hola.builtin import EveryExpression, every, _filter


def test_expression_1():
    data = [
        {
            'done': False
        },
        {
            'done': True
        }
    ]
    assert (every(data).done == True) == False
    assert (every(data).done == False) == False


def test_expression_2():
    data = [
        {
            'abc': 1,
            'done': True
        },
        {
            'done': True
        },
        {
            'hello': 'foo',
            'done': True
        },
    ]
    assert (every(data).done == True) == True
    assert (every(data).done == False) == False

def test_expression_3():
    data = [
    ]
    assert (every(data).done == True) == False
    assert (every(data).done == False) == False


def test_expression_4():
    data = [
        {
            'abc': 1,
            'done': True
        },
        {
            'done': True
        },
        {
            'hello': 'foo',
            'done': True
        },
    ]
    assert len(_filter(data).done == True) == 3
    assert len(_filter(data).done == False) == 0

def test_expression_5():
    data = [
    ]
    assert len(_filter(data).done == True) == 0
    assert len(_filter(data).done == False) == 0