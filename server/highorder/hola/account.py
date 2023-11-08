
import hashlib
from .model import SocialAccount, User, Session, UserAuth
from highorder.base.utils import random_str, time_random_id, IDPrefix
from highorder.base.model import DB_NAME
from postmodel.transaction import in_transaction
from dataclasses import dataclass
from basepy.config import settings
import httpx
from postmodel.transaction import in_transaction
from highorder.hola.extension import (
    ReloadSessionContext,
    SetSessionCommand, SetSessionCommandArg,
    ClearSessionCommand,
    ShowModalCommand, ShowModalCommandArg,
    ShowAlertCommand, ShowAlertCommandArg,
    ExtensionCallSucceed, ExtensionCallSucceedArg,
    ExtensionCallFailed, ExtensionCallFailedArg,
    AutoList,
)

@dataclass
class UserData:
    user_id: str
    user_name: str

@dataclass
class SessionData:
    session_token: str
    user_id: str
    session_type: str


class AccountService:

    @classmethod
    async def create(cls, app_id, **kwargs):
        user_id = time_random_id(IDPrefix.USER, 10)
        name = kwargs.get("name") or user_id
        user = User(app_id=app_id, user_id=user_id, user_name=name, sessions={})
        session_type = kwargs.get('session_type', 'mobile')
        session_data = kwargs.get('session_data', {})
        device_info = kwargs.get('device_info', {})
        country_code = kwargs.get('country_code', 'cn')
        ip = kwargs.get('ip')

        session = Session(app_id=app_id, user_id=user.user_id,
            session_type=session_type,
            session_data = session_data,
            device_info = device_info,
            country_code = country_code,
            ip = ip)
        user.sessions["sessions"] = [session.session_token]

        async with in_transaction(DB_NAME):
            await user.save()
            await session.save()

        return (UserService(user), SessionService(session))


class UserService:
    @classmethod
    async def load(cls, app_id, user_id):
        model = await User.load(app_id=app_id, user_id=user_id)
        if model:
            return cls(model)
        return None

    def __init__(self, model, **kwargs):
        self.model =  model


    def get_data(self):
        return UserData(
            user_id = self.model.user_id,
            user_name = self.model.user_name)

    def get_data_dict(self):
        return dict(
            user_id = self.model.user_id,
            user_name = self.model.user_name)

    @property
    def app_id(self):
        return self.model.app_id

    @property
    def user_id(self):
        return self.model.user_id

    @property
    def user_name(self):
        return self.model.user_name

    @property
    def sessions(self):
        return self.model.sessions

    async def new_session(self, **kwargs):
        session_type = kwargs.get('session_type', 'mobile')
        session_data = kwargs.get('session_data', {})
        device_info = kwargs.get('device_info', {})
        country_code = kwargs.get('country_code', 'cn')
        ip = kwargs.get('ip')

        session = Session(app_id=self.model.app_id, user_id=self.user_id,
            session_type=session_type,
            session_data = session_data,
            device_info = device_info,
            country_code = country_code,
            ip = ip)
        self.model.sessions["sessions"].append(session.session_token)

        async with in_transaction(DB_NAME):
            await self.model.save()
            await session.save()

        return SessionService(session)

    async def save(self):
        await self.model.save()

class UserAuthService:
    @classmethod
    def get_password_hash(cls, password, salt):
        m = hashlib.sha256(f'{salt}:{password}'.encode('utf-8'))
        password_safe = m.hexdigest()
        return password_safe

    @classmethod
    async def add_user(cls, app_id, name, password):
        exist_user_auth = await UserAuth.load(app_id=app_id, email=name)
        if exist_user_auth:
            password_hash = cls.get_password_hash(password, exist_user_auth.salt)
            if password_hash != exist_user_auth.password_hash:
                exist_user_auth.password_hash = password_hash
                await exist_user_auth.save()
            return exist_user_auth.user_id
        else:
            salt = random_str(6)
            password_hash = cls.get_password_hash(password, salt)
            user_id = time_random_id(IDPrefix.USER, 10)
            user = User(app_id=app_id, user_id=user_id, user_name=name, sessions={})
            user_auth = UserAuth(app_id=app_id, user_id=user_id, email=name, salt=salt, password_hash=password_hash)

            async with in_transaction(DB_NAME):
                await user.save()
                await user_auth.save()

            return user_id

    @classmethod
    async def delete_user(cls, app_id, user_id):
        user = await User.load(app_id=app_id, user_id=user_id)
        exist_user_auth = await UserAuth.load(app_id=app_id, email=user.user_name)
        async with in_transaction(DB_NAME):
            await user.delete()
            if exist_user_auth:
                await exist_user_auth.delete()


    @classmethod
    async def check(cls, app_id, name, password):
        model = await UserAuth.load(app_id=app_id, email=name)
        if not model:
            return False, {
                "error_type": "auth_name_failed",
                "error_msg": f"Name {name} error."
            }
        salt = model.salt
        password_hash = cls.get_password_hash(password, salt)
        if password_hash == model.password_hash:
            return True, model.user_id
        else:
            return  False, {
                "error_type": "auth_password_failed",
                "error_msg": f"Name {name} password error."
            }


