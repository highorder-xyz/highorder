# -*- coding: utf-8 -*-
from functools import update_wrapper
from datetime import datetime, timedelta, date
from email.utils import formatdate
import hashlib
import time
import typing
import os
import inspect

from .utils import json, to_bytes, to_unicode, guess_file_mimetype
from .datastructures import HeaderProperty, HeaderDict
from .errors import HTTPError, default_errors
from .request import parse_date, Request
from .types import Receive, Scope, Send
from http.cookies import SimpleCookie
from urllib.parse import quote, quote_plus

from callpy.concurrency import iterate_in_threadpool, run_until_first_complete


import aiofiles
from aiofiles.os import stat as aio_stat
import stat


def http_date(value):
    if isinstance(value, (date, datetime)):
        value = value.utctimetuple()
    elif isinstance(value, (int, float)):
        value = time.gmtime(value)
    if not isinstance(value, str):
        value = time.strftime("%a, %d %b %Y %H:%M:%S GMT", value)
    return value


def html_escape(string):
    """ Escape HTML special characters ``&<>`` and quotes ``'"``. """
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                 .replace('"', '&quot;').replace("'", '&#039;')


def html_quote(string):
    """ Escape and quote a string to be used as an HTTP attribute."""
    return '"%s"' % html_escape(string).replace('\n', '&#10;')\
                    .replace('\r', '&#13;').replace('\t', '&#9;')



def make_response(rv):
    if isinstance(rv, HTTPError):
        rv = Response(to_bytes(rv.get_body()), headers=rv.get_headers(),
                                 status_code=rv.code)
        return rv
    elif isinstance(rv, Response):
        return rv
    elif isinstance(rv, (bytes, str)):
        return Response(rv)
    else:
        raise ValueError('View function returns must be Response or HTTPError, not %s'%(rv))


def redirect(location, code=302):
    """Returns a response object that, if called,
    redirects the client to the target location.  Supported codes are 301,
    302, 303, 305, and 307.
    Args:

      * location: the location the response should redirect to.
      * code: the redirect status code. defaults to 302.
    """
    rv = RedirectResponse(location, status_code=code)
    return rv

def jsonify(*args, **kwargs):
    """Creates a `Response` with the JSON representation of
    the given arguments with an`application/json` mimetype.  The
    arguments to this function are the same as to the `dict`
    constructor.

    """

    indent = None
    separators = (',', ':')
    rv = Response(json.dumps(dict(*args, **kwargs), indent=indent, separators=separators),
        content_type='application/json')
    return rv

def abort(code, *args, **kwargs):
    mapping = default_errors
    if not args and not kwargs and not isinstance(code, int):
        raise HTTPError(description=code)
    if code not in mapping:
        raise LookupError('no exception for %r' % code)
    raise mapping[code](*args, **kwargs)

def text(text, status=200, headers=None):
    if not isinstance(text, (bytes, str, bytearray)):
        raise ValueError('text must be byte,str,bytearray, but <{}> found'.format(type(text)))
    rv = Response(text, status_code=status, headers=headers)
    return rv

def html(html, status=200, headers=None):
    rv = Response(html, status_code=status, headers=headers, content_type="text/html")
    return rv

