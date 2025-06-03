# -*- coding: utf-8 -*-
import re
import os
import sys
import codecs
import mimetypes
from copy import deepcopy
from itertools import repeat
from collections.abc import MutableMapping
from unicodedata import normalize
from .utils import cached_property, to_unicode
import tempfile
import typing
from collections.abc import Sequence
from shlex import shlex
from urllib.parse import SplitResult, parse_qsl, urlencode, urlsplit

from callpy.concurrency import run_in_threadpool
from .types import Scope

def _hkey(s):
    return s.title().replace('_', '-')


class MultiDict(MutableMapping):
    """ This dict stores multiple values per key, but behaves exactly like a
        normal dict in that it returns only the newest value for any given key.
        There are special methods available to access the full list of values.

        Basic Usage:

            >>> d = MultiDict([('a', 'b'), ('a', 'c')])
            >>> d
            MultiDict([('a', 'b'), ('a', 'c')])
            >>> d['a']
            'b'
            >>> d.getlist('a')
            ['b', 'c']
            >>> 'a' in d
            True
    """

    def __init__(self, *a, **kwargs):
        self.dict = {}
        for pl in a:
            for k, v in pl:
                l = self.dict.setdefault(k, [])
                l.append(v)
        for k, v in kwargs.items():
            l = self.dict.setdefault(k, [])
            l.append(v)

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def __delitem__(self, key):
        del self.dict[key]

    def __getitem__(self, key):
        return self.dict[key][0]

    def __setitem__(self, key, value):
        self.append(key, value)

    def keys(self):
        return self.dict.keys()

    def values(self):
        return (v[0] for v in self.dict.values())

    def items(self):
        return ((k, v[0]) for k, v in self.dict.items())

    def allitems(self):
        return ((k, v) for k, vl in self.dict.items() for v in vl)

    iterkeys = keys
    itervalues = values
    iteritems = items
    iterallitems = allitems


    def get(self, key, default=None, index=0, type=None):
        """ Return the most recent value for a key.
            Args:

              * default: The default value to be returned if the key is not
                   present or the type conversion fails.
              * index: An index for the list of available values.
              * type: If defined, this callable is used to cast the value
                    into a specific type. Exception are suppressed and result in
                    the default value to be returned.
        """
        try:
            val = self.dict[key][index]
            return type(val) if type else val
        except Exception:
            pass
        return default

    def append(self, key, value):
        """ Add a new value to the list of values for this key. """
        self.dict.setdefault(key, []).append(value)

    def replace(self, key, value):
        """ Replace the list of values with a single value. """
        self.dict[key] = [value]

    def getall(self, key):
        """ Return a (possibly empty) list of values for a key. """
        return self.dict.get(key) or []

    #: Aliases for WTForms to mimic other multi-dict APIs (Django)
    getone = get
    getlist = getall


class FormsDict(MultiDict):
    """ This `MultiDict` subclass is used to store request form data.
        Additionally to the normal dict-like item access methods (which return
        unmodified data as native strings), this container also supports
        attribute-like access to its values. Attributes are automatically de-
        or recoded to match `input_encoding` (default: 'utf8'). Missing
        attributes default to an empty string. """

    #: Encoding used for attribute values.
    input_encoding = 'utf8'
    #: If true (default), unicode strings are first encoded with `latin1`
    #: and then decoded to match `input_encoding`.
    recode_unicode = True

    def _fix(self, s, encoding=None):
        if isinstance(s, str) and self.recode_unicode:  # Python 3 WSGI
            return s.encode('latin1').decode(encoding or self.input_encoding)
        elif isinstance(s, bytes):  # Python 2 WSGI
            return s.decode(encoding or self.input_encoding)
        else:
            return s

    def getunicode(self, name, default=None, encoding=None):
        """ Return the value as a unicode string, or the default. """
        try:
            return self._fix(self[name], encoding)
        except (UnicodeError, KeyError):
            return default

    def __getattr__(self, name, default=str()):
        # Without this guard, pickle generates a cryptic TypeError:
        if name.startswith('__') and name.endswith('__'):
            return super(FormsDict, self).__getattr__(name)
        return self.getunicode(name, default=default)