class SessionService:
    @classmethod
    async def load(cls, app_id, session_token):
        model = await Session.load(app_id=app_id, session_token=session_token)
        if model:
            return cls(model)
        return None

    @classmethod
    async def delete(cls, app_id, session_token):
        model = await Session.load(app_id=app_id, session_token=session_token)
        if model:
            await model.delete()
        return None

    @classmethod
    async def create(cls, app_id, **kwargs):
        session_type = kwargs.get('session_type', 'mobile')
        session_data = kwargs.get('session_data', {})
        device_info = kwargs.get('device_info', {})
        country_code = kwargs.get('country_code', 'cn')
        ip = kwargs.get('ip')

        session = Session(app_id=app_id, user_id=None,
            session_type = session_type,
            session_data = session_data,
            device_info = device_info,
            country_code = country_code,
            ip = ip)

        async with in_transaction(DB_NAME):
            await session.save()

        return SessionService(session)

    def __init__(self, model, **kwargs):
        self.model = model

    @property
    def user_id(self):
        return self.model.user_id

    @property
    def app_id(self):
        return self.model.app_id

    @property
    def session_token(self):
        return self.model.session_token

    @property
    def session_data(self):
        return self.model.session_data

    @property
    def session_type(self):
        return self.model.session_type

    @property
    def expire_time(self):
        return self.model.expire_time

    @property
    def device_info(self):
        return self.model.device_info

    @property
    def country_code(self):
        return self.model.country_code

    @property
    def ip(self):
        return self.model.ip

    @property
    def weixin_login(self):
        return self.model.session_data.get('weixin_login', False)

    def get_data(self):
        return SessionData(
            session_token=self.model.session_token,
            session_type = self.model.session_type,
            user_id = self.model.user_id)

    def get_data_dict(self):
        return dict(
            session_token=self.model.session_token,
            session_type = self.model.session_type,
            user_id = self.model.user_id)

    async def get_user_service(self):
        if self.model.user_id:
            return await UserService.load(self.model.app_id, self.model.user_id)
        else:
            return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.model, key) and not key.startswith('__'):
                setattr(self.model, key, value)

    async def save(self):
        await self.model.save()


class WeiXinService:
    url_prefix = 'https://api.weixin.qq.com/sns'

    @classmethod
    async def access_token(cls, code):
        async with httpx.AsyncClient() as client:
            url = f'{cls.url_prefix}/oauth2/access_token'
            app_id = settings.server.get('weixin_app_id')
            app_secret = settings.server.get('weixin_app_secret')
            params = {
                "appid": app_id,
                "secret": app_secret,
                "code": code,
                "grant_type": "authorization_code"
            }
            r = await client.get(url, params=params)
            ret = r.json()
            if 'errcode' in ret:
                return {
                    'ok': False,
                    'error': ret
                }
            else:
                return {
                    'ok': True,
                    'data': ret
                }

    @classmethod
    async def refresh_token(cls, refresh_token):
        async with httpx.AsyncClient() as client:
            url = f'{cls.url_prefix}/oauth2/refresh_token'
            app_id = settings.server.get('weixin_app_id')
            params = {
                "appid": app_id,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            r = await client.get(url, params=params)
            ret = r.json()
            if 'errcode' in ret:
                return {
                    'ok': False,
                    'error': ret
                }
            else:
                return {
                    'ok': True,
                    'data': ret
                }

    @classmethod
    async def auth(cls, access_token, open_id):
        async with httpx.AsyncClient() as client:
            url = f'{cls.url_prefix}/auth'
            params = {
                "access_token": access_token,
                "openid": open_id
            }
            r = await client.get(url, params=params)
            ret = r.json()
            if 'errcode' in ret:
                return {
                    'ok': False,
                    'error': ret
                }
            else:
                return {
                    'ok': True,
                    'data': ret
                }

    @classmethod
    async def userinfo(cls, access_token, open_id):
        async with httpx.AsyncClient() as client:
            url = f'{cls.url_prefix}/userinfo'
            params = {
                "access_token": access_token,
                "openid": open_id
            }
            r = await client.get(url, params=params)
            ret = r.json()
            if 'errcode' in ret:
                return {
                    'ok': False,
                    'error': ret
                }
            else:
                return {
                    'ok': True,
                    'data': ret
                }


class SocialAccountService:
    @classmethod
    async def login_weixin(cls, app_id, user_id, code):
        ret = await WeiXinService.access_token(code)
        if ret['ok'] == False:
            return ret
        refresh_ret = await WeiXinService.refresh_token(ret['data']['refresh_token'])
        if not refresh_ret['ok']:
            return refresh_ret
        open_id = ret['data']['openid']
        union_id = ret['data']['unionid']
        access_token = refresh_ret['data']['access_token']
        auth_info = refresh_ret['data']
        auth_info['access_token'] = access_token
        platform_app = settings.server.weixin_app_id
        social_id = f'wx:{platform_app}:{open_id}'
        model = await SocialAccount.load(app_id=app_id, social_id=social_id)
        if not model:
            model = await SocialAccount.create(
                app_id = app_id,
                social_id = social_id,
                user_id = user_id,
                platform = 'wx',
                platform_app = platform_app,
                open_id = open_id,
                union_id = union_id,
                auth_info = auth_info,
                link_status = True
            )
        session = None
        new_user = await UserService.load(app_id=app_id, user_id = model.user_id)
        session = await new_user.new_session(session_data = {
            'weixin_login': True
        })
        # udpate profile
        info = await WeiXinService.userinfo(access_token=access_token, open_id=open_id)
        if info['ok']:
            # TODO update profile
            pass
            # await UserProfileService.create_or_update(app_id=app_id, user_id=user_id, data={
            #     'nick_name': info['data']['nickname'],
            #     'avatar_url': info['data']['headimgurl'],
            #     'extra': info['data']
            # })
        return {'ok':True, 'data': {"session": session.get_data_dict(), "user": new_user.get_data_dict()}}

    def __init__(self, model, **kwargs):
        self.model = model

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
                async with in_transaction(DB_NAME):
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