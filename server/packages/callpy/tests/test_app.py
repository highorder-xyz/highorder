# -*- coding: utf-8 -*-
import pytest

from callpy.app import CallPy
from callpy.web import Blueprint, response
import copy
import traceback
import asyncio


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
 'method': 'GET',
 'path': '/bar',
 'root_path': '/foo',
 'query_string': b'a=1&b=2',
 'scheme': 'http',
 'server': ('172.28.0.10', 8080),
 'type': 'http'}

async def empty_receive():
    return b''


send_list = []

async def list_send(data):
    global send_list
    send_list.append(data)



def test_basic_app():
    app = CallPy(__name__)
    async def hello(req):
        return 'ok'

    app.add_url_rule('/hello', 'hello', hello)

    async def hello2(req):
        return 'ok'

    with pytest.raises(AssertionError):
        app.add_url_rule('/hello', 'hello', hello2)

    @app.endpoint('foo')
    async def foo(req):
        return 'foo'
    app.add_url_rule('/foo', 'foo')

    async def error_handler(error):
        return '500'

    app.register_error_handler(500, error_handler)

@pytest.mark.asyncio
async def test_more_app():
    app = CallPy()

    @app.before_request
    async def before_request1(req):
        print('before_request')

    @app.before_request
    async def before_request2(req):
        print('before_request2')

    @app.route('/hello')
    async def hello(req):
        return 'ok'

    @app.after_request
    async def after_request1(req, resp):
        return resp

    @app.after_request
    async def after_request2(req, resp):
        return resp

    @app.errorhandler(404)
    async def error_handler404(req, exception):
        return '404'

    @app.errorhandler(500)
    async def error_handler500(req, exception):
        print(traceback.format_exc())
        return '500'

    @app.teardown_request
    async def teardown_request(req, resp, exc=None):
        pass

    assert app.before_request_funcs[None][0] == before_request1
    assert app.before_request_funcs[None][1] == before_request2
    assert app.after_request_funcs[None][0] == after_request2
    assert app.after_request_funcs[None][1] == after_request1

    bp = Blueprint('foo', url_prefix='/foo')
    @bp.before_request
    async def bp_before_request(req):
        pass

    @bp.after_request
    async def bp_after_request(req, resp):
        return resp

    @bp.teardown_request
    async def bp_teardown_request(req, resp, exc):
        pass

    @bp.route('/bar')
    async def bar(req):
        return 'bar'

    @bp.before_app_request
    async def bp_app_before_request(req):
        pass
    app.register_blueprint(bp)

    bp2 = Blueprint('foo2', url_prefix='/foo2')

    @bp2.errorhandler(500)
    async def bp_errorhandler(req, exception):
        pass

    with pytest.raises(AssertionError):
        app.register_blueprint(bp2)
    assert app.before_request_funcs[None][2] == bp_app_before_request
    assert app.before_request_funcs['foo'][0] == bp_before_request

    env = copy.deepcopy(scope1)
    env['root_path'] = '/hello'
    env['path'] = ''
    await app(env, empty_receive, list_send)
    global send_list
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'ok'
    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo'
    env['path'] = '/bar'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar'
    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo2'
    env['path'] = ''
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'404'


@pytest.mark.asyncio
async def test_basic_blueprint():
    app = CallPy()
    bp = Blueprint('foo', url_prefix='/foo')

    @bp.before_request
    async def bp_before_request(req):
        pass

    @bp.route('/bar')
    async def bar(req):
        return 'bar'

    @bp.before_app_request
    async def bp_app_before_request(req):
        pass

    @bp.after_request
    async def bp_after_request(req, resp):
        pass

    @bp.after_app_request
    async def bp_after_app_request(req, resp):
        pass

    @bp.teardown_request
    async def bp_teardown_request(req, resp, exc):
        pass

    @bp.teardown_app_request
    async def bp_teardown_app_request(req, resp, exc):
        pass

    @bp.app_errorhandler(500)
    async def bp_app_errorhandler(req, exception):
        pass

    @bp.endpoint('bbb')
    async def bbb():
        return 'ok'

    app.register_blueprint(bp)

    assert app.view_functions['foo.bbb'] == bbb


@pytest.mark.asyncio
async def test_blueprint_errorhandler():
    app = CallPy()

    bp = Blueprint('foo', url_prefix='/foo')

    @bp.route('/bar')
    async def bar(req):
        response.abort(400)
        return 'bar'

    @bp.route('/bar2')
    async def bar2(req):
        i = 1/0
        return 'bar'

    @bp.errorhandler(400)
    async def bp_errorhandler400(req, exception):
        return 'bar'

    @bp.app_errorhandler(500)
    async def bp_errorhandler(req, exception):
        return 'bar2'

    app.register_blueprint(bp)

    global send_list

    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo'
    env['path'] = '/bar'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar'

    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo'
    env['path'] = '/bar2'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar2'


@pytest.mark.asyncio
async def test_blueprint():
    app = CallPy()

    bp = Blueprint('foo', url_prefix='/foo')

    @bp.route('/bar')
    async def bar(req):
        return 'bar'

    @bp.route('/bar2')
    async def bar2(req):
        return 'bar2'

    app.register_blueprint(bp)
    app.register_blueprint(bp, url_prefix='/foo2')

    global send_list

    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo'
    env['path'] = '/bar'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar'

    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo'
    env['path'] = '/bar2'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar2'


    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo2'
    env['path'] = '/bar'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar'

    env = copy.deepcopy(scope1)
    env['root_path'] = '/foo2'
    env['path'] = '/bar2'
    await app(env, empty_receive, list_send)
    ret = send_list.pop()
    send_list.clear()
    assert ret['body'] == b'bar2'

class FakeServer:
    def __init__(self, app, **kwargs):
        self.app = app
        self.wait_seconds = 2
        self.start_hooks = []
        self.stop_hooks = []

    async def serve(self, sockets=None, start_hooks=[], stop_hooks=[]):
        self.start_hooks = start_hooks
        self.stop_hooks = stop_hooks
        for hook in self.start_hooks:
            await hook()
        await asyncio.sleep(self.wait_seconds)
        for hook in self.stop_hooks:
            await hook()

@pytest.mark.asyncio
async def test_hooks():
    app = CallPy()

    before_start_runned = False
    after_start_runned = False
    before_stop_runned = False
    after_stop_runned = False

    @app.before_start
    async def before_start_function():
        nonlocal before_start_runned
        before_start_runned = True

    with pytest.raises(Exception):
        @app.before_start
        def before_start_function2():
            pass

    @app.after_start
    async def after_start_function():
        nonlocal after_start_runned
        after_start_runned = True

    @app.before_stop
    async def before_stop_function():
        nonlocal before_stop_runned
        before_stop_runned = True

    @app.after_stop
    async def after_stop_function():
        nonlocal after_stop_runned
        after_stop_runned = True

    app.server = FakeServer(app)

    await app.start_serve()

    assert before_start_runned
    assert after_start_runned
    assert before_stop_runned
    assert after_stop_runned