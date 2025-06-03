import asyncio
import functools
import os
import platform
import signal
import socket
import ssl
import sys
import time
import typing
from email.utils import formatdate
from callpy.web.protocol import HttpToolsProtocol
from basepy.asynclog import logger

loop_name = 'asyncio'

if sys.platform != 'win32':
    import uvloop
    loop_name = 'uvloop'

HANDLED_SIGNALS = (
    signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
    signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
)

# Fallback to 'ssl.PROTOCOL_SSLv23' in order to support Python < 3.5.3.
SSL_PROTOCOL_VERSION = getattr(ssl, "PROTOCOL_TLS", ssl.PROTOCOL_SSLv23)


class ServerConfig:
    def __init__(
        self,
        host="127.0.0.1",
        port=5000,
        loop=loop_name,
        debug=False,
        root_path="",
        limit_concurrency=None,
        limit_max_requests=None,
        backlog=2048,
        timeout_keep_alive=5,
        timeout_notify=30,
        callback_notify=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        ssl_version=SSL_PROTOCOL_VERSION,
        ssl_cert_reqs=ssl.CERT_NONE,
        ssl_ca_certs=None,
        ssl_ciphers="TLSv1",
        headers=None,
        **kwargs
    ):
        self.host = host
        self.port = port
        self.loop = loop
        self.debug = debug
        self.root_path = root_path
        self.limit_concurrency = limit_concurrency
        self.limit_max_requests = limit_max_requests
        self.backlog = backlog
        self.timeout_keep_alive = timeout_keep_alive
        self.timeout_notify = timeout_notify
        self.callback_notify = callback_notify
        self.ssl_keyfile = ssl_keyfile
        self.ssl_certfile = ssl_certfile
        self.ssl_version = ssl_version
        self.ssl_cert_reqs = ssl_cert_reqs
        self.ssl_ca_certs = ssl_ca_certs
        self.ssl_ciphers = ssl_ciphers
        self.ssl_context = None
        self.headers = headers if headers else []  # type: List[str]
        self.encoded_headers = None  # type: List[Tuple[bytes, bytes]]

        self.loaded = False


    @property
    def is_ssl(self) -> bool:
        return bool(self.ssl_keyfile or self.ssl_certfile)

    def load(self):
        assert not self.loaded

        if self.is_ssl:
            self.ssl_context = self._create_ssl_context(
                keyfile=self.ssl_keyfile,
                certfile=self.ssl_certfile,
                ssl_version=self.ssl_version,
                cert_reqs=self.ssl_cert_reqs,
                ca_certs=self.ssl_ca_certs,
                ciphers=self.ssl_ciphers,
            )

        encoded_headers = [
            (key.lower().encode("latin1"), value.encode("latin1"))
            for key, value in self.headers
        ]
        self.encoded_headers = (
            encoded_headers
            if b"server" in dict(encoded_headers)
            else [(b"server", b"callpy")] + encoded_headers
        )  # type: List[Tuple[bytes, bytes]]

        self.loaded = True

    def _create_ssl_context(self, certfile, keyfile, ssl_version, cert_reqs, ca_certs, ciphers):
        ctx = ssl.SSLContext(ssl_version)
        ctx.load_cert_chain(certfile, keyfile)
        ctx.verify_mode = cert_reqs
        if ca_certs:
            ctx.load_verify_locations(ca_certs)
        if ciphers:
            ctx.set_ciphers(ciphers)
        return ctx


class ServerState:
    """
    Shared servers state that is available between all protocol instances.
    """

    def __init__(self):
        self.total_requests = 0
        self.connections = set()
        self.tasks = set()
        self.default_headers = []


