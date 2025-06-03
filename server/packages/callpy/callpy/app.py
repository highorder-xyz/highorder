# -*- coding: utf-8 -*-

import os
import sys
from datetime import timedelta
import traceback
from itertools import chain
from functools import update_wrapper
import asyncio

from .web.routing import Router
from .web.errors import HTTPError, InternalServerError, MethodNotAllowed, BadRequest

from .web.request import Request
from .web.response import Response, make_response
from .web.handlers import StaticHandler
from .web.utils import reraise, to_bytes, to_unicode
from .server import Server
from basepy.asynclog import logger
from functools import partial
if sys.platform != 'win32':
    from .supervisor import Supervisor
else:
    from .watcher import Watcher as Supervisor


class CallPy(object):
    """The callpy object implements a ASGI application and acts as the central
    object.  Once it is created it will act as a central registry for
    the view functions, the URL rules,  and more.

    Usually you create a `CallPy` instance in your main module or
    in the `__init__.py` file of your package like this:

        from callpy import CallPy
        app = CallPy()

    """

    def __init__(self, name=''):
        self.config = {}
        self.dispatch = {}

        self.name = name or 'main'

        self.before_start_hooks = []
        self.after_start_hooks = []
        self.before_stop_hooks = []
        self.after_stop_hooks = []

        #: A dictionary of all view functions registered.  The keys will
        #: be function names which are also used to generate URLs and
        #: the values are the function objects themselves.
        self.view_functions = {}

        #: A dictionary of all registered error handlers.  The key is `None`
        #: for error handlers active on the application, otherwise the key is
        #: the name of the blueprint.  Each key points to another dictionary
        #: where they key is the status code of the http exception.  The
        #: special key `None` points to a list of tuples where the first item
        #: is the class for the instance check and the second the error handler
        #: function.
        #:
        self.error_handler_spec = {None: {}}

        #: A dictionary with lists of functions that should be called at the
        #: beginning of the request.  The key of the dictionary is the name of
        #: the blueprint this function is active for, `None` for all requests.
        #: This can for example be used to open database connections or
        #: getting hold of the currently logged in user.
        self.before_request_funcs = {}

        #: A dictionary with lists of functions that should be called after
        #: each request.  The key of the dictionary is the name of the blueprint
        #: this function is active for, `None` for all requests.  This can for
        #: example be used to open database connections or getting hold of the
        #: currently logged in user.
        self.after_request_funcs = {}
        self.teardown_request_funcs = {}

        #: all the attached blueprints in a dictionary by name.  Blueprints
        #: can be attached multiple times so this dictionary does not tell
        #: you how often they got attached.
        self.blueprints = {}

        self.router = Router()


    def run(self, host=None, port=None, debug=False, **options):
        """Runs the application on a local development server.
        Args:

          * host: the hostname to listen on. Set this to '0.0.0.0' to
                     have the server available externally as well. Defaults to
                     '127.0.0.1'.
          * port: the port of the webserver. Defaults to 5000 or the
                     port defined in the SERVER_NAME` config variable if
                     present.
        """
        if host is None:
            host = '127.0.0.1'
        if port is None:
            port = 3000
        if debug is not None:
            self.debug = bool(debug)
        workers = options.get('workers', 1)
        daemon = options.get('daemon', False)
        sv = Supervisor(self.name, workers=workers, daemon=daemon, target=self._serve_forever)
        self.server = Server(self, host=host, port=port, **options)
        sv.run()

    def _serve_forever(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_serve())

    async def start_serve(self):
        if len(self.before_start_hooks) > 0:
            for hook in self.before_start_hooks:
                await hook()
        await self.server.serve(start_hooks=self.after_start_hooks, stop_hooks=self.before_stop_hooks)
        if len(self.after_stop_hooks) > 0:
            for hook in self.after_stop_hooks:
                await hook()

    def register_blueprint(self, blueprint, **options):
        """Registers a blueprint on the application.
        """
        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, \
                'A blueprint\'s name collision occurred between %r and ' \
                '%r.  Both share the same name "%s".  Blueprints that ' \
                'are created on the fly need unique names.' % \
                (blueprint, self.blueprints[blueprint.name], blueprint.name)
        else:
            self.blueprints[blueprint.name] = blueprint
        blueprint.register(self, options)

    def add_url_rule(self, rule, endpoint=None, view_func=None, methods=None, **options):
        """Connects a URL rule.  Works exactly like the `route`
        decorator.  If a view_func is provided it will be registered with the
        endpoint.

        Basically this example:

            @app.route('/')
            def index():
                pass

        Is equivalent to the following:

            def index():
                pass
            app.add_url_rule('/', 'index', index)

        If the view_func is not provided you will need to connect the endpoint
        to a view function like so:

            app.view_functions['index'] = index

        Internally `route` invokes `add_url_rule` so if you want
        to customize the behavior via subclassing you only need to change
        this method.

        For more information refer to `url-route-registrations`.

        Args:

          * rule : the URL rule as string
          * endpoint : the endpoint for the registered URL rule.
          * view_func: the function to call when serving a request to the
                    provided endpoint
          * options: methods is a list of methods this rule should be limited
                    to (`GET`, `POST` etc.).
        """
        if endpoint is None:
            endpoint = view_func.__name__

        # if the methods are not given and the view_func object knows its
        # methods we can use that instead.  If neither exists, we go with
        # a tuple of only `GET` as default.
        if methods is None:
            methods = getattr(view_func, 'methods', None) or ('GET',)
        methods = set(methods)

        # Methods that should always be added
        required_methods = set(getattr(view_func, 'required_methods', ()))

        # Add the required methods now.
        methods |= required_methods

        defaults = options.get('defaults') or {}

        self.router.add(rule, endpoint, methods=methods, defaults=defaults)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func

    def route(self, rule, **options):
        """A decorator that is used to register a view function for a
        given URL rule.  This does the same thing as `add_url_rule`
        but is intended for decorator usage:

            @app.route('/')
            def index():
                return 'Hello World'

        For more information refer to `url-route-registrations`.

        Args:

          * rule: the URL rule as string
          * endpoint: the endpoint for the registered URL rule.
        """
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            methods = options.pop('methods', None)
            self.add_url_rule(rule, endpoint, f, methods, **options)
            return f
        return decorator

    def static(self, rule, directory, html=False, check=False):
        realrule1 = '{}/'.format(rule.rstrip('/'))
        realrule2 = '{}{}'.format(realrule1, '<path:target>')

        h = StaticHandler(directory, html=html, check_dir=check)
        endpoint = 'static_{}'.format(rule.strip('/').replace('/', '_'))

        self.add_url_rule(realrule1, endpoint, h, ['GET', 'PUT', 'POST', 'HEAD', 'DELETE'])
        self.add_url_rule(realrule2, endpoint, h, ['GET', 'PUT', 'POST', 'HEAD', 'DELETE'])


    def endpoint(self, endpoint):
        """A decorator to register a function as an endpoint.
        Example:

            @app.endpoint('example.endpoint')
            def example():
                return "example"
        Args:
            endpoint: the name of the endpoint
        """
        def decorator(f):
            self.view_functions[endpoint] = f
            return f
        return decorator

    def errorhandler(self, code):
        """A decorator that is used to register a function give a given
        error code.  Example:

            @app.errorhandler(404)
            def page_not_found(request, error):
                return 'This page does not exist', 404

        You can also register a function as error handler without using
        the `errorhandler` decorator.  The following example is
        equivalent to the one above:

            def page_not_found(request, error):
                return 'This page does not exist', 404
            app.error_handler_spec[None][404] = page_not_found

        Setting error handlers via assignments to `error_handler_spec`
        however is discouraged as it requires fiddling with nested dictionaries
        and the special case for arbitrary exception types.

        The first `None` refers to the active blueprint.  If the error
        handler should be application wide `None` shall be used.

        """
        def decorator(f):
            self._register_error_handler(None, code, f)
            return f
        return decorator

    def register_error_handler(self, code, f):
        """Alternative error attach function to the `errorhandler`
        decorator that is more straightforward to use for non decorator
        usage.
        """
        self._register_error_handler(None, code, f)

    def _register_error_handler(self, key, code, f):
        if not isinstance(code, int):
            raise ValueError("code must int, got {}".format(code))

        assert code != 500 or key is None, \
            'It is currently not possible to register a 500 internal ' \
            'server error on a per-blueprint level.'
        self.error_handler_spec.setdefault(key, {})[code] = f

    def _check_hook(self, hook):
        if not asyncio.iscoroutinefunction(hook):
            raise Exception('before/after hooks must be coroutine functions.')

    def before_start(self, hook):
        self._check_hook(hook)
        self.before_start_hooks.append(hook)
        return hook

    def after_start(self, hook):
        self._check_hook(hook)
        self.after_start_hooks.append(hook)
        return hook

    def before_stop(self, hook):
        self._check_hook(hook)
        self.before_stop_hooks.append(hook)
        return hook

    def after_stop(self, hook):
        self._check_hook(hook)
        self.after_stop_hooks.append(hook)
        return hook

    def before_request(self, f):
        """Registers a function to run before each request."""
        self.before_request_funcs.setdefault(None, []).append(f)
        return f


    def after_request(self, f):
        """Register a function to be run after each request.  Your function
        must take one parameter, a `Response` object and return
        a new response object.

        """
        self.after_request_funcs.setdefault(None, []).insert(0, f)
        return f

    def teardown_request(self, f):
        """Register a function to be run at the end of each request,
        regardless of whether there was an exception or not.

        Generally teardown functions must take every necessary step to avoid
        that they will fail.  If they do execute code that might fail they
        will have to surround the execution of these code by try/except
        statements and log occurring errors.

        When a teardown function was called because of a exception it will
        be passed an error object.
        """
        self.teardown_request_funcs.setdefault(None, []).insert(0, f)
        return f


    async def handle_http_error(self, request, e):
        """Handles an HTTP exception.  By default this will invoke the
        registered error handlers and fall back to returning the
        exception as response.
        """
        handlers = self.error_handler_spec.get(request.blueprint)
        # Proxy exceptions don't have error codes.  We want to always return
        # those unchanged as errors
        if e.code is None:
            return e
        if handlers and e.code in handlers:
            handler = handlers[e.code]
        else:
            handler = self.error_handler_spec[None].get(e.code)
        if handler is None:
            return e
        return await handler(request, e)

    async def handle_user_exception(self, request, e):
        """This method is called whenever an exception occurs that should be
        handled.  A special case are `~.web.error.HTTPError` which are forwarded by
        this function to the `handle_http_error` method.  This
        function will either return a response value or reraise the
        exception with the same traceback.
        """
        exc_type, exc_value, tb = sys.exc_info()
        assert exc_value is e

        if isinstance(e, HTTPError):
            return await self.handle_http_error(request, e)
        else:
            error = InternalServerError(exc_info=(exc_type, exc_value, tb))
            return await self.handle_http_error(request, error)

    async def handle_exception(self, request, e):
        """Default exception handling that kicks in when an exception
        occurs that is not caught.  In debug mode the exception will
        be re-raised immediately, otherwise it is logged and the handler
        for a 500 internal server error is used.  If no such handler
        exists, a default 500 internal server error message is displayed.
        """
        exc_info = sys.exc_info()
        await logger.error('Exception on %s [%s]' % (
            request.path,
            request.method
        ), exc_info=exc_info)

        return InternalServerError(exc_info=exc_info)

    async def full_dispatch_request(self, request):
        """Dispatches the request and on top of that performs request
        pre and postprocessing as well as HTTP exception catching and
        error handling.
        """
        try:
            req = request
            endpoint, view_args = self.router.match(req.full_path)
            req.endpoint, req.view_args = endpoint, view_args
            rv = await self.preprocess_request(req)
            if rv is None:
                rv = await self.view_functions[req.endpoint](req, **req.view_args)
        except Exception as e:
            await logger.info(f'{req.endpoint}, {req.view_args}')
            await logger.info('%s'%(traceback.format_exc()))
            rv = await self.handle_user_exception(req, e)
            return make_response(rv)
        else:
            response = make_response(rv)
            response = await self.process_response(request, response)
            return response

    async def preprocess_request(self, request):
        """Called before the actual request dispatching and will
        call every as `before_request` decorated function.
        If any of these function returns a value it's handled as
        if it was the return value from the view and further
        request handling is stopped.
        """
        bp = request.blueprint
        funcs = self.before_request_funcs.get(None, ())
        if bp is not None and bp in self.before_request_funcs:
            funcs = chain(funcs, self.before_request_funcs[bp])
        for func in funcs:
            rv = await func(request)
            if rv is not None:
                return rv

    async def process_response(self, request, response):
        """Can be overridden in order to modify the response object
        before it's sent to the ASGI server.  By default this will
        call all the `after_request` decorated functions.

        Args:

          * response: a `Response` object.

        Returns:

          * a new response object or the same, has to be an
                 instance of `Response`.
        """
        bp = request.blueprint
        funcs = []
        if bp is not None and bp in self.after_request_funcs:
            funcs = chain(funcs, self.after_request_funcs[bp])
        if None in self.after_request_funcs:
            funcs = chain(funcs, self.after_request_funcs[None])
        for handler in funcs:
            response = await handler(request, response)
        return response

    async def do_teardown_request(self, request, response, exc=None):
        """Called after the actual request dispatching and will
        call every as `teardown_request` decorated function.
        """
        if exc is None:
            exc = sys.exc_info()[1]
        funcs = self.teardown_request_funcs.get(None, ())
        bp = request.blueprint
        if bp is not None and bp in self.teardown_request_funcs:
            funcs = chain(funcs, self.teardown_request_funcs[bp])
        for func in funcs:
            rv = await func(request, response, exc)

    def dispatch_app(self, path, app):
        if isinstance(path, (str)):
            key = path
            self.dispatch[key] = app
        elif isinstance(path, (list, tuple)):
            for key in path:
                self.dispatch[key] = app
        else:
            raise Exception(f'dispatch path must be str or list[str]')

        _startup = getattr(app, '_startup')
        _shutdown = getattr(app, '_shutdown')
        if isinstance(_startup, (list, tuple)):
            for hook in _startup:
                self.before_start(hook)
        if isinstance(_shutdown, (list, tuple)):
            for hook in _shutdown:
                self.after_stop(hook)

    async def __call__(self, scope, receive, send):
        scope['app'] = self
        path = scope['path']
        if self.dispatch:
            for dispatch_path, app in self.dispatch.items():
                if dispatch_path == path or path.startswith(f'{dispatch_path}/'):
                    await app(scope, receive, send)
                    return
        req = Request(scope, receive)
        error = None
        response = None
        try:
            try:
                response = await self.full_dispatch_request(req)
            except Exception as e:
                await logger.info('%s'%(traceback.format_exc()))
                error = e
                response = make_response(await self.handle_exception(req, e))
            await response(send)
        finally:
            await self.do_teardown_request(req, response, error)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.name,
        )
