
import tempfile
from typing import List
from highorder_editor.service import EditorConfig

from highorder_editor.base.helpers import (
    ApplicationFolder, random_string, get_media_type
)
from datetime import datetime
import os
from basepy.asynclib.threaded import threaded
from highorder_editor.base.fs import FileSystem
import json
import hmac
import hashlib
import httpx


class ApplicationStorage:
    @classmethod
    @threaded
    def load_app_configs(cls, name):
        app_config_root = ApplicationFolder.get_app_root()
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        fpath = os.path.join(app_config_root, f'{name}.json')
        if not os.path.exists(fpath):
            return {}
        with open(fpath, 'r') as f:
            return json.loads(f.read())

    @classmethod
    @threaded
    def write_app_configs(cls, name, value):
        app_config_root = ApplicationFolder.get_app_root()
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        with open(os.path.join(app_config_root, f'{name}.json'), 'w') as f:
            f.write(json.dumps(value, ensure_ascii=False))



    @classmethod
    @threaded
    def write_app_hola(cls, name, code):
        app_config_root = ApplicationFolder.get_app_root()
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        with open(os.path.join(app_config_root, name), 'w') as f:
            f.write(code)


    @classmethod
    @threaded
    def load_app_hola(cls, name):
        app_config_root = ApplicationFolder.get_app_root()
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        fpath = os.path.join(app_config_root, f'{name}')
        if not os.path.exists(fpath):
            return ''
        with open(fpath, 'r') as f:
            return f.read()

    @classmethod
    def translate_upload_path(cls, up_path):
        if up_path.startswith('/_f/'):
            return os.path.join(ApplicationFolder.get_upload_dir(), up_path[4:])
        return up_path

class UploadedFileRecord:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.size=kwargs['size']
        self.media_type = kwargs['media_type']
        self.uploaded=datetime.fromisoformat(kwargs['uploaded'])


class ApplicationContentService:
    def __init__(self, content, **kwargs):
        self._content = content

    @classmethod
    async def load(cls):
        content = await ApplicationStorage.load_app_configs("content")
        assert content != None
        if not content:
            content['main'] = {'files': []}
        inst = cls(content)
        await inst.save()
        return inst

    @property
    def config(self):
        return self._content

    def get_collections(self):
        return self._content.keys()

    async def add_collection(self, name):
        if name not in self._content:
            self._content[name] = {'files': []}
            await self.save()

    def get_collection_root(self, collection):
        collection_root = os.path.join(ApplicationFolder.get_content_root(), collection)
        if not os.path.exists(collection_root):
            os.makedirs(collection_root, exist_ok=True)
        return collection_root

    async def save_files(self, collection, data_files):
        collection_data = self._content.setdefault(collection, {})
        files_meta = collection_data.setdefault('files', [])
        collection_root = self.get_collection_root(collection)
        uploaded = []
        for file in data_files:
            src_path = ApplicationStorage.translate_upload_path(file)
            filename = os.path.basename(file)
            uploaded.append(src_path)
            dest_path = os.path.join(collection_root, filename)
            statinfo = os.stat(src_path)
            await FileSystem.copy_file(src_path, dest_path)

            others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
            others_meta.append(dict(
                name=filename,
                size=statinfo.st_size,
                media_type = get_media_type(src_path),
                uploaded=datetime.now().isoformat()
            ))
            files_meta = others_meta

        self._content[collection]['files'] = files_meta
        await self.save()
        await self.remove_uploaded_files(uploaded)

    async def remove_uploaded_files(self, uploaded):
        for file in uploaded:
            await FileSystem.remove(file)

    async def get_files(self, collection, page=1):
        files_meta = self._content.get(collection, {}).get('files', [])
        files = [UploadedFileRecord(**file_meta) for file_meta in files_meta]
        return files

    async def delete_file(self, collection, filename):
        files_meta = self._content.get(collection, {}).get('files', [])
        others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
        self._content[collection]['files'] = others_meta
        await self.save()
        collection_root = self.get_collection_root(collection)
        dest = os.path.join(collection_root, filename)
        await FileSystem.remove(dest)


    async def save(self):
        await ApplicationStorage.write_app_configs('content', self._content)


class ApplicationDataFileService:
    def __init__(self, datafile, **kwargs):
        self._datafile = datafile

    @classmethod
    async def load(cls):
        datafile = await ApplicationStorage.load_app_configs("datafile")
        return cls(datafile)

    @property
    def config(self):
        return self._datafile

    async def save_files(self, data_files):
        files_meta = self._datafile.setdefault('files', [])
        uploaded = []
        for file in data_files:
            src_path = ApplicationStorage.translate_upload_path(file)
            filename = os.path.basename(file)
            uploaded.append(src_path)
            dest_path = os.path.join(ApplicationFolder.get_datafile_root(), filename)
            statinfo = os.stat(src_path)
            await FileSystem.copy_file(src_path, dest_path)

            others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
            others_meta.append(dict(
                name=filename,
                size=statinfo.st_size,
                media_type = 'json',
                uploaded=datetime.now().isoformat()
            ))
            files_meta = others_meta

        self._datafile['files'] = files_meta
        await self.save()
        await self.remove_uploaded_files(uploaded)

    async def remove_uploaded_files(self, uploaded):
        for file in uploaded:
            await FileSystem.remove(file)

    async def get_files(self, page=1):
        files_meta = self._datafile.get('files', [])
        files = [UploadedFileRecord(**file_meta) for file_meta in files_meta]
        return files

    async def delete_file(self, filename):
        files_meta = self._datafile.get('files', [])
        others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
        self._datafile['files'] = others_meta
        await self.save()
        dest = os.path.join(ApplicationFolder.get_datafile_root(), filename)
        await FileSystem.remove(dest)

    async def save(self):
        await ApplicationStorage.write_app_configs('datafile', self._datafile)


