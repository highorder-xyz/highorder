from callpy.web import Blueprint
from callpy.web.response import jsonify
from highorder.servicedef import not_login_required, login_required
from .service import QuestService
import dataclass_factory
from .data import (
    ClientRequestCommand
)

factory = dataclass_factory.Factory()

bp =  Blueprint('quest', url_prefix="/service/quest")

@bp.route('/main', methods=["POST", "GET"])
@login_required
async def quest_main(request):
    quest_svc = await QuestService.create(request.user, request.session, request.config_loader)
    data = await request.json()

    request_cmd = None
    if 'command' in data:
        request_cmd = factory.load(data, ClientRequestCommand)

    commands = await quest_svc.handle_request(request_cmd)

    return jsonify({"ok":True, "data": factory.dump({"commands": commands})})