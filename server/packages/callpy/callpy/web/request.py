# -*- coding: utf-8 -*-
import sys
from functools import update_wrapper
from datetime import datetime, timedelta
import typing
import email
import email.utils
import base64
import time
import http.cookies
import json
import typing
from collections.abc import Mapping
import asyncio

from .datastructures import URL, FormData, Headers, QueryParams
from .types import Message, Receive, Scope, Send
from .errors import HTTPError, BadRequest
from .utils import cached_property
from .datastructures import MultiDict, FormsDict, HeaderDict
from .formparsers import FormParser, MultiPartParser, parse_options_header
from io import StringIO, BytesIO
from http.cookies import SimpleCookie
from .utils import (to_unicode, to_bytes, urlencode, urldecode, urlquote, urljoin, json)

from .errors import BadRequest

MEMFILE_MAX = 4*1024*1024


SERVER_PUSH_HEADERS_TO_COPY = {
    "accept",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "user-agent",
}


def parse_date(ims):
    """ Parse rfc1123, rfc850 and asctime timestamps and return UTC epoch. """
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0, )) - (ts[9] or 0) - time.timezone
    except (TypeError, ValueError, IndexError, OverflowError):
        return None


def parse_auth(header):
    """ Parse rfc2617 HTTP authentication header string (basic) and return (user,pass) tuple or None"""
    try:
        method, data = header.split(None, 1)
        if method.strip().lower() == b'basic':
            user, pwd = base64.b64decode(data).split(b':', 1)
            return to_unicode(user), to_unicode(pwd)
    except (KeyError, ValueError, Exception):
        return None


def parse_range_header(header, maxlen=0):
    """ Yield (start, end) ranges parsed from a HTTP Range header. Skip
        unsatisfiable ranges. The end index is non-inclusive."""
    if not header or header[:6] != 'bytes=': return
    ranges = [r.split('-', 1) for r in header[6:].split(',') if '-' in r]
    for start, end in ranges:
        try:
            if not start:  # bytes=-100    -> last 100 bytes
                start, end = max(0, maxlen - int(end)), maxlen
            elif not end:  # bytes=100-    -> all but the first 99 bytes
                start, end = int(start), maxlen
            else:  # bytes=100-200 -> bytes 100-200 (inclusive)
                start, end = int(start), min(int(end) + 1, maxlen)
            if 0 <= start < end <= maxlen:
                yield start, end
        except ValueError:
            pass

def parse_content_type(content_type):
    parts = to_unicode(content_type).split(';')
    params = {}
    for part in parts[1:]:
        if '=' not in part:
            break
        k, v = part.strip().split('=', 1)
        params[k] = v
    return (parts[0], params)

class ClientDisconnect(Exception):
    pass

async def empty_receive() -> Message:
    raise RuntimeError("Receive channel has not been made available")


async def empty_send(message: Message) -> None:
    raise RuntimeError("Send channel has not been made available")


