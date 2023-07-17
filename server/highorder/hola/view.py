from callpy.web import Blueprint
from callpy.web.response import jsonify
from .service import HolaAccountService, HolaService
import dataclass_factory
from .data import (
    ClientRequestCommand
)

factory = dataclass_factory.Factory()

bp =  Blueprint('hola', url_prefix="/service/hola")

@bp.route('/main', methods=["POST", "GET"])
async def hola_main(request):
    if request.user:
        hola_svc = await HolaService.create(request.user, request.session, request.config_loader)
    else:
        hola_svc = HolaAccountService(request.app_id, request.config_loader)
    data = await request.json()

    request_cmd = None
    if 'command' in data:
        request_cmd = factory.load(data, ClientRequestCommand)

    commands = await hola_svc.handle_request(request_cmd)

    return jsonify({"ok":True, "data": factory.dump({"commands": commands})})