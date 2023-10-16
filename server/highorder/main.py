
from basepy.config import settings
from basepy.asynclog import logger

debug = settings.server.get('debug', False)
if debug:
    from basepy.more.rich_console import install_rich_console
    install_rich_console()

from callpy import CallPy
from callpy.web import response
from callpy.web.response import FileResponse
import os

from .base import error

from .boot import boot_components

app = CallPy('highorder')

webapp_root = settings.server.get('webapp_root', None)
simulator_root = settings.server.get('simulator_root', None)

@app.route('/')
async def index(request):
    args = request.args
    if 'app_id' in args and 'client_key' in args:
        return FileResponse(os.path.join(settings.server.webapp_root, 'index.html'))
    return 'highorder server ok'

@app.route('/favicon.ico')
async def favicon(request):
    favicon_path = os.path.join(webapp_root, 'favicon.ico')
    if webapp_root and os.path.exists(favicon_path):
        return FileResponse(os.path.join(settings.server.webapp_root, 'favicon.ico'))
    return response.abort(404)

if webapp_root:
    app.static('/assets', os.path.abspath(os.path.join(webapp_root, 'assets')))

if simulator_root:
    @app.route('/simulator/')
    async def simulator(request):
        args = request.args
        if 'app_id' in args and 'client_key' in args and simulator_root:
            return FileResponse(os.path.join(simulator_root, 'index.html'))
        return 'highorder server ok'

    @app.route('/simulator/favicon.ico')
    async def simulator_favicon(request):
        favicon_path = os.path.join(simulator_root, 'favicon.ico')
        if simulator_root and os.path.exists(favicon_path):
            return FileResponse(os.path.join(simulator_root, 'favicon.ico'))
        return response.abort(404)


    app.static('/simulator/assets', os.path.abspath(os.path.join(simulator_root, 'assets')))

content_location = settings.server.get('content_location', None)
if content_location:
    if not os.path.exists(content_location):
        os.makedirs(content_location, exist_ok=True)
    app.static('/static', os.path.abspath(content_location))


@app.before_start
async def app_before_start():
    if not debug:
        await logger.init(settings.log)
    else:
        await logger.init()
    try:
        await boot_components()
    except Exception as ex:
        await logger.error(str(ex))

@app.before_request
async def app_before_request(request):
    if not request.path.startswith('/service/'):
        return

@app.errorhandler(500)
async def app_error_handler(request, exc):
    return error.server_error(type(exc).__name__, exc.description, exc.code)

from .hola.view import bp as hola_bp
app.register_blueprint(hola_bp)

from .account.extension import AccountServiceExtension
from .hola.extension import HolaServiceRegister

HolaServiceRegister.register(AccountServiceExtension)


def main():
    debug = settings.server.get('debug', False)
    port = settings.server.get('port', 5000)
    host = settings.server.get('host', '0.0.0.0')
    app.run(host=host, port=port, debug=debug)