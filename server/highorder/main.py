
from basepy.config import settings
from basepy.asynclog import logger

debug = settings.server.get('debug', False)
if debug:
    from basepy.more.rich_console import install_rich_console
    install_rich_console()

from callpy import CallFlow
from callpy.web import response
from callpy.web.response import FileResponse
from .servicedef import (
    validate_client,
    validate_session_token
)
import os

from .base import error

from .boot import boot_components

app = CallFlow('highorder')

webapp_root = settings.server.get('webapp_root', None)

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
    await boot_components()

@app.before_request
async def app_before_request(request):
    if not request.path.startswith('/service/'):
        return
    sign = request.headers.get('X-HighOrder-Sign')
    app_id = request.headers.get('X-HighOrder-Application-Id')
    assert app_id != None
    session_token = request.headers.get('X-HighOrder-Session-Token')
    sign_valid  = await validate_client(app_id, sign, request)
    if not sign_valid:
        return error.client_invalid('sign not correct.')
    request.app_id = app_id

    user = None
    session = None
    if session_token:
        session, user = await validate_session_token(session_token, app_id)

    request.user = user
    request.session = session


@app.errorhandler(500)
async def app_error_handler(request, exc):
    return error.server_error(type(exc).__name__, exc.description, exc.code)

from .hola.view import bp as hola_bp
app.register_blueprint(hola_bp)


def main():
    debug = settings.server.get('debug', False)
    app.run(host='0.0.0.0', port=5000, debug=debug)