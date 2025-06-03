
import asyncio
import itertools
import sys
import time
from typing import Any

import hiredis
import uvloop

class RespProtocol(asyncio.Protocol):
    def __init__(self):
        self.response = list()
        self.parser = hiredis.Reader()
        self.transport = None  # type: asyncio.transports.Transport
        self.commands = {
            b"COMMAND": self.command,
            b"PING": self.ping,
        }

    def connection_made(self, transport: asyncio.transports.Transport):
        self.transport = transport

    def data_received(self, data: bytes):
        self.parser.feed(data)

        while 1:
            req = self.parser.gets()
            if req is False:
                break
            else:
                self.response.append(self.commands[req[0].upper()](*req[1:]))

        self.transport.writelines(self.response)
        self.response.clear()

    def command(self):
        # Far from being a complete implementation of the `COMMAND` command of
        # Redis, yet sufficient for us to start using redis-cli.
        return b"+OK\r\n"

    def ping(self, message=b"PONG"):
        return b"$%d\r\n%s\r\n" % (len(message), message)



class RespServer(object):
    def __init__(self, name):
        self.name = name
        self.serve_protocol = RespProtocol

    def run_forever(self, addr="0.0.0.0", port=7878):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        loop = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        coro = loop.create_server(self.serve_protocol, addr, port)
        server = loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

        return 0
