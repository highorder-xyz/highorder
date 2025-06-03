# -*- coding: utf-8 -*-

import os
import sys
import json

from urllib.parse import urljoin
from urllib.parse import urlencode, quote as urlquote, unquote as urlunquote
from mimetypes import guess_type

import socket


def get_remote_addr(transport):
    socket_info = transport.get_extra_info("socket")
    if socket_info is not None:
        try:
            info = socket_info.getpeername()
        except OSError:
            # This case appears to inconsistently occur with uvloop
            # bound to a unix domain socket.
            family = None
            info = None
        else:
            family = socket_info.family

        if family in (socket.AF_INET, socket.AF_INET6):
            return (str(info[0]), int(info[1]))
        return None
    info = transport.get_extra_info("peername")
    if info is not None and isinstance(info, (list, tuple)) and len(info) == 2:
        return (str(info[0]), int(info[1]))
    return None


def get_local_addr(transport):
    socket_info = transport.get_extra_info("socket")
    if socket_info is not None:
        info = socket_info.getsockname()
        family = socket_info.family
        if family in (socket.AF_INET, socket.AF_INET6):
            return (str(info[0]), int(info[1]))
        return None
    info = transport.get_extra_info("sockname")
    if info is not None and isinstance(info, (list, tuple)) and len(info) == 2:
        return (str(info[0]), int(info[1]))
    return None


def is_ssl(transport):
    return bool(transport.get_extra_info("sslcontext"))


def get_client_addr(scope):
    client = scope.get("client")
    if not client:
        return ""
    return "%s:%d" % client


def get_path_with_query_string(scope):
    path_with_query_string = scope.get("root_path", "") + scope["path"]
    if scope["query_string"]:
        path_with_query_string = "{}?{}".format(
            path_with_query_string, scope["query_string"].decode("ascii")
        )
    return path_with_query_string


def reraise(tp, value, tb=None):
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value


# Some helpers for string/byte handling
def to_bytes(s, enc='utf8'):
    if s is None:
        return None
    return s.encode(enc) if isinstance(s, str) else bytes(s)


def to_unicode(s, enc='utf8', err='strict'):
    if s is None:
        return None
    if isinstance(s, bytes):
        return s.decode(enc, err)
    else:
        return str(s)

def urldecode(qs):
    r = []
    for pair in qs.replace(';', '&').split('&'):
        if not pair: continue
        nv = pair.split('=', 1)
        if len(nv) != 2: nv.append('')
        key = urlunquote(nv[0].replace('+', ' '), encoding='utf-8')
        value = urlunquote(nv[1].replace('+', ' '), encoding='utf-8')
        r.append((key, value))
    return r

