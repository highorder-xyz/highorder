import os
import re
import sys
import base64
from io import BytesIO
from numbers import Number
import typing
from enum import Enum
from urllib.parse import unquote_plus

from .datastructures import FormData, Headers, UploadFile


# These are regexes for parsing header values.
SPECIAL_CHARS = re.escape(b'()<>@,;:\\"/[]?={} \t')
QUOTED_STR = br'"(?:\\.|[^"])*"'
VALUE_STR = br'(?:[^' + SPECIAL_CHARS + br']+|' + QUOTED_STR + br')'
OPTION_RE_STR = (
    br'(?:;|^)\s*([^' + SPECIAL_CHARS + br']+)\s*=\s*(' + VALUE_STR + br')'
)
OPTION_RE = re.compile(OPTION_RE_STR)
QUOTE = b'"'[0]


def parse_options_header(value):
    """
    Parses a Content-Type header into a value in the following format:
        (content_type, {parameters})
    """
    if not value:
        return (b'', {})

    # If we are passed a string, we assume that it conforms to WSGI and does
    # not contain any code point that's not in latin-1.
    if isinstance(value, str):            # pragma: no cover
        value = value.encode('latin-1')

    # If we have no options, return the string as-is.
    if b';' not in value:
        return (value.lower().strip(), {})

    # Split at the first semicolon, to get our value and then options.
    ctype, rest = value.split(b';', 1)
    options = {}

    # Parse the options.
    for match in OPTION_RE.finditer(rest):
        key = match.group(1).lower()
        value = match.group(2)
        if value[0] == QUOTE and value[-1] == QUOTE:
            # Unquote the value.
            value = value[1:-1]
            value = value.replace(b'\\\\', b'\\').replace(b'\\"', b'"')

        # If the value is a filename, we need to fix a bug on IE6 that sends
        # the full file path instead of the filename.
        if key == b'filename':
            if value[1:3] == b':\\' or value[:2] == b'\\\\':
                value = value.split(b'\\')[-1]

        options[key] = value

    return ctype, options


class MultiPartParseError(ValueError):
    pass


class QueryStringParseError(ValueError):
    pass


class QueryStringParser():
    def __init__(self, strict_parsing=False,
                 max_size=float('inf')):
        self.buffer = bytes()
        self.items = []

        # Max-size stuff
        if not isinstance(max_size, Number) or max_size < 1:
            raise ValueError("max_size must be a positive number, not %r" %
                             max_size)
        self.max_size = max_size
        self._current_size = 0

        # Should parsing be strict?
        self.strict_parsing = strict_parsing

    def feed(self, data):
        data_len = len(data)
        if (self._current_size + data_len) > self.max_size:
            raise QueryStringParseError('QueryString data size ({}) must be less than max_size({})'.format(
                (self._current_size + data_len), self.max_size
                ))

        try:
            self._internal_feed(data, data_len)
        finally:
            self._current_size += data_len

    def _internal_feed(self, data, length):
        strict_parsing = self.strict_parsing

        if data:
            self.buffer += data
            no_more_data = False
        else:
            no_more_data = True

        i = 0
        data_len = len(self.buffer)

        buffer = self.buffer
        while i < data_len:
            sep_pos = buffer.find(b'&', i)
            if sep_pos == -1:
                sep_pos = buffer.find(b';', i)
                if sep_pos == -1 and no_more_data:
                    sep_pos = data_len+1

            if sep_pos == -1:
                break

            equal_pos = buffer.find(b'=', i, sep_pos)
            if equal_pos == -1:
                if strict_parsing:
                    raise QueryStringParseError('not found = in pair, got {}'.format(buffer[:sep_pos]))
                pair = (unquote_plus(buffer[i:sep_pos].decode('latin-1')), None)
            else:
                pair = (unquote_plus(buffer[i:equal_pos].decode('latin-1')),
                    unquote_plus(buffer[equal_pos+1:sep_pos].decode('latin-1')))
            self.items.append(pair)
            i = (sep_pos + 1)

        if i > 0:
            self.buffer = self.buffer[i:]


    def gets(self):
        items = self.items
        self.items = []
        return items

    def __repr__(self):
        return "%s(strict_parsing=%r, max_size=%r)" % (
            self.__class__.__name__, self.strict_parsing, self.max_size
        )


class MultiPartMessage(Enum):
    PART_BEGIN = 1
    PART_DATA = 2
    PART_END = 3
    HEADER_FIELD = 4
    HEADER_VALUE = 5
    HEADER_END = 6
    HEADERS_FINISHED = 7
    END = 8


def _user_safe_decode(src: bytes, codec: str) -> str:
    try:
        return src.decode(codec)
    except (UnicodeDecodeError, LookupError):
        return src.decode("latin-1")


class FormParser:
    def __init__(
        self, headers: Headers, stream: typing.AsyncGenerator[bytes, None]
    ) -> None:
        self.headers = headers
        self.stream = stream

    async def parse(self) -> FormData:
        # Create the parser.
        parser = QueryStringParser()
        # Feed the parser with data from the request.
        async for chunk in self.stream:
            if chunk:
                parser.feed(chunk)
            else:
                parser.feed(b"")

        items = parser.gets()
        return FormData(items)

