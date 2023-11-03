from highorder.base.utils import StampToken


def test_stamp_1():
    st = StampToken()
    token = st.make('stamp_id', 'hello')
    assert st.verify(token) == True
    body = st.load(token)
    assert body == 'hello'


def test_stamp_2():
    st = StampToken()
    token = st.make('stamp_id', 1)
    assert st.verify(token) == True
    body = st.load(token)
    assert body == 1


def test_stamp_3():
    st = StampToken()
    token = st.make('stamp_id', {"foo": {"bar": True }})
    assert st.verify(token) == True
    body = st.load(token)
    assert body == {"foo": {"bar": True }}