class ConfigDict(dict):
    def __contains__(self, k):
        try:
            return dict.__contains__(self, k) or hasattr(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property. """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls=None):
        if obj is None: return self
        if self.func.__name__ not in obj.__dict__:
            obj.__dict__[self.func.__name__] = self.func(obj)
        value = obj.__dict__[self.func.__name__]
        return value


common_mimetypes = {
	"3g2": "video/3gpp2",
	"3gp": "video/3gpp",
	"3gpp": "video/3gpp",
	"7z": "application/x-7z-compressed",
	"ai": "application/postscript",
	"aif": "audio/x-aiff",
	"aifc": "audio/x-aiff",
	"aiff": "audio/x-aiff",
	"amr": "audio/amr",
	"apk": "application/vnd.android.package-archive",
	"avi": "video/x-msvideo",
	"bmp": "image/x-ms-bmp",
	"book": "application/vnd.framemaker",
	"bz": "application/x-bzip",
	"bz2": "application/x-bzip2",
	"cjs": "application/node",
	"css": "text/css",
	"csv": "text/csv",
	"doc": "application/msword",
	"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
	"epub": "application/epub+zip",
	"geo": "application/vnd.dynageo",
	"geojson": "application/geo+json",
	"gif": "image/gif",
	"gz": "application/gzip",
	"h261": "video/h261",
	"h263": "video/h263",
	"h264": "video/h264",
	"heic": "image/heic",
	"heif": "image/heif",
	"htm": "text/html",
	"html": "text/html",
	"ico": "image/x-icon",
	"ics": "text/calendar",
	"ini": "text/plain",
	"ink": "application/inkml+xml",
	"iso": "application/x-iso9660-image",
	"jar": "application/java-archive",
	"java": "text/x-java-source",
	"jpeg": "image/jpeg",
	"jpg": "image/jpeg",
	"js": "text/javascript",
	"json": "application/json",
	"json5": "application/json5",
	"jsonld": "application/ld+json",
	"jsx": "text/jsx",
	"latex": "application/x-latex",
	"less": "text/less",
	"log": "text/plain",
	"m1v": "video/mpeg",
	"m21": "application/mp21",
	"m2a": "audio/mpeg",
	"m2v": "video/mpeg",
	"m3a": "audio/mpeg",
	"m3u": "audio/x-mpegurl",
	"m3u8": "application/vnd.apple.mpegurl",
	"m4a": "audio/x-m4a",
	"m4p": "application/mp4",
	"m4v": "video/x-m4v",
	"man": "text/troff",
	"manifest": "text/cache-manifest",
	"markdown": "text/markdown",
	"md": "text/markdown",
	"mid": "audio/midi",
	"midi": "audio/midi",
	"mime": "message/rfc822",
	"mj2": "video/mj2",
	"mjp2": "video/mj2",
	"mjs": "text/javascript",
	"mk3d": "video/x-matroska",
	"mka": "audio/x-matroska",
	"mkd": "text/x-markdown",
	"mks": "video/x-matroska",
	"mkv": "video/x-matroska",
	"mov": "video/quicktime",
	"mp2": "audio/mpeg",
	"mp21": "application/mp21",
	"mp2a": "audio/mpeg",
	"mp3": "audio/mpeg",
	"mp4": "video/mp4",
	"mp4a": "audio/mp4",
	"mp4s": "application/mp4",
	"mp4v": "video/mp4",
	"mpe": "video/mpeg",
	"mpeg": "video/mpeg",
	"mpg": "video/mpeg",
	"mpg4": "video/mp4",
	"mpga": "audio/mpeg",
	"mpkg": "application/vnd.apple.installer+xml",
	"odp": "application/vnd.oasis.opendocument.presentation",
	"ods": "application/vnd.oasis.opendocument.spreadsheet",
	"odt": "application/vnd.oasis.opendocument.text",
	"oga": "audio/ogg",
	"ogg": "audio/ogg",
	"ogv": "video/ogg",
	"ogx": "application/ogg",
	"opus": "audio/ogg",
	"otf": "font/otf",
	"pdf": "application/pdf",
	"pgp": "application/pgp-encrypted",
	"php": "application/x-httpd-php",
	"png": "image/png",
	"ppt": "application/vnd.ms-powerpoint",
	"pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
	"rar": "application/x-rar-compressed",
	"rss": "application/rss+xml",
	"rtf": "text/rtf",
	"sh": "application/x-sh",
	"svg": "image/svg+xml",
	"svgz": "image/svg+xml",
	"tar": "application/x-tar",
	"tex": "application/x-tex",
	"texi": "application/x-texinfo",
	"texinfo": "application/x-texinfo",
	"text": "text/plain",
	"tif": "image/tiff",
	"tiff": "image/tiff",
	"ts": "video/mp2t",
	"ttf": "font/ttf",
	"txt": "text/plain",
	"vbox": "application/x-virtualbox-vbox",
	"vcard": "text/vcard",
	"vsd": "application/vnd.visio",
	"wasm": "application/wasm",
	"wav": "audio/x-wav",
	"weba": "audio/webm",
	"webm": "video/webm",
	"webp": "image/webp",
	"woff": "font/woff",
	"woff2": "font/woff2",
	"xhtm": "application/vnd.pwg-xhtml-print+xml",
	"xhtml": "application/xhtml+xml",
	"xlm": "application/vnd.ms-excel",
	"xls": "application/vnd.ms-excel",
	"xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	"xltx": "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
	"xml": "text/xml",
	"xslt": "application/xslt+xml",
	"yaml": "text/yaml",
	"yml": "text/yaml",
	"zip": "application/zip",
}

def guess_file_mimetype(fpath_or_name):
    if not fpath_or_name:
        return None
    name, ext = os.path.splitext(fpath_or_name)
    _ext = ext[1:]
    if _ext in common_mimetypes:
        return common_mimetypes[_ext]
    else:
        return guess_type(fpath_or_name)[0]