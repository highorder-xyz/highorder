
import os
import stat
import typing
from email.utils import parsedate

from aiofiles.os import stat as aio_stat

from .datastructures import URL, Headers
from .request import Request
from .response import (
    Response,
    FileResponse,
    text,
    redirect
)
from .types import Receive, Scope, Send
from string import Formatter


class NotModifiedResponse(Response):
    NOT_MODIFIED_HEADERS = (
        "cache-control",
        "content-location",
        "date",
        "etag",
        "expires",
        "vary",
    )

    def __init__(self, headers: Headers):
        super().__init__(
            status_code=304,
            headers={
                name: value
                for name, value in headers.items()
                if name in self.NOT_MODIFIED_HEADERS
            },
        )

def is_formattable(format_string):
    keys = [tup[1] for tup in Formatter().parse(format_string) if tup[1] is not None]
    if len(keys) > 0:
        return True
    return False

class StaticHandler:
    def __init__(
        self,
        directory: str = None,
        html: bool = False,
        check_dir: bool = True,
    ) -> None:
        if is_formattable(directory):
            self.directory_format = directory
            self.directory = None
        else:
            self.directory_format = None
            self.directory = os.path.abspath(directory)
            if check_dir and directory is not None and not os.path.isdir(directory):
                raise RuntimeError(f"Directory '{directory}' does not exist")
        self.html = html
        self.config_checked = False

    async def __call__(self, request, target='', **kwargs):
        print('_call__', target)

        if not self.config_checked:
            await self.check_config()
            self.config_checked = True

        response = await self.get_response(request, target)
        return response


    async def get_response(self, request, path: str) -> Response:
        """
        Returns an HTTP response, given the incoming path, method and request headers.
        """
        if request.method not in ("GET", "HEAD"):
            return text("Method Not Allowed", status=405)

        if path.startswith("..") or path.startswith("."):
            # Most clients will normalize the path, so we shouldn't normally
            # get this, but don't allow misbehaving clients to break out of
            # the static files directory.
            return text("Not Found", status=404)

        if self.directory:
            full_path = os.path.join(self.directory, path)
        elif self.directory_format:
            directory = self.directory_format.format(**request.view_args)
            full_path = os.path.join(os.path.abspath(directory), path)
        else:
            full_path = path

        stat_result = await self.lookup_path(full_path)

        if stat_result and stat.S_ISREG(stat_result.st_mode):
            # We have a static file to serve.
            return self.file_response(full_path, stat_result, request)

        elif stat_result and stat.S_ISDIR(stat_result.st_mode) and self.html:
            # We're in HTML mode, and have got a directory URL.
            # Check if we have 'index.html' file to serve.
            index_path = os.path.join(full_path, "index.html")
            stat_result = await self.lookup_path(index_path)
            if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
                if not request.full_path.endswith("/"):
                    # Directory URLs should redirect to always end in "/".
                    new_url = '{}/'.format(request.base_url)
                    return redirect(new_url)
                return self.file_response(index_path, stat_result, request)

        if self.html:
            # Check for '404.html' if we're in HTML mode.
            file_path = os.path.join(full_path, "404.html")
            stat_result = await self.lookup_path(file_path)
            if stat_result is not None and stat.S_ISREG(stat_result.st_mode):
                return self.file_response(
                    file_path, stat_result, request, status_code=404
                )

        return text("Not Found", status=404)

    async def lookup_path(
        self, path: str
    ) -> typing.Tuple[str, typing.Optional[os.stat_result]]:
        try:
            stat_result = await aio_stat(path)
            return stat_result
        except FileNotFoundError:
            pass
        return None

    def file_response(
        self,
        full_path: str,
        stat_result: os.stat_result,
        request: Request,
        status_code: int = 200,
    ) -> Response:
        method = request.method
        request_headers = request.headers

        response = FileResponse(
            full_path, status_code=status_code, stat_result=stat_result, method=method
        )
        if self.is_not_modified(response.headers, request_headers):
            return NotModifiedResponse(response.headers)
        return response

    async def check_config(self) -> None:
        """
        Perform a one-off configuration check that StaticHandler is actually
        pointed at a directory, so that we can raise loud errors rather than
        just returning 404 responses.
        """
        if self.directory is None:
            return

        try:
            stat_result = await aio_stat(self.directory)
        except FileNotFoundError:
            raise RuntimeError(
                f"StaticHandler directory '{self.directory}' does not exist."
            )
        if not (stat.S_ISDIR(stat_result.st_mode) or stat.S_ISLNK(stat_result.st_mode)):
            raise RuntimeError(
                f"StaticHandler path '{self.directory}' is not a directory."
            )

    def is_not_modified(
        self, response_headers: Headers, request_headers: Headers
    ) -> bool:
        """
        Given the request and response headers, return `True` if an HTTP
        "Not Modified" response could be returned instead.
        """
        try:
            if_none_match = request_headers["if-none-match"]
            etag = response_headers["etag"]
            if if_none_match == etag:
                return True
        except KeyError:
            pass

        try:
            if_modified_since = parsedate(request_headers["if-modified-since"])
            last_modified = parsedate(response_headers["last-modified"])
            if (
                if_modified_since is not None
                and last_modified is not None
                and if_modified_since >= last_modified
            ):
                return True
        except KeyError:
            pass

        return False
