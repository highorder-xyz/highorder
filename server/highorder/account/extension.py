
from highorder.hola.data import ClearSessionCommand
from postmodel.transaction import in_transaction
from .service import SessionService, UserAuthService, UserService
from highorder.hola.extension import (
    ReloadSessionContext,
    SetSessionCommand, SetSessionCommandArg,
    ShowModalCommand, ShowModalCommandArg,
    ShowAlertCommand, ShowAlertCommandArg,
    ExtensionCallSucceed, ExtensionCallSucceedArg,
    ExtensionCallFailed, ExtensionCallFailedArg,
    AutoList,
)

class AccountServiceExtension:
    ext_name = "account"

    @classmethod
    async def login_name_password(cls, args):
        commands = AutoList()
        name = args.get('name')
        password = args.get('password')
        if not name or not password:
            raise Exception(f'name and password must be provided, but go name: "{name}", password: "{password}"')
        info = args['__info__']
        app_id = info['app_id']
        session_data = info['session']

        ok, ret = await UserAuthService.check(app_id, name, password)
        if ok:
            user_id = ret
            user = await UserService.load(app_id = app_id, user_id = user_id)
            session_token = session_data['session_token']
            if session_token not in user.sessions:
                sessions = user.sessions.setdefault('sessions', [])
                sessions.append(session_token)
                session = await SessionService.load(app_id = app_id, session_token=session_token)
                session.update(user_id = user_id)
                async with in_transaction():
                    await user.save()
                    await session.save()

            commands.add(ReloadSessionContext())
            commands.add(SetSessionCommand(args=SetSessionCommandArg(
                session = session_data,
                user = user.get_data_dict()
            )))
        else:
            commands.add(ExtensionCallFailed(args=ExtensionCallFailedArg(
                error_type = ret.get('error_type', ''),
                error_msg = ret.get('error_msg', ''),
                error = ret.get('error', {})
            )))

        return commands

    @classmethod
    async def logout(cls, args):
        commands = AutoList()
        info = args['__info__']
        app_id = info['app_id']
        session_token = info['session']['session_token']
        await SessionService.delete(app_id, session_token)
        commands.add(ClearSessionCommand())
        return commands