class FormDataPart:
    def __init__(self, charset="latin-1"):
        self.data = b""
        self.file = None
        self.headerlist = []
        self.disposition = None
        self.name = None
        self.filename = None
        self.content_type = None
        self.charset = charset
        self.content_length = -1
        self.transfer_encoding = b'8bit'
        self.feeding_data = False

    async def feed_line(self, line):
        if self.feeding_data:
            await self.feed_data(line)
        else:
            self.feed_header(line)

    def feed_header(self, line):
        if not line.strip():
            self.finalize_header()
        elif line[0] in b" \t" and self.headerlist:
            name, value = self.headerlist.pop()
            self.headerlist.append((name, value + line.strip()))
        else:
            if b":" not in line:
                raise MultiPartParseError("Syntax error in header: No colon.")

            name, value = line.split(b":", 1)
            self.headerlist.append((name.strip(), value.strip()))

    def finalize_header(self):
        for (key, value) in self.headerlist:
            k = key.title()
            if k == b"Content-Disposition":
                self.disposition, options = parse_options_header(value)
                self.name = _user_safe_decode(options.get(b"name", b""), self.charset)
                if b"filename" in options:
                    self.filename = _user_safe_decode(options.get(b"filename"), self.charset)
            elif k == b"Content-Type":
                self.content_type, options = parse_options_header(value)
                self.charset = options.get(b"charset").decode('latin-1') or self.charset
            elif k == b"Content-Length":
                self.content_length = int(value)
            elif k == b"Content-Transfer-Encoding":
                transfer_encoding = value.lower()
                if transfer_encoding not in [b'binary', b'8bit', b'7bit', b'base64', b'quoted-printable']:
                    raise MultiPartParseError(
                        'Unknown Content-Transfer-Encoding "{0}"'.format(
                            transfer_encoding
                        )
                    )
                else:
                    self.transfer_encoding = transfer_encoding

        if not self.disposition:
            raise MultiPartParseError("Content-Disposition header is missing.")

        if self.filename:
            self.file = UploadFile(
                            filename=self.filename,
                            content_type=self.content_type.decode("latin-1"),
                        )
        self.feeding_data = True

    async def feed_data(self, line):
        if self.file:
            await self.file.write(line)
        else:
            self.data += line

    async def finalize(self):
        if self.file:
            await self.file.seek(0)
        else:
            if self.transfer_encoding == b'base64':
                self.data = base64.b64decode(self.data)
            elif self.transfer_encoding == b'quoted-printable':
                p = QueryStringParser()
                p.feed(self.data)
                p.feed('')
                items = p.gets()
                self.data = FormData(items)
            else:
                self.data = _user_safe_decode(self.data, self.charset)

    def get(self):
        if self.data:
            return (self.name, self.data)
        elif self.file:
            return (self.name, self.file)
        else:
            raise ValueError('FormDataPart error, not contain valid data or file.')

class MultiPartParser:
    def __init__(
        self, headers: Headers, stream: typing.AsyncGenerator[bytes, None],
        buffer_size=2 ** 16
    ) -> None:
        self.headers = headers
        self.stream = stream
        self.parts = []
        self._boundary = ''
        self.separator = ''
        self.terminator = ''
        self.buffer = bytes()
        self.current_part = None
        self.buffer_size = buffer_size
        self.charset = 'utf-8'

    @property
    def boundary(self):
        return self._boundary

    @boundary.setter
    def boundary(self, boundary):
        self._boundary = boundary
        self.separator = b"--" + self.boundary
        self.terminator = b"--" + self.boundary + b"--"

    async def feed(self, data=b""):
        data = data or b""
        last_data = (len(data) == 0)
        buffer = self.buffer + data
        lines = buffer.splitlines(keepends=True)
        for line in lines:
            if line.endswith(b"\r\n"):
                line, linebreak = line[:-2], b"\r\n"
            elif line.endswith(b"\n"):
                line, linebreak = line[:-1], b"\n"
                if not line:
                    continue
            elif line.endswith(b"\r"):
                line, linebreak = line[:-1], b"\r"
            else:
                line, linebreak = line, b""

            if not linebreak and not last_data:
                self.buffer = line
                if len(self.buffer) >= self.buffer_size:
                    raise MultiPartParseError('MultiPart data too long, must be less than 64KB.')
                break

            if line == self.separator:
                if self.current_part:
                    await self.current_part.finalize()
                    self.parts.append(self.current_part)
                self.current_part = FormDataPart(self.charset)
            elif line == self.terminator:
                await self.current_part.finalize()
                self.parts.append(self.current_part)
                self.current_part = None
            else:
                await self.current_part.feed_line(line)

    async def parse(self) -> FormData:
        # Parse the Content-Type header to get the multipart boundary.
        content_type, params = parse_options_header(self.headers["Content-Type"])
        charset = params.get(b"charset", "utf-8")
        if type(charset) == bytes:
            charset = charset.decode("latin-1")
        self.charset = charset
        self.boundary = params.get(b"boundary")

        # Feed the parser with data from the request.
        async for chunk in self.stream:
            await self.feed(chunk)

        return FormData(list(map(lambda x: x.get(), self.parts)))