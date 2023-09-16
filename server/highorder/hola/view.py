from callpy.web import Blueprint
from callpy.web.response import Response
from .service import HolaService
import dataclass_factory
import hmac, hashlib
from highorder.base.loader import ConfigLoader
from highorder.base import error
from highorder.account.service import SessionService
from .data import (
    ClientRequestCommand
)
import json

factory = dataclass_factory.Factory()

bp =  Blueprint('hola', url_prefix="/service/hola")

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

    def get_client_secret(self, client_key):
        for k in self.client_keys:
            if k.client_key == client_key:
                return k.client_secret
        return None


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

async def validate_client_request(request):
    sign = request.headers.get('X-HighOrder-Sign')
    app_id = request.headers.get('X-HighOrder-Application-Id')
    assert app_id != None
    session_token = request.headers.get('X-HighOrder-Session-Token')

    sign_valid  = await validate_client(app_id, sign, request)
    if not sign_valid:
        return False, error.client_invalid('sign not correct.')
    request.app_id = app_id

    user = None
    session = None
    if session_token:
        session, user = await validate_session_token(session_token, app_id)

    request.user = user
    request.session = session
    return True, None

async def validate_client_lite_request(request):
    app_id = request.headers.get('X-HighOrder-Application-Id')
    assert app_id != None
    session_token = request.headers.get('X-HighOrder-Session-Token')
    request.app_id = app_id
    app_config = await AppConfig.get(app_id)
    request.config_loader = app_config.loader

    user = None
    session = None
    if session_token:
        session, user = await validate_session_token(session_token, app_id)

    request.user = user
    request.session = session
    return True, None

@bp.route('/main', methods=["POST", "GET"])
async def hola_main(request):
    valid, err_response = await validate_client_request(request)
    if not valid:
        return err_response
    data = await request.json()
    request_cmd = None
    if 'command' in data:
        request_cmd = factory.load(data, ClientRequestCommand)

    hola_svc = await HolaService.create(request.app_id, request.session, request.config_loader, request_cmd.context)
    commands = await hola_svc.handle_request(request_cmd)

    ret_data = json.dumps({"ok":True, "data": factory.dump({"commands": commands})},
                          ensure_ascii=False, indent=None, separators=(',', ':'))

    return Response(ret_data, content_type='application/json')

@bp.route('/lite', methods=["POST", "GET"])
async def hola_lite(request):
    valid, err_response = await validate_client_lite_request(request)
    if not valid:
        return err_response
    data = await request.json()
    request_cmd = None
    if 'command' in data:
        request_cmd = factory.load(data, ClientRequestCommand)

    hola_svc = await HolaService.create(request.app_id, request.session, request.config_loader, request_cmd.context)
    commands = await hola_svc.handle_request(request_cmd)

    ret_data = json.dumps({"ok":True, "data": factory.dump({"commands": commands})},
                          ensure_ascii=False, indent=None, separators=(',', ':'))
    return Response(ret_data, content_type='application/json')