class Response(object):
    """ Storage class for a response body as well as headers and cookies.
        This class does support dict-like case-insensitive item-access to
        headers, but is NOT a dict. Most notably, iterating over a response
        yields parts of the body and not the headers.

        Args:

          * body: The response body as one of the supported types.
          * status: Either an HTTP status code (e.g. 200) or a status line
                       including the reason phrase (e.g. '200 OK').
          * headers: A dictionary or a list of name-value pairs.

        Additional keyword arguments are added to the list of headers.
        Underscores in the header name are replaced with dashes.
    """

    default_status = 200
    default_content_type = 'text/plain'
    charset = "UTF-8"

    # Header blacklist for specific response codes
    # (rfc2616 section 10.2.3 and 10.3.5)
    bad_headers = {
        204: set(('Content-Type', )),
        304: set(('Allow', 'Content-Encoding', 'Content-Language',
                  'Content-Length', 'Content-Range', 'Content-Type',
                  'Content-Md5', 'Last-Modified'))
    }

    def __init__(self, body="", status_code=None, headers=None, **more_headers):
        self._cookies = None
        self._headers = HeaderDict()
        self.status_code = status_code or self.default_status
        self.body = body
        self.init_headers(headers, more_headers)

    def init_headers(self, headers: typing.Mapping[str, str] = None, more_headers = None) -> None:
        _headers = HeaderDict()
        if headers:
            if isinstance(headers, dict):
                headers = headers.items()
            for name, value in headers:
                _headers.append(name, value)
        if more_headers:
            for name, value in more_headers.items():
                _headers.append(name, value)

        populate_content_length = "content-length" not in _headers
        populate_content_type = "content-type" not in _headers

        raw_body = getattr(self, "body", "")
        if isinstance(raw_body, bytes):
            body = raw_body
        else:
            body = raw_body.encode(self.charset)
        if body and populate_content_length:
            content_length = str(len(body))
            _headers.append("content-length", content_length.encode("latin-1"))

        content_type = self.default_content_type
        if content_type is not None and populate_content_type:
            if content_type.startswith("text/"):
                content_type += "; charset=" + self.charset
            _headers.append("content-type", content_type.encode("latin-1"))

        self._headers = _headers


    def copy(self, cls=None):
        """ Returns a copy of self. """
        cls = cls or Response
        assert issubclass(cls,Response)
        copy = cls()
        copy.status_code = self.status_code
        copy._headers = HeaderDict(self._headers.allitems())
        if self._cookies:
            copy._cookies = SimpleCookie()
            copy._cookies.load(self._cookies.output(header=''))
        copy.body = self.body
        return copy

    def __iter__(self):
        return iter(self.body)

    def close(self):
        if hasattr(self.body, 'close'):
            self.body.close()

    @property
    def status_code(self):
        """ The HTTP status code as an integer (e.g. 404)."""
        return self._status_code

    @status_code.setter
    def status_code(self, code):
        if isinstance(code, str):
            code = int(code.strip())
        elif isinstance(code, int):
            code = code
        else:
            raise ValueError('String status must be valid int, got {}'.format(code))
        if not 100 <= code <= 999:
            raise ValueError('Status code out of range.')
        self._status_code = int(code)

    @property
    def status(self):
        return self.status_code

    @status.setter
    def status(self, status):
        self.status_code = status

    @property
    def headers(self):
        """ An instance of `HeaderDict`, a case-insensitive dict-like
            view on the response headers. """
        return self._headers

    def __contains__(self, name):
        return name in self._headers

    def __delitem__(self, name):
        del self._headers[name]

    def __getitem__(self, name):
        return self._headers[name]

    def __setitem__(self, name, value):
        self._headers[name] = value

    def get_header(self, name, default=None):
        """ Return the value of a previously defined header. If there is no
            header with that name, return a default value. """
        return self._headers.get(name, [default])

    def set_header(self, name, value):
        """ Create a new response header, replacing any previously defined
            headers with the same name. """
        self._headers.replace(name, value)

    def add_header(self, name, value):
        """ Add an additional response header, not removing duplicates. """
        self._headers.append(name, value)

    def iter_headers(self):
        """ Yield (header, value) tuples, skipping headers that are not
            allowed with the current response status code. """
        return self.headerlist

    @property
    def headerlist(self):
        out = []
        headers = list(self._headers.allitems())
        if 'Content-Type' not in self._headers:
            headers.append(('Content-Type', self.default_content_type))
        #headers.append(('Server', 'CallPy %s'%(server_version)))
        if self._status_code in self.bad_headers:
            bad_headers = self.bad_headers[self._status_code]
            headers = [h for h in headers if h[0] not in bad_headers]
        out.extend(headers)
        if self._cookies:
            for c in self._cookies.values():
                out.append(('Set-Cookie', c.OutputString()))
        return [(k, v.encode('utf8').decode('latin1')) for (k, v) in out]

    content_type = HeaderProperty('Content-Type')
    content_length = HeaderProperty('Content-Length', reader=int)
    expires = HeaderProperty(
        'Expires',
        reader=lambda x: datetime.utcfromtimestamp(parse_date(x)),
        writer=lambda x: http_date(x))

    @property
    def charset(self, default='UTF-8'):
        """ Return the charset specified in the content-type header (default: utf8). """
        if 'charset=' in self.content_type:
            return self.content_type.split('charset=')[-1].split(';')[0].strip()
        return default

    def set_cookie(self, name, value, secret=None, **options):
        """ Create a new cookie or replace an old one. If the `secret` parameter is
            set, create a `Signed Cookie` (described below).

            Args:

              * name: the name of the cookie.
              * value: the value of the cookie.
              * secret: a signature key required for signed cookies.

            Additionally, this method accepts all RFC 2109 attributes that are
            supported by `cookie.Morsel`, including:

              * max_age: maximum age in seconds. (default: None)
              * expires: a datetime object or UNIX timestamp. (default: None)
              * domain: the domain that is allowed to read the cookie. (default: current domain)
              * path: limits the cookie to a given path (default: current path)
              * secure: limit the cookie to HTTPS connections (default: off).
              * httponly: prevents client-side javascript to read this cookie (default: off).

            If neither `expires` nor `max_age` is set (default), the cookie will
            expire at the end of the browser session (as soon as the browser
            window is closed).
            Signed cookies may store any pickle-able object and are
            cryptographically signed to prevent manipulation. Keep in mind that
            cookies are limited to 4kb in most browsers.
            Warning: Signed cookies are not encrypted (the client can still see
            the content) and not copy-protected (the client can restore an old
            cookie). The main intention is to make pickling and unpickling
            save, not to store secret information at client side.
        """
        if not self._cookies:
            self._cookies = SimpleCookie()

        if secret:
            pass
            #value = to_unicode(cookie_encode((name, value), secret))
        elif not isinstance(value, str):
            raise TypeError('Secret key missing for non-string Cookie.')

        if len(value) > 4096: raise ValueError('Cookie value to long.')
        self._cookies[name] = value

        for key, value in options.items():
            if key == 'max_age':
                if isinstance(value, timedelta):
                    value = value.seconds + value.days * 24 * 3600
            if key == 'expires':
                if isinstance(value, (date, datetime)):
                    value = value.timetuple()
                elif isinstance(value, (int, float)):
                    value = time.gmtime(value)
                value = time.strftime("%a, %d %b %Y %H:%M:%S GMT", value)
            if key in ('secure', 'httponly') and not value:
                continue
            self._cookies[name][key.replace('_', '-')] = value

    def delete_cookie(self, key, **kwargs):
        """ Delete a cookie. Be sure to use the same `domain` and `path`
            settings as used to create the cookie. """
        kwargs['max_age'] = -1
        kwargs['expires'] = 0
        self.set_cookie(key, '', **kwargs)

    def __repr__(self):
        out = ''
        for name, value in self.headerlist:
            out += '%s: %s\n' % (name.title(), value.strip())
        return out

    def raw_headers(self):
        headers = list(map(lambda x: [to_bytes(x[0]), to_bytes(x[1])], self.headerlist))
        return  headers

    async def __call__(self, send):
        headers = list(map(lambda x: [to_bytes(x[0]), to_bytes(x[1])], self.headerlist))
        await send({"type": "http.response.start", "status": self.status_code, "headers": headers})
        if isinstance(self.body, list):
            body = b"".join(list(map(lambda x: to_bytes(x), body)))
        else:
            body = to_bytes(self.body)
        await send({"type": "http.response.body", "body":body, "more_body": False})