class ApplicationDB():
    """Database-backed Application class for console mode"""
    def __init__(self, model, **kwargs):
        assert model != None
        self.model = model
        self.members = []
        self.workspace_name = None

    @property
    def app_id(self):
        return self.model.app_id

    @property
    def workspace_id(self):
        return self.model.workspace_id

    @property
    def name(self):
        return self.model.name

    @property
    def description(self):
        return self.model.description

    @classmethod
    async def load(cls, app_id):
        from highorder_editor.model import ApplicationModel
        m = await ApplicationModel.get_or_none(app_id=app_id)
        if not m:
            return None
        inst = cls(m)
        return inst

    async def save_profile(self, name, description):
        if name:
            self.model.name = name
        if description:
            self.model.description = description
        await self.model.save()

    async def create_client_key(self):
        from highorder_editor.model import ApplicationClientKeyModel
        key_id = random_string(8)
        key_secret = random_string(32)
        clientkey = await ApplicationClientKeyModel.create(app_id = self.app_id,
                clientkey_id = key_id, clientkey_secret = key_secret, valid=True
            )
        return clientkey

# Alias for backward compatibility
Application = ApplicationDB


class ApplicationFile():
    """File-based Application class for single app mode"""
    def __init__(self, app_id, **kwargs):
        self.app_id = app_id
        self.name = kwargs.get('name', '')
        self.description = kwargs.get('description', '')
        self._app = None

    @classmethod
    async def load(cls, app_id = None):
        app = await EditorConfig.get_app()
        if app_id and app_id != app['app_id']:
            return None
        else:
            inst = cls(**app)
            _app_config = await ApplicationStorage.load_app_configs('app')

            if not _app_config:
                _app_config = dict(
                    app_id = app_id,
                    app_name = app['name'],
                    client_keys = [cls.gen_client_key(app_id)]
                )
                inst._app = _app_config
                await inst.write_app_info()
            else:
                inst._app = _app_config
            return inst

    async def get_hola_json(self, name="main.hola"):
        return await ApplicationStorage.load_app_configs(name)

    async def save_hola_json(self, json_obj, name="main.hola"):
        await ApplicationStorage.write_app_configs(name, json_obj)

    async def get_hola_code(self, name="main.hola"):
        return await ApplicationStorage.load_app_hola(name)

    async def save_hola_code(self, code, name="main.hola"):
        await ApplicationStorage.write_app_hola(name, code)

    async def write_app_info(self):
        await ApplicationStorage.write_app_configs('app', self._app)

    async def get_valid_clientkeys(self):
        return self._app.get('client_keys', [])

    async def get_client_secret(self, client_key):
        client_keys = self._app.get('client_keys', [])
        filtered = list(filter(lambda x: x['client_key'] == client_key, client_keys))
        if not filtered:
            return None
        return filtered[0]['client_secret']

    @classmethod
    def gen_client_key(cls, app_id):
        key_id = random_string(8)
        key_secret = random_string(32)
        clientkey = dict(app_id = app_id,
                client_key = key_id,
                client_secret = key_secret,
                valid=True
            )
        return clientkey

    async def create_client_key(self):
        clientkey = self.gen_client_key(self.app_id)
        client_keys = self._app.setdefault('client_keys', [])
        client_keys.append(clientkey)
        await self.write_app_info()
        return clientkey


class ApplicationSetupService:
    @classmethod
    async def load(cls, app_id, server_url):
        setup_hola = await ApplicationStorage.load_app_hola('setup.hola')
        inst = cls(app_id, setup_hola, server_url)
        return inst

    def __init__(self, app_id, hola, server_url):
        self.app_id = app_id
        self.hola = hola
        self.server_url = server_url

    async def save_setup_hola(self, code=""):
        self.hola = code
        await ApplicationStorage.write_app_hola('setup.hola', code)

    def get_sign(self, client_key, client_secret, body):
        assert isinstance(body, (bytes))
        timestamp = str(int(datetime.now().timestamp())).encode('utf-8')
        message = bytes(self.app_id, 'latin-1') + timestamp + body
        signature = hmac.new(
            bytes(client_secret, 'latin-1'),
            msg=message,
            digestmod=hashlib.sha256
        ).hexdigest().lower().encode('utf-8')
        return b','.join([signature, timestamp, client_key.encode('utf-8')])

    async def call_setup_service(self, hola_code):
        server = await EditorConfig.get_server()
        client_key = server['client_key']
        client_secret = server['client_secret']
        server_url = self.server_url
        data = {
            "command":"app_setup",
            "args": {
                "hola": hola_code
            }
        }
        body = bytes(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf-8')
        sign = self.get_sign(client_key, client_secret, body)
        headers = {
            'X-HighOrder-Sign': sign,
            'X-HighOrder-Application-Id': self.app_id
        }

        async with httpx.AsyncClient() as client:
            url = f'{server_url}/service/hola/setup'
            r = await client.post(url, headers=headers, content=body)
            ret = r.json()
            return ret


    async def run_setup(self):
        hola_code = self.hola
        response = await self.call_setup_service(hola_code)
        if response['ok']:
            return
        else:
            error_type = response['error_type']
            error_msg = response['error_msg']
            raise Exception(f'Setup Failed: {error_type} \nmsg="{error_msg}"')

