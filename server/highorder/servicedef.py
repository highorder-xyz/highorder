
from functools import wraps
import hmac, hashlib
from highorder.base.loader import ConfigLoader
from highorder.base import error
from .account.service import SessionService
from basepy.asynclog import logger

async def validate_client(app_id, sign, request):
    hex_sign, timestamp, client_key = sign.split(',', 3)
    raw_data = await request.body()

    app_config = await AppConfig.get(app_id)
    client_secret = app_config.get_client_secret(client_key)
    request.config_loader = app_config.loader
    if not client_secret:
        return False

    msg = bytes(f'{app_id}{timestamp}', encoding='utf-8') + raw_data
    hex_sign_server = hmac.new(
            bytes(client_secret, encoding='utf-8'),
            msg,
            hashlib.sha256
        ).hexdigest()

    if hex_sign_server == hex_sign:
        return True
    return False

async def validate_session_token(session_token, app_id):
    assert session_token
    session_svc = await SessionService.load(app_id, session_token)
    if session_svc:
        return (session_svc, await session_svc.get_user_service())
    return (None, None)

async def response_unauthorized(msg):
    return error.bad_request('AuthorizeRequired', msg, 401)

async def response_session_invalid():
    return error.session_invalid()

def login_required(f):
    @wraps(f)
    def wrap(request, **kwargs):
        if request.user:
            return f(request, **kwargs)
        else:
            session_token = request.headers.get('X-HighOrder-Session-Token')
            if session_token:
                return response_session_invalid()
            else:
                return response_unauthorized('login required.')

    return wrap

async def response_forbidden(msg):
    return error.bad_request('Forbidden', msg, 403)

def not_login_required(f):
    @wraps(f)
    def wrap(request, **kwargs):
        if not request.user:
            return f(request, **kwargs)
        else:
            return response_forbidden('you must logout first.')

    return wrap


class AppConfig:
    @classmethod
    async def get(cls, app_id):
        assert app_id and len(app_id) > 1
        config_loader = ConfigLoader(app_id)
        await config_loader.load()
        appconfig = cls(config_loader)
        return appconfig

    def __init__(self, config_looader):
        self.loader = config_looader
        self.client_keys = self.loader.client_keys
        self.account = self.loader.account

    def get_client_secret(self, client_key):
        for k in self.client_keys:
            if k.client_key == client_key:
                return k.client_secret
        return None

