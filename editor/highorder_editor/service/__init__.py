
from datetime import timedelta, datetime
from highorder_editor.base.helpers import ApplicationFolder, random_string, extract_name_in_email
import hashlib
import json
import os

class EditorConfig:
    filename = 'editor.json'
    _config = None

    @classmethod
    def load(cls):
        fpath = os.path.join(ApplicationFolder.root_folder, cls.filename)
        if not os.path.exists(fpath):
            cls._config = {}
            return
        with open(fpath, 'rb') as f:
            cls._config = json.loads(f.read().decode('utf-8'))

    @classmethod
    async def get_user(cls, name):
        if cls._config is None:
            cls.load()
        users = cls._config.get('users', [])
        for user in users:
            if user['name'] == name:
                return user
        return None

    @classmethod
    async def get_app(cls):
        if cls._config is None:
            cls.load()
        return cls._config['app']

    @classmethod
    async def get_server(cls):
        if cls._config is None:
            cls.load()
        server = cls._config.get('server', {})
        return server


class EditorSession:
    filename = 'editor_session.json'
    _config = None

    @classmethod
    def load(cls):
        fpath = os.path.join(ApplicationFolder.root_folder, cls.filename)
        if not os.path.exists(fpath):
            cls._config = {}
            return
        with open(fpath, 'rb') as f:
            cls._config = json.loads(f.read().decode('utf-8'))

    @classmethod
    def save_config(cls):
        fpath = os.path.join(ApplicationFolder.root_folder, cls.filename)
        with open(fpath, 'wb') as f:
            f.write(json.dumps(cls._config, ensure_ascii=False).encode('utf-8'))

    @classmethod
    async def get_session(cls, session_id):
        if cls._config is None:
            cls.load()
        sessions = cls._config.get('sessions', [])
        for session in sessions:
            if session['session_id'] == session_id:
                expired_at = datetime.fromisoformat(session['expired_at'])
                if expired_at < datetime.now():
                    return None
                return session
        return None

    @classmethod
    async def save(cls, session_id, user_name, expired_at=None):
        if cls._config is None:
            cls.load()

        session = await cls.get_session(session_id)
        if not session:
            session = dict(
                session_id = session_id,
                user_name = user_name,
                expired_at = expired_at
            )
            sessions = cls._config.setdefault('sessions', [])
            sessions.append(session)
        else:
            session['user_name'] = user_name
            session['expired_at'] = expired_at
        cls.save_config()

    @classmethod
    async def delete(cls, session_id):
        if cls._config is None:
            cls.load()
        sessions = cls._config.get('sessions', [])
        filtered = list(filter(lambda x: x['session_id'] != session_id, sessions))
        cls._config['sessions'] = filtered
        cls.save_config()


class Auth:
    @classmethod
    async def get_user(cls, name):
        return await EditorConfig.get_user(name)

    @classmethod
    async def check_pass(cls, name, password):
        user = await cls.get_user(name)
        if not user:
            return False, None
        password_safe = cls.get_password_safe(user['salt'], password)
        if password_safe == user['password']:
            return True, user
        else:
            return False, user

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
        session = await EditorSession.get_session(session_id=session_id)
        return session

    @classmethod
    async def save(self, session_id, user_name, expired_at=None):
        expired = expired_at or datetime.now() + timedelta(days=1)
        return await EditorSession.save(session_id=session_id, user_name=user_name, expired_at = expired.isoformat())

    @classmethod
    async def delete(self, session_id):
        await EditorSession.delete(session_id=session_id)
