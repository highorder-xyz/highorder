from callpy.web import Blueprint
from callpy.web.response import jsonify
from .service import HolaService
import dataclass_factory
from .data import (
    ClientReHolaCommand
)

factory = dataclass_factory.Factory()

bp =  Blueprint('hola', url_prefix="/service/hola")

@bp.route('/main', methods=["POST", "GET"])
async def hola_main(request):
    hola_svc = await HolaService.create(request.user, request.session, request.config_loader)
    data = await request.json()

    request_cmd = None
    if 'command' in data:
        request_cmd = factory.load(data, ClientReHolaCommand)

    commands = await hola_svc.handle_request(request_cmd)

    return jsonify({"ok":True, "data": factory.dump({"commands": commands})})