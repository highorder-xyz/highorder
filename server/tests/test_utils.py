from highorder.base.utils import StampToken, restruct_dict


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


def restruct_compare(dictionary, target):
    r = restruct_dict(dictionary)
    assert r == target

def test_restruct_dict_1():
    restruct_compare({'name': 'hello'}, {'name': 'hello'})
    restruct_compare({'name': 'hello', 'profile.avatar': 'http://xxx'},
        {
            'name': 'hello',
            "profile": {
                "avatar": 'http://xxx'
            }
        }
    )

    restruct_compare(
        {
            'name': 'hello',
            'attribute': {
                "primary.role": "owner"
            },
            'profile.avatar': 'http://xxx'
        },
        {
            'name': 'hello',
            'attribute': {
                'primary': {
                    'role': 'owner'
                }
            },
            "profile": {
                "avatar": 'http://xxx'
            }
        }
    )