class Server:
    def __init__(self, app, **kwargs):
        self.app = app
        self.config = ServerConfig(**kwargs)
        self.server_state = ServerState()

        self.started = False
        self.should_exit = False
        self.force_exit = False
        self.last_notified = 0

    def _setup_event_loop(self):
        loop_name = self.config.loop.lower()
        if loop_name == 'uvloop':
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        elif loop_name == 'asyncio':
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise ValueError('loop must be uvloop or asyncio.')

    def run(self, sockets=None):
        self._setup_event_loop()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.serve(sockets=sockets))

    async def serve(self, sockets=None, start_hooks=None, stop_hooks=None):
        start_hooks = start_hooks or []
        stop_hooks = stop_hooks or []
        process_id = os.getpid()

        config = self.config
        if not config.loaded:
            config.load()

        self.install_signal_handlers()

        message = "Started server process [%d]"
        await logger.info(message, process_id)

        await self.startup(sockets=sockets)
        if len(start_hooks) > 0:
            for hook in start_hooks:
                await hook()
        if self.should_exit:
            return
        await self.main_loop()
        if len(stop_hooks) > 0:
            for hook in stop_hooks:
                await hook()
        await self.shutdown(sockets=sockets)

        await logger.info(
            "Finished server process [%d]",
            process_id
        )

    async def startup(self, sockets=None):
        config = self.config

        create_protocol = functools.partial(
            HttpToolsProtocol, app=self.app, root_path=config.root_path,
            server_state=self.server_state,
            limit_concurrency=config.limit_concurrency,
            timeout_keep_alive=config.timeout_keep_alive
        )

        loop = asyncio.get_event_loop()

        reuse_port = True
        if sys.platform == 'win32':
            reuse_port = False

        if sockets is not None:
            # Explicitly passed a list of open sockets.
            self.servers = []
            for sock in sockets:
                server = await loop.create_server(
                    create_protocol, sock=sock, ssl=config.ssl_context, backlog=config.backlog,
                    reuse_port=reuse_port
                )
                self.servers.append(server)
        else:
            # Standard case. Create a socket from a host/port pair.
            try:
                server = await loop.create_server(
                    create_protocol,
                    host=config.host,
                    port=config.port,
                    ssl=config.ssl_context,
                    backlog=config.backlog,
                    reuse_port=reuse_port
                )
            except OSError as exc:
                await logger.error(exc)
                sys.exit(1)
            port = config.port
            if port == 0:
                port = server.sockets[0].getsockname()[1]
            protocol_name = "https" if config.ssl_context else "http"
            message = "CallPy running on %s://%s:%d (Press CTRL+C to quit)"
            await logger.info(
                message,
                protocol_name,
                config.host,
                port
            )
            self.servers = [server]

        self.started = True

    async def main_loop(self):
        counter = 0
        should_exit = await self.on_tick(counter)
        while not should_exit:
            counter += 1
            counter = counter % 864000
            await asyncio.sleep(0.1)
            should_exit = await self.on_tick(counter)

    async def on_tick(self, counter) -> bool:
        # Update the default headers, once per second.
        if counter % 10 == 0:
            current_time = time.time()
            current_date = formatdate(current_time, usegmt=True).encode()
            self.server_state.default_headers = [
                (b"date", current_date)
            ] + self.config.encoded_headers

            # Callback to `callback_notify` once every `timeout_notify` seconds.
            if self.config.callback_notify is not None:
                if current_time - self.last_notified > self.config.timeout_notify:
                    self.last_notified = current_time
                    await self.config.callback_notify()

        # Determine if we should exit.
        if self.should_exit:
            return True
        if self.config.limit_max_requests is not None:
            return self.server_state.total_requests >= self.config.limit_max_requests
        return False

    async def shutdown(self, sockets=None):
        await logger.info("Shutting down")

        # Stop accepting new connections.
        for server in self.servers:
            server.close()
        for socket in sockets or []:
            socket.close()
        for server in self.servers:
            await server.wait_closed()

        # Request shutdown on all existing connections.
        for connection in list(self.server_state.connections):
            connection.shutdown()
        await asyncio.sleep(0.1)

        # Wait for existing connections to finish sending responses.
        if self.server_state.connections and not self.force_exit:
            msg = "Waiting for connections to close. (CTRL+C to force quit)"
            await logger.info(msg)
            while self.server_state.connections and not self.force_exit:
                await asyncio.sleep(0.1)

        # Wait for existing tasks to complete.
        if self.server_state.tasks and not self.force_exit:
            msg = "Waiting for background tasks to complete. (CTRL+C to force quit)"
            await logger.info(msg)
            while self.server_state.tasks and not self.force_exit:
                await asyncio.sleep(0.1)

    def install_signal_handlers(self):
        loop = asyncio.get_event_loop()

        try:
            for sig in HANDLED_SIGNALS:
                loop.add_signal_handler(sig, self.handle_exit, sig, None)
        except NotImplementedError as exc:
            # Windows
            for sig in HANDLED_SIGNALS:
                signal.signal(sig, self.handle_exit)

    def handle_exit(self, sig, frame):
        if self.should_exit:
            self.force_exit = True
        else:
            self.should_exit = True