class RedirectResponse(Response):
    code = 301

    def __init__(self, new_url, status_code: int=302, headers: dict = None):
        self.new_url = new_url
        super().__init__(
            body=self.get_body(), status_code=status_code, headers=self.get_headers()
        )


    def get_headers(self):
        return [('Location', quote_plus(str(self.new_url), safe=":/%#?&=@[]!$&'()*+,;")),
                ('Content-Type', 'text/html')]

    def get_body(self):
        display_location = html_escape(self.new_url)
        body = str((
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
            '<title>Redirecting...</title>\n'
            '<h1>Redirecting...</h1>\n'
            '<p>You should be redirected automatically to target URL: '
            '<a href="%s">%s</a>.  If not click the link.') % (html_escape(self.new_url), display_location))
        return body

class StreamingResponse(Response):
    def __init__(
        self,
        request: Request,
        body: typing.Any,
        status_code: int = 200,
        headers: dict = None
    ) -> None:
        if inspect.isasyncgen(body):
            self.body_iterator = body
        else:
            self.body_iterator = iterate_in_threadpool(body)

        self.status_code = status_code
        super().__init__(
            body='', status_code=status_code, headers=headers
        )
        self.request = request

    async def listen_for_disconnect(self) -> None:
        while True:
            message = await self.request._receive()
            if message["type"] == "http.disconnect":
                break

    async def stream_response(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers(),
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def __call__(self, send: Send) -> None:
        await run_until_first_complete(
            (self.stream_response, {"send": send}),
            (self.listen_for_disconnect),
        )



class FileResponse(Response):
    chunk_size = 4096

    def __init__(
        self,
        path: str,
        status_code: int = 200,
        headers: dict = {},
        filename: str = None,
        stat_result: os.stat_result = None,
        method: str = None,
    ) -> None:
        assert aiofiles is not None, "'aiofiles' must be installed to use FileResponse"
        self.path = path
        self.status_code = status_code
        self.filename = filename
        self.send_header_only = method is not None and method.upper() == "HEAD"
        more_headers = {}

        if 'content-type' not in headers:
            content_type = guess_file_mimetype(filename or path) or "text/plain"
            more_headers['content_type'] = content_type

        super().__init__(
            body='', status_code=status_code, headers=headers, **more_headers
        )

        if self.filename is not None:
            content_disposition_filename = quote(self.filename)
            if content_disposition_filename != self.filename:
                content_disposition = "attachment; filename*=utf-8''{}".format(
                    content_disposition_filename
                )
            else:
                content_disposition = 'attachment; filename="{}"'.format(self.filename)
            self.headers.setdefault("content-disposition", content_disposition)
        self.stat_result = stat_result
        if stat_result is not None:
            self.set_stat_headers(stat_result)

    def set_stat_headers(self, stat_result: os.stat_result) -> None:
        content_length = str(stat_result.st_size)
        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = hashlib.md5(etag_base.encode()).hexdigest()

        self.headers.setdefault("content-length", content_length)
        self.headers.setdefault("last-modified", last_modified)
        self.headers.setdefault("etag", etag)

    async def __call__(self, send: Send) -> None:
        if self.stat_result is None:
            try:
                stat_result = await aio_stat(self.path)
                self.set_stat_headers(stat_result)
            except FileNotFoundError:
                raise RuntimeError(f"File at path {self.path} does not exist.")
            else:
                mode = stat_result.st_mode
                if not stat.S_ISREG(mode):
                    raise RuntimeError(f"File at path {self.path} is not a file.")
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers(),
            }
        )
        if self.send_header_only:
            await send({"type": "http.response.body", "body": b"", "more_body": False})
        else:
            async with aiofiles.open(self.path, mode="rb") as file:
                more_body = True
                while more_body:
                    chunk = await file.read(self.chunk_size)
                    more_body = len(chunk) == self.chunk_size
                    await send(
                        {
                            "type": "http.response.body",
                            "body": chunk,
                            "more_body": more_body,
                        }
                    )
