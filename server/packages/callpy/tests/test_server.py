import threading
import time
import asyncio

import requests
from callpy.server import Server


def test_run():
    class App:
        async def __call__(self, scope, receive, send):
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b"", "more_body": False})

    class CustomServer(Server):
        def install_signal_handlers(self):
            pass

    server = CustomServer(app=App(), limit_max_requests=1)
    thread = threading.Thread(target=server.run)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    response = requests.get("http://127.0.0.1:5000")
    assert response.status_code == 204
    thread.join()

def test_run_multiprocess():
    class App:
        async def __call__(self, scope, receive, send):
            await send({"type": "http.response.start", "status": 204, "headers": []})
            await send({"type": "http.response.body", "body": b"", "more_body": False})

    class CustomServer(Server):
        def install_signal_handlers(self):
            pass

    server = CustomServer(app=App(), loop="asyncio", limit_max_requests=1)
    thread = threading.Thread(target=server.run)
    thread.start()
    while not server.started:
        time.sleep(0.01)
    response = requests.get("http://127.0.0.1:5000")
    assert response.status_code == 204
    thread.join()



def test_run_with_shutdown():
    class App:
        async def __call__(self, scope, receive, send):
            while True:
                time.sleep(1)

    class CustomServer(Server):
        def install_signal_handlers(self):
            pass

    server = CustomServer(app=App(), loop="asyncio", limit_max_requests=1)
    exc = True

    def safe_run():
        nonlocal exc, server
        try:
            exc = None
            server._setup_event_loop()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(server.serve())
        except Exception as e:
            exc = e

    thread = threading.Thread(target=safe_run)
    thread.start()

    while not server.started:
        time.sleep(0.01)

    server.should_exit = True
    thread.join()
    assert exc is None