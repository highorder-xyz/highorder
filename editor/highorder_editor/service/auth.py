from datetime import timedelta, datetime
from highorder_editor.model import SessionModel, UserModel
from peewee import IntegrityError
from highorder_editor.base.helpers import random_string, extract_name_in_email
import hashlib

class Auth:
    @classmethod
    def exists(cls, email):
        return UserModel.select().where(UserModel.email == email).exists()

    @classmethod
    def get_user(cls, email):
        try:
            return UserModel.get(UserModel.email == email)
        except UserModel.DoesNotExist:
            return None

    @classmethod
    def check_pass(cls, email, password):
        user = cls.get_user(email)
        if not user:
            return False, None
        password_safe = cls.get_password_safe(user.salt, password)
        if password_safe == user.password:
            return True, user
        else:
            return False, user

    @classmethod
    def create_user(cls, email, password, nickname=None):
        salt = random_string(6)
        password_safe = cls.get_password_safe(salt, password)
        nick = nickname if nickname else extract_name_in_email(email)
        try:
            return UserModel.create(
                email=email, 
                password=password_safe, 
                salt=salt, 
                nickname=nick, 
                sessions={}
            )
        except IntegrityError as ex:
            raise(ex)
        except Exception as ex:
            raise(ex)

    @classmethod
    def set_pass(cls, user, password):
        salt = random_string(6)
        password_safe = cls.get_password_safe(salt, password)
        user.salt = salt
        user.password = password_safe
        user.save()

    @classmethod
    def get_password_safe(cls, salt, password):
        m = hashlib.sha256(f'{salt}:{password}'.encode('utf-8'))
        password_safe = m.hexdigest()
        return password_safe


class Session:
    @classmethod
    def load(cls, session_id):
        if not session_id:
            return None
        try:
            return SessionModel.get(SessionModel.session_id == session_id)
        except SessionModel.DoesNotExist:
            return None

    @classmethod
    def create(cls, session_id, user_id, device=None, expired_at=None):
        expired = expired_at or datetime.now() + timedelta(days=14)
        return SessionModel.create(
            session_id=session_id, 
            user_id=user_id,
            device=device or {}, 
            expired_at=expired
        )

    @classmethod
    def delete(cls, session_id):
        try:
            session = SessionModel.get(SessionModel.session_id == session_id)
            session.delete_instance()
        except SessionModel.DoesNotExist:
            pass
