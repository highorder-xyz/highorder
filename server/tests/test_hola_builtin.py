
from highorder.hola.builtin import EveryExpression, every


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