class HeaderDict(MultiDict):
    """ A case-insensitive version of `MultiDict` that defaults to
        replace the old value instead of appending it. """

    def __init__(self, *a, **ka):
        self.dict = {}
        if a or ka: self.update(*a, **ka)

    def __contains__(self, key):
        return _hkey(key) in self.dict

    def __delitem__(self, key):
        del self.dict[_hkey(key)]

    def __getitem__(self, key):
        return self.dict[_hkey(key)][0]

    def __setitem__(self, key, value):
        if not isinstance(value, (int, float, str, bytes)):
            raise ValueError('value must be string, got {}, type: {}'.format(value, type(value)))
        self.dict[_hkey(key)] = [value if isinstance(value, str) else
                                 to_unicode(value)]

    def append(self, key, value):
        if not isinstance(value, (int, float, str, bytes)):
            raise ValueError('value must be string, got {}, type: {}'.format(value, type(value)))
        self.dict.setdefault(_hkey(key), []).append(
            value if isinstance(value, str) else to_unicode(value))

    def replace(self, key, value):
        if not isinstance(value, (int, float, str, bytes)):
            raise ValueError('value must be string, got {}, type: {}'.format(value, type(value)))
        self.dict[_hkey(key)] = [value if isinstance(value, str) else
                                 to_unicode(value)]

    def getall(self, key):
        return self.dict.get(_hkey(key)) or []

    def get(self, key, default=None, index=0):
        return MultiDict.get(self, _hkey(key), default, index)


class HeaderProperty(object):
    def __init__(self, name, reader=None, writer=str, default=''):
        self.name, self.default = name, default
        self.reader, self.writer = reader, writer
        self.__doc__ = 'Current value of the %r header.' % name.title()

    def __get__(self, obj, _):
        if obj is None: return self
        value = obj.headers.get(self.name, self.default)
        return self.reader(value) if self.reader else value

    def __set__(self, obj, value):
        obj.headers[self.name] = self.writer(value)

    def __delete__(self, obj):
        del obj.headers[self.name]

class URL:
    def __init__(
        self, url: str = "", scope: Scope = None, **components: typing.Any
    ) -> None:
        if scope is not None:
            assert not url, 'Cannot set both "url" and "scope".'
            assert not components, 'Cannot set both "scope" and "**components".'
            scheme = scope.get("scheme", "http")
            server = scope.get("server", None)
            path = scope.get("root_path", "") + scope["path"]
            query_string = scope.get("query_string", b"")

            host_header = None
            for key, value in scope["headers"]:
                if key == b"host":
                    host_header = value.decode("latin-1")
                    break

            if host_header is not None:
                url = f"{scheme}://{host_header}{path}"
            elif server is None:
                url = path
            else:
                host, port = server
                default_port = {"http": 80, "https": 443, "ws": 80, "wss": 443}[scheme]
                if port == default_port:
                    url = f"{scheme}://{host}{path}"
                else:
                    url = f"{scheme}://{host}:{port}{path}"

            if query_string:
                url += "?" + query_string.decode()
        elif components:
            assert not url, 'Cannot set both "url" and "**components".'
            url = URL("").replace(**components).components.geturl()

        self._url = url

    @property
    def components(self) -> SplitResult:
        if not hasattr(self, "_components"):
            self._components = urlsplit(self._url)
        return self._components

    @property
    def scheme(self) -> str:
        return self.components.scheme

    @property
    def netloc(self) -> str:
        return self.components.netloc

    @property
    def path(self) -> str:
        return self.components.path

    @property
    def query(self) -> str:
        return self.components.query

    @property
    def fragment(self) -> str:
        return self.components.fragment

    @property
    def username(self) -> typing.Union[None, str]:
        return self.components.username

    @property
    def password(self) -> typing.Union[None, str]:
        return self.components.password

    @property
    def hostname(self) -> typing.Union[None, str]:
        return self.components.hostname

    @property
    def port(self) -> typing.Optional[int]:
        return self.components.port

    @property
    def is_secure(self) -> bool:
        return self.scheme in ("https", "wss")

    def replace(self, **kwargs: typing.Any) -> "URL":
        if (
            "username" in kwargs
            or "password" in kwargs
            or "hostname" in kwargs
            or "port" in kwargs
        ):
            hostname = kwargs.pop("hostname", self.hostname)
            port = kwargs.pop("port", self.port)
            username = kwargs.pop("username", self.username)
            password = kwargs.pop("password", self.password)

            netloc = hostname
            if port is not None:
                netloc += f":{port}"
            if username is not None:
                userpass = username
                if password is not None:
                    userpass += f":{password}"
                netloc = f"{userpass}@{netloc}"

            kwargs["netloc"] = netloc

        components = self.components._replace(**kwargs)
        return self.__class__(components.geturl())

    def include_query_params(self, **kwargs: typing.Any) -> "URL":
        params = MutableMultiDict(parse_qsl(self.query, keep_blank_values=True))
        params.update({str(key): str(value) for key, value in kwargs.items()})
        query = urlencode(params.multi_items())
        return self.replace(query=query)

    def replace_query_params(self, **kwargs: typing.Any) -> "URL":
        query = urlencode([(str(key), str(value)) for key, value in kwargs.items()])
        return self.replace(query=query)

    def remove_query_params(
        self, keys: typing.Union[str, typing.Sequence[str]]
    ) -> "URL":
        if isinstance(keys, str):
            keys = [keys]
        params = MutableMultiDict(parse_qsl(self.query, keep_blank_values=True))
        for key in keys:
            params.pop(key, None)
        query = urlencode(params.multi_items())
        return self.replace(query=query)

    def __eq__(self, other: typing.Any) -> bool:
        return str(self) == str(other)

    def __str__(self) -> str:
        return self._url

    def __repr__(self) -> str:
        url = str(self)
        if self.password:
            url = str(self.replace(password="********"))
        return f"{self.__class__.__name__}({repr(url)})"


