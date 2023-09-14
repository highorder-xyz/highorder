
from .model import SocialAccount, User, Session, UserProfile
from highorder.base.utils import time_random_id
from postmodel.transaction import in_transaction
from dataclasses import dataclass
from basepy.config import settings
import httpx

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
        user_id = time_random_id('UU', 10)
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

        async with in_transaction():
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

    async def get_profile(self):
        user_id = self.user_id
        app_id = self.app_id
        return await UserProfileService.load_or_create(app_id, user_id)

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

        async with in_transaction():
            await self.model.save()
            await session.save()

        return SessionService(session)

class SessionService:
    @classmethod
    async def load(cls, app_id, session_token):
        model = await Session.load(app_id=app_id, session_token=session_token)
        if model:
            return cls(model)
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

        async with in_transaction():
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
        return await UserService.load(self.model.app_id, self.model.user_id)


class UserProfileService:
    @classmethod
    async def load(cls, app_id, user_id):
        model = await UserProfile.load(app_id=app_id, user_id=user_id)
        if model:
            return cls(model)
        return None

    @classmethod
    async def create_or_update(cls, app_id, user_id, data):
        model = await UserProfile.load(app_id=app_id, user_id=user_id)
        if not model:
            model = await UserProfile.create(
                app_id = app_id,
                user_id = user_id,
                nick_name = data['nick_name'],
                avatar_url = data['avatar_url'],
                extra = data.get('extra', {})
            )
            inst = cls(model)
        else:
            inst = cls(model)
            await inst.update(data)
        return inst

    @classmethod
    async def load_or_create(cls, app_id, user_id):
        profile = await cls.load(app_id, user_id)
        if not profile:
            data = {
                'nick_name': f'无名-{user_id[-8:]}',
                'avatar_url': ''
            }
            await cls.create_or_update(app_id, user_id, data)
            return data
        else:
            return {
                'nick_name': profile.nick_name,
                'avatar_url': profile.avatar_url
            }


    def __init__(self, model, **kwargs):
        self.model =  model

    @property
    def nick_name(self):
        return self.model.nick_name

    @property
    def avatar_url(self):
        return self.model.avatar_url

    async def update(self, data):
        if 'nick_name' in data:
            self.model.nick_name = data['nick_name']
        if 'avatar_url' in data:
            self.model.avatar_url = data['avatar_url']
        if 'extra' in data:
            self.model.extra = data['extra']
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
            await UserProfileService.create_or_update(app_id=app_id, user_id=user_id, data={
                'nick_name': info['data']['nickname'],
                'avatar_url': info['data']['headimgurl'],
                'extra': info['data']
            })
        return {'ok':True, 'data': {"session": session.get_data_dict(), "user": new_user.get_data_dict()}}

    def __init__(self, model, **kwargs):
        self.model = model