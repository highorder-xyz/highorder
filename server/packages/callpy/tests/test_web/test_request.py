import pytest

from callpy.web.request import (Request, parse_auth, parse_content_type, parse_date, parse_range_header)
from callpy.web.errors import BadRequest, NotFound, MethodNotAllowed
from callpy.web.datastructures import MultiDict, FormsDict
from callpy.web.utils import to_bytes, to_unicode
from io import BytesIO
import time
import base64
import copy
import inspect
import json

scope1 = {'client': ('172.29.0.10', 34784),
 'headers': [[b'host', b'test.callpy.org'],
             [b'connection', b'close'],
             [b'user-agent',
              b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:60.0) Gecko'
              b'/20100101 Firefox/60.0'],
             [b'accept',
              b'text/plain;q=0.9,*/*;q='
              b'0.8'],
             [b'accept-language', b'en-US,en;q=0.5'],
             [b'accept-encoding', b'gzip, deflate, br']],
 'http_version': '0.0',
 'method': 'POST',
 'path': '/bar',
 'root_path': '/foo',
 'query_string': b'a=1&b=2',
 'scheme': 'http',
 'server': ('172.28.0.10', 8080),
 'type': 'http'}

async def form_data_receive():
    return {'type':'http.request',
            'body': b'hello=world&code=200',
            'more_body': False}

async def json_data_receive():
    return {'type':'http.request',
            'body': b'{"hello":"world", "code":200}',
            'more_body': False}

def test_content_type():
    r = parse_content_type('text/plain')
    assert r == ('text/plain', {})
    r = parse_content_type('text/plain; charset=utf-8')
    assert r == ('text/plain', {'charset': 'utf-8'})

def test_auth():
    assert None == parse_auth(':')
    assert None == parse_auth('basic n:m')

def test_range_header():
    rv = list(parse_range_header('bytes=52'))
    assert rv == []

    rv = list(parse_range_header('bytes=52-', 1000))
    assert rv == [(52, 1000)]

    rv = list(parse_range_header('bytes=52a-', 1000))
    assert rv == []

    rv = list(parse_range_header('bytes=52-99', 1000))
    assert rv == [(52, 100)]

    rv = list(parse_range_header('bytes=52-99,-1000', 2000))
    assert rv == [(52, 100), (1000, 2000)]

    rv = list(parse_range_header('bytes = 1 - 100', 1000))
    assert rv == []

    rv = list(parse_range_header('AWesomes=0-999', 1000))
    assert rv == []

def test_basic_request():
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'content-type', b'text/plain; charset=utf-8'])
    req = Request(scope, None)
    assert req.args == MultiDict({'a':'1', 'b':'2'}.items())
    assert req.path == '/bar'
    assert req.full_path == '/foo/bar'
    assert req.script_root == '/foo'
    assert req.url == 'http://test.callpy.org/foo/bar?a=1&b=2'
    assert req.base_url == 'http://test.callpy.org/foo/bar'
    assert req.root_url == 'http://test.callpy.org/foo/'
    assert req.host_url == 'http://test.callpy.org/'
    assert req.host == 'test.callpy.org'
    assert req.blueprint == None
    assert req.mimetype == 'text/plain'
    assert req.mimetype_params == {'charset': 'utf-8'}
    assert req.content_length == 0
    assert req.authorization == None
    assert req.cookies == FormsDict()
    assert list(req.range) == []
    assert req.is_xhr == False
    assert req.is_secure == False
    assert req.if_modified_since == None
    assert req.if_unmodified_since == None
    assert req.access_route == ['172.29.0.10']
    assert req.remote_addr == '172.29.0.10'
    assert req.chunked == False
    assert req.method == "POST"
    assert req.url_charset == 'utf-8'
    assert "Content-Type" in req.headers

def test_basic_request2():
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x_forwarded_host', b'test.callpy.org'])
    req = Request(scope, None)
    assert req.host == 'test.callpy.org'
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x_forwarded_host', b'test.callpy.org, a.proxy.org'])
    req = Request(scope, None)
    assert req.host == 'test.callpy.org'
    scope = dict(copy.deepcopy(scope1))
    req = Request(scope, None)
    assert req.host == 'test.callpy.org'

@pytest.mark.asyncio
async def test_request_form():
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'content_type', b'application/x-www-form-urlencoded'])
    req = Request(scope, receive=form_data_receive)
    form_data = await req.form()
    form_data2 = await req.form()
    assert len(form_data) == 2
    assert form_data['hello'] == 'world'
    assert form_data['code'] == '200'
    assert len(form_data2) == 2
    assert form_data2['hello'] == 'world'
    assert form_data2['code'] == '200'

@pytest.mark.asyncio
async def test_request_json():
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'content_type', b'application/json'])
    req = Request(scope, receive=json_data_receive)
    json_data = await req.json()
    assert len(json_data) == 2
    assert json_data['hello'] == 'world'
    assert json_data['code'] == 200

def test_basic_error():
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'content-length', b'20a'])
    req = Request(scope, None)
    assert req.content_length == 0


def test_cookie_dict():
    """ Environ: Cookie dict """
    t = dict()
    t[b'a=a']      = {'a': 'a'}
    t[b'a=a; b=b'] = {'a': 'a', 'b':'b'}
    t[b'a=a; a=b'] = {'a': 'b'}
    for k, v in t.items():
        scope = dict(copy.deepcopy(scope1))
        scope['headers'].append([b'cookie', k])
        req = Request(scope, None)
        for n in v:
            assert v[n] == req.cookies[n]
            assert v[n] == req.get_cookie(n)


def test_auth():
    user, pwd = 'marc', 'secret'
    basic = base64.b64encode(to_bytes('%s:%s' % (user, pwd)))
    scope = dict(copy.deepcopy(scope1))
    r = Request(scope, None)
    assert r.authorization == None
    scope['headers'].append([b'authorization',  b'basic ' + basic])
    r = Request(scope, None)
    assert r.authorization == (user, pwd)

def test_remote_addr():
    ips = [b'1.2.3.4', b'2.3.4.5', b'3.4.5.6']
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x-forwarded-for', b', '.join(ips)])
    r = Request(scope, None)
    assert r.remote_addr == to_unicode(ips[0])

    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x-forwarded-for', b', '.join(ips)])
    scope['client'] = (to_unicode(ips[1]), 1212)
    r = Request(scope, None)
    assert r.remote_addr == to_unicode(ips[0])

    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'remote-addr', ips[1]])
    scope['client'] = (to_unicode(ips[1]), 1212)
    r = Request(scope, None)
    assert r.remote_addr == to_unicode(ips[1])

def test_remote_route():
    ips = [b'1.2.3.4', b'2.3.4.5', b'3.4.5.6']
    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x_forwarded_for', b', '.join(ips)])
    r = Request(scope, None)
    assert r.remote_route == list(map(lambda x: to_unicode(x), ips))

    scope = dict(copy.deepcopy(scope1))
    scope['headers'].append([b'x_forwarded_for', b', '.join(ips)])
    scope['client'] = (to_unicode(ips[1]), 1212)
    r = Request(scope, None)
    assert r.remote_route == list(map(lambda x: to_unicode(x), ips))

    scope = dict(copy.deepcopy(scope1))
    scope['client'] = (to_unicode(ips[1]), 1212)
    r = Request(scope, None)
    assert r.remote_route == [to_unicode(ips[1]),]
