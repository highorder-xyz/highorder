import pytest

from callpy.web.request import parse_date
from callpy.web.response import text as text_response
from callpy.web.response import html as html_response
from callpy.web.response import (
    Response, make_response, redirect, jsonify,
    html_escape, html_quote, http_date)
from callpy.web.datastructures import MultiDict
from callpy.web.errors import BadRequest
import json
import copy
import datetime
import time


def test_http_date():
    t = time.time()
    assert http_date(t) == time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(t))

def test_html():
    assert '"&lt;&#039;&#13;&#10;&#9;&quot;\\&gt;"' == html_quote('<\'\r\n\t"\\>')

def test_basic_response():
    r = text_response('text')
    assert r.body == 'text'
    assert r.status_code == 200
    assert r.charset.lower() == 'utf-8'

    r = text_response('redirect', 302)
    assert r.status_code == 302

    r = text_response('', 999)
    assert r.status_code == 999

    with pytest.raises(ValueError):
        r = text_response('', 1099)

    with pytest.raises(ValueError):
        r = text_response('', 99)

    r = text_response('', '999') # Illegal, but acceptable three digit code
    assert r.status_code == 999

    with pytest.raises(ValueError):
        r = make_response(None)

    assert r.status_code == 999


    with pytest.raises(ValueError):
        r = text_response(object())

    r = text_response('text', 200, [('Custom-Header', 'custom-value')])
    assert r.status_code == 200
    assert 'Custom-Header' in r

    r = text_response('text', '200', {'Custom-Header':'custom-value'})
    assert r.status_code == 200
    assert 'Custom-Header' in r
    assert r.get_header('Custom-Header') == 'custom-value'
    assert 'Custom-Header' in dict(r.iter_headers())

    r.set_cookie('name1', 'value')
    r1 = r.copy()
    assert r1.headers == r.headers
    assert r1.body == r.body
    assert repr(r1) == repr(r)

    r = text_response('', 304)
    assert r.status_code == 304
    assert 'Content-Type' not in dict(r.iter_headers())

    r = make_response(BadRequest(''))
    assert r.status_code == 400


def test_jsonify():
    r = jsonify(username='admin',
                   email='admin@localhost',
                   id=42)
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'application/json'
    assert json.loads(r.body)['username'] == 'admin'

def test_set_cookie():
    r = Response()
    r.set_cookie('name1', 'value', max_age=5)
    r.set_cookie('name2', 'value 2', path='/foo')
    r.set_cookie('name4', 'value4', secret=True)
    with pytest.raises(TypeError):
        r.set_cookie('name3', 3)

    cookies = [value for name, value in r.headerlist
               if name.title() == 'Set-Cookie']
    cookies.sort()
    assert cookies[0] == 'name1=value; Max-Age=5'
    assert cookies[1] == 'name2="value 2"; Path=/foo'

def test_set_cookie_maxage():
    import datetime
    r = Response()
    r.set_cookie('name1', 'value', max_age=5)
    r.set_cookie('name2', 'value', max_age=datetime.timedelta(days=1))
    cookies = sorted([value for name, value in r.headerlist
               if name.title() == 'Set-Cookie'])
    assert cookies[0] == 'name1=value; Max-Age=5'
    assert cookies[1] == 'name2=value; Max-Age=86400'

def test_set_cookie_expires():
    r = Response()
    r.set_cookie('name1', 'value', expires=42)
    r.set_cookie('name2', 'value', expires=datetime.datetime(1970,1,1,0,0,43))
    cookies = sorted([value for name, value in r.headerlist
               if name.title() == 'Set-Cookie'])
    assert cookies[0] == 'name1=value; expires=Thu, 01 Jan 1970 00:00:42 GMT'
    assert cookies[1] == 'name2=value; expires=Thu, 01 Jan 1970 00:00:43 GMT'

def test_set_cookie_secure():
    r = Response()
    r.set_cookie('name1', 'value', secure=True)
    r.set_cookie('name2', 'value', secure=False)
    cookies = sorted([value for name, value in r.headerlist
               if name.title() == 'Set-Cookie'])
    assert cookies[0].lower() == 'name1=value; secure'
    assert cookies[1] == 'name2=value'

def test_set_cookie_httponly():
    r = Response()
    r.set_cookie('name1', 'value', httponly=True)
    r.set_cookie('name2', 'value', httponly=False)
    cookies = sorted([value for name, value in r.headerlist
               if name.title() == 'Set-Cookie'])
    assert cookies[0].lower() == 'name1=value; httponly'
    assert cookies[1] == 'name2=value'

def test_delete_cookie():
    response = Response()
    response.set_cookie('name', 'value')
    response.delete_cookie('name')
    cookies = [value for name, value in response.headerlist
               if name.title() == 'Set-Cookie']
    assert 'name=;' in cookies[0] or 'name="";' in cookies[0]

def test_redirect():
    r = redirect('http://example.com/foo/new', 302)
    assert r.status_code == 302
    assert r.headers['location'] == 'http://example.com/foo/new'
    r = redirect('http://example.com/foo/new2', 301)
    assert r.status_code == 301
    assert r.headers['location'] == 'http://example.com/foo/new2'

def test_set_header():
    response = Response()
    response['x-test'] = 'foo'
    headers = [value for name, value in response.headerlist
               if name.title() == 'X-Test']
    assert ['foo'] == headers
    assert 'foo' == response['x-test']

    response['X-Test'] = 'bar'
    headers = [value for name, value in response.headerlist
               if name.title() == 'X-Test']
    assert ['bar'] == headers
    assert 'bar' == response['x-test']

def test_append_header():
    response = Response()
    response.set_header('x-test', 'foo')
    headers = [value for name, value in response.headerlist
               if name.title() == 'X-Test']
    assert ['foo'] == headers
    assert 'foo' == response['x-test']

    response.add_header('X-Test', 'bar')
    headers = [value for name, value in response.headerlist
               if name.title() == 'X-Test']
    assert ['foo', 'bar'] == headers
    assert 'foo' == response['x-test']

def test_delete_header():
    response = Response()
    response['x-test'] = 'foo'
    assert 'foo', response['x-test']
    del response['X-tESt']
    with pytest.raises(KeyError):
        response['x-test']

def test_non_string_header():
    response = Response()
    response['x-test'] = 5
    assert '5' == response['x-test']
    with pytest.raises(ValueError):
        response['x-test'] = None

def test_expires_header():
    import datetime
    response = Response()
    now = datetime.datetime.now()
    response.expires = now

    def seconds(a, b):
        td = max(a,b) - min(a,b)
        return td.days*360*24 + td.seconds

    assert 0 == seconds(response.expires, now)
    now2 = datetime.datetime.utcfromtimestamp(
        parse_date(response.headers['Expires']))
    assert 0 == seconds(now, now2)
