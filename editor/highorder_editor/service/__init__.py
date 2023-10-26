
from datetime import timedelta, datetime
from highorder_editor.base.helpers import random_string, extract_name_in_email
import hashlib
import json


class EditorConfig:
    filename = 'editor.json'


class Auth:
    @classmethod
    async def get_user(cls, email):
        return await UserModel.get_or_none(email=email)

    @classmethod
    async def check_pass(cls, email, password):
        user = await cls.get_user(email)
        if not user:
            return False, None
        password_safe = cls.get_password_safe(user.salt, password)
        if password_safe == user.password:
            return True, user
        else:
            return False, user

    @classmethod
    async def set_pass(cls, user, password):
        salt = random_string(6)
        password_safe = cls.get_password_safe(salt, password)
        user.salt = salt
        user.password = password_safe
        await user.save()

    @classmethod
    def get_password_safe(cls, salt, password):
        m = hashlib.sha256(f'{salt}:{password}'.encode('utf-8'))
        password_safe = m.hexdigest()
        return password_safe


class Session:
    @classmethod
    async def load(self, session_id):
        if not session_id:
            return None
        session = await SessionModel.get_or_none(session_id=session_id)
        return session

    @classmethod
    async def create(self, session_id, user_id, device=None, expired_at=None):
        expired = expired_at or datetime.now() + timedelta(days=14)
        return await SessionModel.create(session_id=session_id, user_id=user_id,
                device = device or {}, expired_at = expired)

    @classmethod
    async def delete(self, session_id):
        await SessionModel.get(session_id=session_id).delete()

class User:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email