class URLPath(str):
    """
    A URL path string that may also hold an associated protocol and/or host.
    Used by the routing to return `url_path_for` matches.
    """

    def __new__(cls, path: str, protocol: str = "", host: str = "") -> "URLPath":
        assert protocol in ("http", "websocket", "")
        return str.__new__(cls, path)  # type: ignore

    def __init__(self, path: str, protocol: str = "", host: str = "") -> None:
        self.protocol = protocol
        self.host = host

    def make_absolute_url(self, base_url: typing.Union[str, URL]) -> str:
        if isinstance(base_url, str):
            base_url = URL(base_url)
        if self.protocol:
            scheme = {
                "http": {True: "https", False: "http"},
                "websocket": {True: "wss", False: "ws"},
            }[self.protocol][base_url.is_secure]
        else:
            scheme = base_url.scheme

        if self.host:
            netloc = self.host
        else:
            netloc = base_url.netloc

        path = base_url.path.rstrip("/") + str(self)
        return str(URL(scheme=scheme, netloc=netloc, path=path))


class Secret:
    """
    Holds a string value that should not be revealed in tracebacks etc.
    You should cast the value to `str` at the point it is required.
    """

    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}('**********')"

    def __str__(self) -> str:
        return self._value


class CommaSeparatedStrings(Sequence):
    def __init__(self, value: typing.Union[str, typing.Sequence[str]]):
        if isinstance(value, str):
            splitter = shlex(value, posix=True)
            splitter.whitespace = ","
            splitter.whitespace_split = True
            self._items = [item.strip() for item in splitter]
        else:
            self._items = list(value)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: typing.Union[int, slice]) -> typing.Any:
        return self._items[index]

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self._items)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = [item for item in self]
        return f"{class_name}({items!r})"

    def __str__(self) -> str:
        return ", ".join([repr(item) for item in self])


