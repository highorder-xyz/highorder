
from highorder.account.service import AccountService
from callpy.web import Blueprint
from callpy.web.response import jsonify
from highorder.servicedef import not_login_required
import dataclass_factory

factory = dataclass_factory.Factory()
bp =  Blueprint('account', url_prefix="/service/account")


@bp.route('/login/anonymous', methods=["POST", "GET"])
@not_login_required
async def anonymous_login(request):
    user, session = await AccountService.create(request.app_id)
    return jsonify(factory.dump({"ok":True, "data": {"user":user.get_data(), "session":session.get_data(),}}))