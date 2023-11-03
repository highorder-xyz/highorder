
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
import importlib
import importlib.resources

from .base import error

from .boot import boot_components

app = CallPy('highorder')

server_mode = settings.server.get('mode', 'single')
config_dir = os.path.abspath(settings.server.get('config_dir') or os.getcwd())

webapp_root = settings.server.get('webapp_root', None)
if not webapp_root:
    with importlib.resources.path('highorder', '__init__.py') as f:
        webapp_root = os.path.join(os.path.dirname(f), 'webapp')

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


content_url = settings.server.get('content_url', None)
if not content_url:
    if server_mode == 'multi':
        app.static('/static/<app_folder_name>/content', os.path.join(config_dir, '{app_folder_name}/content'))
    else:
        app.static('/static/content', os.path.join(config_dir, 'content'))


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

if settings.server.get('run_editor', False) == True:
    from highorder_editor.view import setup_editor
    editor_app = setup_editor(os.getcwd())
    app.dispatch_app(['/editor', '/wave-static', '/_f', '/_s', '/manifest.json', '/simulator'], editor_app)

from .hola.account import AccountServiceExtension
from .hola.extension import HolaServiceRegister

HolaServiceRegister.register(AccountServiceExtension)


def main():
    debug = settings.server.get('debug', False)
    port = settings.server.get('port', 5000)
    host = settings.server.get('host', '0.0.0.0')
    app.run(host=host, port=port, debug=debug)