class Request(object):
    """
    """

    #: the charset for the request, defaults to utf-8
    charset = 'utf-8'

    #: the error handling procedure for errors, defaults to 'replace'
    encoding_errors = 'replace'

    endpoint = ''

    #: a dict of view arguments that matched the request.  If an exception
    #: happened when matching, this will be `None`.
    view_args = None

    def __init__(self, scope, receive=empty_receive, send=empty_send, populate_request=True):
        self.scope = scope
        self._receive = receive
        self._send = send
        self._stream_consumed = False
        self._is_disconnected = False
        if populate_request:
            self.scope['callpy.request'] = self

    def __repr__(self):
        args = []
        try:
            args.append("'%s'" % to_unicode(self.url, self.url_charset))
            args.append('[%s]' % self.method)
        except Exception:
            args.append('(invalid ASGI scope )')

        return '<%s %s>' % (
            self.__class__.__name__,
            ' '.join(args)
        )

    @property
    def url_charset(self):
        """The charset that is assumed for URLs.  Defaults to the value
        of `charset`.

        """
        return self.charset

    @cached_property
    def args(self):
        query_string = self.query_string
        if query_string:
            return MultiDict(urldecode(query_string))
        else:
            return MultiDict()

    @cached_property
    def chunked(self):
        """ True if Chunked transfer encoding was. """
        return 'chunked' in self.headers.get('transfer-encoding', '').lower()

    async def stream(self) -> typing.AsyncGenerator[bytes, None]:
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return

        if self._stream_consumed:
            raise RuntimeError("Stream consumed")

        self._stream_consumed = True
        while True:
            message = await self._receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    yield body
                if not message.get("more_body", False):
                    break
            elif message["type"] == "http.disconnect":
                self._is_disconnected = True
                raise ClientDisconnect()
        yield b""

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> typing.Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json

    async def form(self) -> FormData:
        if not hasattr(self, "_form"):
            content_type_header = self.headers.get("Content-Type")
            content_type, options = parse_options_header(content_type_header)
            if content_type == b"multipart/form-data":
                multipart_parser = MultiPartParser(self.headers, self.stream())
                self._form = await multipart_parser.parse()
            elif content_type == b"application/x-www-form-urlencoded":
                form_parser = FormParser(self.headers, self.stream())
                self._form = await form_parser.parse()
            else:
                self._form = FormData()
        return self._form

    async def close(self) -> None:
        if hasattr(self, "_form"):
            await self._form.close()

    async def is_disconnected(self) -> bool:
        if not self._is_disconnected:
            try:
                message = await asyncio.wait_for(self._receive(), timeout=0.0000001)
            except asyncio.TimeoutError:
                message = {}

            if message.get("type") == "http.disconnect":
                self._is_disconnected = True

        return self._is_disconnected

    async def send_push_promise(self, path: str) -> None:
        if "http.response.push" in self.scope.get("extensions", {}):
            raw_headers = []
            for name in SERVER_PUSH_HEADERS_TO_COPY:
                for value in self.headers.getlist(name):
                    raw_headers.append(
                        (name.encode("latin-1"), value.encode("latin-1"))
                    )
            await self._send(
                {"type": "http.response.push", "path": path, "headers": raw_headers}
            )

    def get_host(self):
        headers = self.headers
        if 'x-forwarded-host' in headers:
            rv = headers['x-forwarded-host'].split(',', 1)[0].strip()
        elif 'host' in headers:
            rv = headers['host']
        else:
            rv, port = self.scope['server']
            if (self.scope['type'], port) not \
               in (('https', '443'), ('http', '80')):
                rv += ':%s'%(port)
        return rv


    def get_content_length(self):
        """Returns the content length from the headers as
        integer.  If it's not available `None` is returned.
        """
        content_length = self.headers.get('content-length')
        if content_length is not None:
            try:
                return max(0, int(content_length))
            except (ValueError, TypeError):
                pass
        return 0

    def get_current_url(self, root_only=False, strip_querystring=False, host_only=False):
        """A handy helper function that recreates the full URL as IRI for the
        current request or parts of it.  Here an example:

            >>> get_current_url()
            'http://localhost/script/?param=foo'
            >>> get_current_url(root_only=True)
            'http://localhost/script/'
            >>> get_current_url(host_only=True)
            'http://localhost/'
            >>> get_current_url(strip_querystring=True)
            'http://localhost/script/'

        """
        scope = self.scope
        tmp = [scope['type'], '://', self.get_host()]
        cat = tmp.append
        if host_only:
            return ''.join(tmp) + '/'
        cat(urlquote(scope.get('root_path', '')).rstrip('/'))
        cat('/')
        if not root_only:
            cat(urlquote(scope.get('path', '').lstrip('/')))
            if not strip_querystring:
                qs = self.query_string
                if qs:
                    cat('?' + qs)
        return ''.join(tmp)

    @cached_property
    def cookies(self):
        """Read only access to the retrieved cookie values as dictionary."""
        cookies = SimpleCookie(self.headers.get('cookie')).values()
        return FormsDict((c.key, c.value) for c in cookies)

    def get_cookie(self, key):
        """ Return the content of a cookie. """
        value = self.cookies.get(key)
        return value

    @cached_property
    def headers(self):
        return HeaderDict(list(map(lambda x: [to_unicode(x[0]), to_unicode(x[1])], self.scope['headers'])))

    @cached_property
    def path(self):
        """Requested path as unicode.  This works a bit like the regular path
        info but will always include a leading slash, even if the URL root is accessed.
        """
        return '/' + self.scope.get('path', '').lstrip('/')

    @property
    def script_name(self):
        """ The initial portion of the URL's `path` that was removed by a higher
            level (server or routing middleware) before the application was
            called. This script path is returned with leading and tailing
            slashes. """
        script_name = self.scope.get('root_path', '').strip('/')
        return '/' + script_name + '/' if script_name else ''

    @property
    def full_path(self):
        """Requested path as unicode, including the query string."""
        root_path = self.scope.get('root_path', '')
        path = self.scope.get('path', '')
        return '{}{}'.format(root_path, path)

    @cached_property
    def script_root(self):
        """The root path of the script without the trailing slash."""
        raw_path = to_unicode(self.scope.get('root_path') or '',
                                       self.charset, self.encoding_errors)
        return raw_path.rstrip('/')

    @cached_property
    def url(self):
        """The reconstructed current URL as IRI.
        """
        return self.get_current_url()

    @cached_property
    def base_url(self):
        """Like `url` but without the querystring
        """
        return self.get_current_url(strip_querystring=True)

    @cached_property
    def root_url(self):
        """The full URL root (with hostname), this is the application
        root as IRI.
        """
        return self.get_current_url(root_only=True)

    @cached_property
    def host_url(self):
        """Just the host with scheme as IRI.
        """
        return self.get_current_url(host_only=True)

    @cached_property
    def host(self):
        """Just the host including the port if available.
        """
        return self.get_host()

    @property
    def query_string(self):
        return to_unicode(self.scope.get('query_string', ''))

    @property
    def method(self):
        return self.scope.get('method', 'GET').upper()

    @cached_property
    def access_route(self):
        """If a forwarded header exists this is a list of all ip addresses
        from the client ip to the last proxy server.
        """
        headers = self.headers
        if 'x-forwarded-for' in headers:
            addr = headers['x-forwarded-for'].split(',')
            return list([x.strip() for x in addr])
        elif 'client' in self.scope:
            return list([self.scope['client'][0]])
        return list()

    remote_route = access_route

    @property
    def remote_addr(self):
        """The remote address of the client."""
        route = self.access_route
        return route[0] if route else None


    is_xhr = property(lambda x: x.headers.get('x-requested-with', '')
                      .lower() == 'xmlhttprequest', doc='''
        True if the request was triggered via a JavaScript XMLHttpRequest.
        This only works with libraries that support the `X-Requested-With`
        header and set it to "XMLHttpRequest".  Libraries that do that are
        prototype, jQuery and Mochikit and probably some more.''')
    is_secure = property(lambda x: x.scope['type'] == 'https',
                         doc='`True` if the request is secure.')


    @cached_property
    def if_modified_since(self):
        """The parsed `If-Modified-Since` header as datetime object."""
        return parse_date(self.headers.get('if-modified-since'))

    @cached_property
    def if_unmodified_since(self):
        """The parsed `If-Unmodified-Since` header as datetime object."""
        return parse_date(self.headers.get('if-unmodified-since'))


    @cached_property
    def range(self):
        """The parsed `Range` header.
        """
        return parse_range_header(self.headers.get('range'))


    @cached_property
    def authorization(self):
        header = self.headers.get('Authorization')
        if not header: return None
        return parse_auth(header.encode('ascii'))

    @property
    def content_type(self):
        return self.headers.get('content-type', '')


    @cached_property
    def content_length(self):
        """The Content-Length entity-header field indicates the size of the
        entity-body in bytes or, in the case of the HEAD method, the size of
        the entity-body that would have been sent had the request been a
        GET.
        """
        return self.get_content_length()

    @cached_property
    def parsed_content_type(self):
        return parse_content_type(self.headers.get('content-type', ''))

    @property
    def mimetype(self):
        """Like `content_type` but without parameters (eg, without
        charset, type etc.).  For example if the content
        type is ``text/html; charset=utf-8`` the mimetype would be
        ``'text/html'``.
        """
        return self.parsed_content_type[0]

    @property
    def mimetype_params(self):
        """The mimetype parameters as dict.  For example if the content
        type is ``text/html; charset=utf-8`` the params would be
        ``{'charset': 'utf-8'}``.
        """
        return self.parsed_content_type[1]

    @property
    def blueprint(self):
        """The name of the current blueprint"""
        if '.' in self.endpoint:
            return self.endpoint.rsplit('.', 1)[0]