class ImmutableMultiDict(typing.Mapping):
    def __init__(
        self,
        *args: typing.Union[
            "ImmutableMultiDict",
            typing.Mapping,
            typing.List[typing.Tuple[typing.Any, typing.Any]],
        ],
        **kwargs: typing.Any,
    ) -> None:
        assert len(args) < 2, "Too many arguments."

        if args:
            value = args[0]
        else:
            value = []

        if kwargs:
            value = (
                ImmutableMultiDict(value).multi_items()
                + ImmutableMultiDict(kwargs).multi_items()
            )

        if not value:
            _items = []  # type: typing.List[typing.Tuple[typing.Any, typing.Any]]
        elif hasattr(value, "multi_items"):
            value = typing.cast(ImmutableMultiDict, value)
            _items = list(value.multi_items())
        elif hasattr(value, "items"):
            value = typing.cast(typing.Mapping, value)
            _items = list(value.items())
        else:
            value = typing.cast(
                typing.List[typing.Tuple[typing.Any, typing.Any]], value
            )
            _items = list(value)

        self._dict = {k: v for k, v in _items}
        self._list = _items

    def getlist(self, key: typing.Any) -> typing.List[str]:
        return [item_value for item_key, item_value in self._list if item_key == key]

    def keys(self) -> typing.KeysView:
        return self._dict.keys()

    def values(self) -> typing.ValuesView:
        return self._dict.values()

    def items(self) -> typing.ItemsView:
        return self._dict.items()

    def multi_items(self) -> typing.List[typing.Tuple[str, str]]:
        return list(self._list)

    def get(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        if key in self._dict:
            return self._dict[key]
        return default

    def __getitem__(self, key: typing.Any) -> str:
        return self._dict[key]

    def __contains__(self, key: typing.Any) -> bool:
        return key in self._dict

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._dict)

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return sorted(self._list) == sorted(other._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = self.multi_items()
        return f"{class_name}({items!r})"


class MutableMultiDict(ImmutableMultiDict):
    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        self.setlist(key, [value])

    def __delitem__(self, key: typing.Any) -> None:
        self._list = [(k, v) for k, v in self._list if k != key]
        del self._dict[key]

    def pop(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        self._list = [(k, v) for k, v in self._list if k != key]
        return self._dict.pop(key, default)

    def popitem(self) -> typing.Tuple:
        key, value = self._dict.popitem()
        self._list = [(k, v) for k, v in self._list if k != key]
        return key, value

    def poplist(self, key: typing.Any) -> typing.List:
        values = [v for k, v in self._list if k == key]
        self.pop(key)
        return values

    def clear(self) -> None:
        self._dict.clear()
        self._list.clear()

    def setdefault(self, key: typing.Any, default: typing.Any = None) -> typing.Any:
        if key not in self:
            self._dict[key] = default
            self._list.append((key, default))

        return self[key]

    def setlist(self, key: typing.Any, values: typing.List) -> None:
        if not values:
            self.pop(key, None)
        else:
            existing_items = [(k, v) for (k, v) in self._list if k != key]
            self._list = existing_items + [(key, value) for value in values]
            self._dict[key] = values[-1]

    def append(self, key: typing.Any, value: typing.Any) -> None:
        self._list.append((key, value))
        self._dict[key] = value

    def update(
        self,
        *args: typing.Union[
            "MutableMultiDict",
            typing.Mapping,
            typing.List[typing.Tuple[typing.Any, typing.Any]],
        ],
        **kwargs: typing.Any,
    ) -> None:
        value = MutableMultiDict(*args, **kwargs)
        existing_items = [(k, v) for (k, v) in self._list if k not in value.keys()]
        self._list = existing_items + value.multi_items()
        self._dict.update(value)


class QueryParams(ImmutableMultiDict):
    """
    An immutable multidict.
    """

    def __init__(
        self,
        *args: typing.Union[
            "ImmutableMultiDict",
            typing.Mapping,
            typing.List[typing.Tuple[typing.Any, typing.Any]],
            str,
            bytes,
        ],
        **kwargs: typing.Any,
    ) -> None:
        assert len(args) < 2, "Too many arguments."

        value = args[0] if args else []

        if isinstance(value, str):
            super().__init__(parse_qsl(value, keep_blank_values=True), **kwargs)
        elif isinstance(value, bytes):
            super().__init__(
                parse_qsl(value.decode("latin-1"), keep_blank_values=True), **kwargs
            )
        else:
            super().__init__(*args, **kwargs)  # type: ignore
        self._list = [(str(k), str(v)) for k, v in self._list]
        self._dict = {str(k): str(v) for k, v in self._dict.items()}

    def __str__(self) -> str:
        return urlencode(self._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        query_string = str(self)
        return f"{class_name}({query_string!r})"


class UploadFile:
    """
    An uploaded file included as part of the request data.
    """

    spool_max_size = 4 * 1024 * 1024

    def __init__(
        self, filename: str, file: typing.IO = None, content_type: str = ""
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        if file is None:
            file = tempfile.SpooledTemporaryFile(max_size=self.spool_max_size)
        self.file = file

    async def write(self, data: typing.Union[bytes, str]) -> None:
        await run_in_threadpool(self.file.write, data)

    async def read(self, size: int = None) -> typing.Union[bytes, str]:
        return await run_in_threadpool(self.file.read, size)

    async def seek(self, offset: int) -> None:
        await run_in_threadpool(self.file.seek, offset)

    async def close(self) -> None:
        await run_in_threadpool(self.file.close)


class FormData(ImmutableMultiDict):
    """
    An immutable multidict, containing both file uploads and text input.
    """

    def __init__(
        self,
        *args: typing.Union[
            "FormData",
            typing.Mapping[str, typing.Union[str, UploadFile]],
            typing.List[typing.Tuple[str, typing.Union[str, UploadFile]]],
        ],
        **kwargs: typing.Union[str, UploadFile],
    ) -> None:
        super().__init__(*args, **kwargs)

    async def close(self) -> None:
        for key, value in self.multi_items():
            if isinstance(value, UploadFile):
                await value.close()


class Headers(typing.Mapping[str, str]):
    """
    An immutable, case-insensitive multidict.
    """

    def __init__(
        self,
        headers: typing.Mapping[str, str] = None,
        raw: typing.List[typing.Tuple[bytes, bytes]] = None,
        scope: Scope = None,
    ) -> None:
        self._list = []  # type: typing.List[typing.Tuple[bytes, bytes]]
        if headers is not None:
            assert raw is None, 'Cannot set both "headers" and "raw".'
            assert scope is None, 'Cannot set both "headers" and "scope".'
            self._list = [
                (key.lower().encode("latin-1"), value.encode("latin-1"))
                for key, value in headers.items()
            ]
        elif raw is not None:
            assert scope is None, 'Cannot set both "raw" and "scope".'
            self._list = raw
        elif scope is not None:
            self._list = scope["headers"]

    @property
    def raw(self) -> typing.List[typing.Tuple[bytes, bytes]]:
        return list(self._list)

    def keys(self) -> typing.List[str]:  # type: ignore
        return [key.decode("latin-1") for key, value in self._list]

    def values(self) -> typing.List[str]:  # type: ignore
        return [value.decode("latin-1") for key, value in self._list]

    def items(self) -> typing.List[typing.Tuple[str, str]]:  # type: ignore
        return [
            (key.decode("latin-1"), value.decode("latin-1"))
            for key, value in self._list
        ]

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        try:
            return self[key]
        except KeyError:
            return default

    def getlist(self, key: str) -> typing.List[str]:
        get_header_key = key.lower().encode("latin-1")
        return [
            item_value.decode("latin-1")
            for item_key, item_value in self._list
            if item_key == get_header_key
        ]

    def mutablecopy(self) -> "MutableHeaders":
        return MutableHeaders(raw=self._list[:])

    def __getitem__(self, key: str) -> str:
        get_header_key = key.lower().encode("latin-1")
        for header_key, header_value in self._list:
            if header_key == get_header_key:
                return header_value.decode("latin-1")
        raise KeyError(key)

    def __contains__(self, key: typing.Any) -> bool:
        get_header_key = key.lower().encode("latin-1")
        for header_key, header_value in self._list:
            if header_key == get_header_key:
                return True
        return False

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._list)

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, Headers):
            return False
        return sorted(self._list) == sorted(other._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        as_dict = dict(self.items())
        if len(as_dict) == len(self):
            return f"{class_name}({as_dict!r})"
        return f"{class_name}(raw={self.raw!r})"


class MutableHeaders(Headers):
    def __setitem__(self, key: str, value: str) -> None:
        """
        Set the header `key` to `value`, removing any duplicate entries.
        Retains insertion order.
        """
        set_key = key.lower().encode("latin-1")
        set_value = value.encode("latin-1")

        found_indexes = []
        for idx, (item_key, item_value) in enumerate(self._list):
            if item_key == set_key:
                found_indexes.append(idx)

        for idx in reversed(found_indexes[1:]):
            del self._list[idx]

        if found_indexes:
            idx = found_indexes[0]
            self._list[idx] = (set_key, set_value)
        else:
            self._list.append((set_key, set_value))

    def __delitem__(self, key: str) -> None:
        """
        Remove the header `key`.
        """
        del_key = key.lower().encode("latin-1")

        pop_indexes = []
        for idx, (item_key, item_value) in enumerate(self._list):
            if item_key == del_key:
                pop_indexes.append(idx)

        for idx in reversed(pop_indexes):
            del self._list[idx]

    @property
    def raw(self) -> typing.List[typing.Tuple[bytes, bytes]]:
        return self._list

    def setdefault(self, key: str, value: str) -> str:
        """
        If the header `key` does not exist, then set it to `value`.
        Returns the header value.
        """
        set_key = key.lower().encode("latin-1")
        set_value = value.encode("latin-1")

        for idx, (item_key, item_value) in enumerate(self._list):
            if item_key == set_key:
                return item_value.decode("latin-1")
        self._list.append((set_key, set_value))
        return value

    def update(self, other: dict) -> None:
        for key, val in other.items():
            self[key] = val

    def append(self, key: str, value: str) -> None:
        """
        Append a header, preserving any duplicate entries.
        """
        append_key = key.lower().encode("latin-1")
        append_value = value.encode("latin-1")
        self._list.append((append_key, append_value))

    def add_vary_header(self, vary: str) -> None:
        existing = self.get("vary")
        if existing is not None:
            vary = ", ".join([existing, vary])
        self["vary"] = vary
