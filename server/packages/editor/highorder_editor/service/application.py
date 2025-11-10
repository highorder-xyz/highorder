
from highorder_editor.base.helpers import (
    ApplicationFolder, random_string, get_media_type,
    get_publish_package_root, get_publish_content_root, get_publish_release_root
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
    def load_app_configs(cls, app_id, name):
        app_config_root = ApplicationFolder.get_app_root(app_id)
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        fpath = os.path.join(app_config_root, f'{name}.json')
        if not os.path.exists(fpath):
            return {}
        with open(fpath, 'r') as f:
            return json.loads(f.read())

    @classmethod
    @threaded
    def write_app_configs(cls, app_id, name, value):
        app_config_root = ApplicationFolder.get_app_root(app_id)
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        with open(os.path.join(app_config_root, f'{name}.json'), 'w') as f:
            f.write(json.dumps(value, ensure_ascii=False))



    @classmethod
    @threaded
    def write_app_hola(cls, app_id, name, code):
        app_config_root = ApplicationFolder.get_app_root(app_id)
        if not os.path.exists(app_config_root):
            os.makedirs(app_config_root, exist_ok=True)
        with open(os.path.join(app_config_root, name), 'w') as f:
            f.write(code)


    @classmethod
    @threaded
    def load_app_hola(cls, app_id, name):
        app_config_root = ApplicationFolder.get_app_root(app_id)
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
        self.app_id = kwargs.get('app_id')

    @classmethod
    async def load(cls, app_id):
        content = await ApplicationStorage.load_app_configs(app_id, "content")
        assert content != None
        if not content:
            content['main'] = {'files': []}
        inst = cls(content, app_id=app_id)
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
        collection_root = os.path.join(ApplicationFolder.get_content_root(self.app_id), collection)
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
        await ApplicationStorage.write_app_configs(self.app_id, 'content', self._content)


class ApplicationDataFileService:
    def __init__(self, datafile, **kwargs):
        self._datafile = datafile
        self.app_id = kwargs.get('app_id')

    @classmethod
    async def load(cls, app_id):
        datafile = await ApplicationStorage.load_app_configs(app_id, "datafile")
        return cls(datafile, app_id=app_id)

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
            dest_path = os.path.join(ApplicationFolder.get_datafile_root(self.app_id), filename)
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
        dest = os.path.join(ApplicationFolder.get_datafile_root(self.app_id), filename)
        await FileSystem.remove(dest)

    async def save(self):
        await ApplicationStorage.write_app_configs(self.app_id, 'datafile', self._datafile)


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
        m = ApplicationModel.get_or_none(ApplicationModel.app_id == app_id)
        if not m:
            return None
        inst = cls(m)
        await inst.ensure_app_config()
        return inst

    @classmethod
    async def create(cls, name, description, creator_id, detail=None):
        from highorder_editor.model import ApplicationModel
        app = ApplicationModel.create(name=name, description=description, detail=detail or {}, creator=creator_id)
        inst = cls(app)
        await inst.create_client_key()
        await inst.ensure_app_config()
        return inst

    async def save_profile(self, name, description):
        if name:
            self.model.name = name
        if description:
            self.model.description = description
        self.model.save()

    async def create_client_key(self):
        from highorder_editor.model import ApplicationClientKeyModel
        key_id = random_string(8)
        key_secret = random_string(32)
        clientkey = ApplicationClientKeyModel.create(app_id = self.app_id,
                clientkey_id = key_id, clientkey_secret = key_secret, valid=True
            )
        return clientkey

    async def ensure_app_config(self):
        app_root = ApplicationFolder.get_app_root(self.app_id)
        fpath = os.path.join(app_root, 'app.json')
        if os.path.exists(fpath):
            return
        client_keys = await self.get_valid_clientkeys()
        data = {
            'app_id': self.app_id,
            'app_name': self.name,
            'client_keys': client_keys or []
        }
        await ApplicationStorage.write_app_configs(self.app_id, 'app', data)

    async def get_valid_clientkeys(self):
        from highorder_editor.model import ApplicationClientKeyModel
        rows = (ApplicationClientKeyModel
                .select()
                .where((ApplicationClientKeyModel.app_id == self.app_id) & (ApplicationClientKeyModel.valid == True)))
        return [dict(app_id=row.app_id, client_key=row.clientkey_id, client_secret=row.clientkey_secret, valid=row.valid) for row in rows]

    async def get_client_secret(self, client_key):
        from highorder_editor.model import ApplicationClientKeyModel
        row = (ApplicationClientKeyModel
               .get_or_none((ApplicationClientKeyModel.app_id == self.app_id) & (ApplicationClientKeyModel.clientkey_id == client_key) & (ApplicationClientKeyModel.valid == True)))
        return row.clientkey_secret if row else None

    async def get_hola_json(self, name="main.hola"):
        return await ApplicationStorage.load_app_configs(self.app_id, name)

    async def save_hola_json(self, json_obj, name="main.hola"):
        await ApplicationStorage.write_app_configs(self.app_id, name, json_obj)

    async def get_hola_code(self, name="main.hola"):
        return await ApplicationStorage.load_app_hola(self.app_id, name)

    async def save_hola_code(self, code, name="main.hola"):
        await ApplicationStorage.write_app_hola(self.app_id, name, code)

    # --- Publish helpers and operations ---
    def next_major_version(self, version):
        major, minor = version.split('.') if version else ('0', '0')
        major = int(major)
        minor = 0
        major = major + 1
        return f"{major}.0", major * 10000

    def next_minor_version(self, version):
        major, minor = version.split('.') if version else ('0', '0')
        major = int(major)
        minor = int(minor) + 1
        if minor > 9999:
            raise Exception('minor version not allowed to be greater than 9999.')
        return f"{major}.{minor}", major * 10000 + minor

    async def get_state(self):
        # In editor, ApplicationModel embeds state fields
        return self.model

    async def get_package_data(self):
        publish_date = datetime.now().isoformat()
        package_data = {}
        manifest = {
            'app_id': self.app_id,
            'app_version': '',
            'description': '',
            'publish_type': '',
            'publish_date': publish_date,
        }
        package_data['manifest'] = manifest

        client_keys = await self.get_valid_clientkeys()
        app = {
            'app_id': self.app_id,
            'app_name': self.name,
            'client_keys': client_keys,
        }
        package_data['app'] = app

        for key in ['content', 'datafile']:
            cfg = await ApplicationStorage.load_app_configs(self.app_id, key)
            package_data[key] = cfg or {}

        hola_json = await self.get_hola_json()
        package_data['hola'] = hola_json or {}
        return package_data

    async def _write_all_app_configs(self, package_data):
        # Write app/*.json for keys used by server loader
        for key in ['app', 'content', 'datafile', 'hola']:
            if key in package_data:
                await ApplicationStorage.write_app_configs(self.app_id, key if key != 'hola' else 'main.hola', package_data[key])

    async def do_create_package(self, latest_package, description):
        from highorder_editor.model import ApplicationPublishModel
        package_data = await self.get_package_data()
        publish_date = package_data['manifest']['publish_date']

        # decide version & publish_type using simple diffs
        if latest_package:
            import json as _json
            latest_data = _json.loads(bytes(latest_package.package_data).decode('utf-8')) if latest_package.package_data else {}
            latest_version = latest_package.app_version

            hola_changed = (latest_data.get('hola') != package_data.get('hola'))
            if hola_changed:
                publish_type = 'major'
                app_version, version_number = self.next_major_version(latest_version)
            else:
                data_changed = (
                    latest_data.get('content') != package_data.get('content') or
                    latest_data.get('datafile') != package_data.get('datafile')
                )
                if data_changed:
                    publish_type = 'minor'
                    app_version, version_number = self.next_minor_version(latest_version)
                else:
                    raise Exception('No changes found to latest release, No package need to be created.')
        else:
            app_version = '1.0'
            version_number = 10000
            publish_type = 'major'

        manifest = package_data['manifest']
        manifest['app_version'] = app_version
        manifest['description'] = description
        manifest['publish_type'] = publish_type

        await self._write_all_app_configs(package_data)

        build_root = ApplicationFolder.get_app_build_root(self.app_id)
        # core zip
        target_path = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{app_version}_core.zip')
        await FileSystem.zip_folder_to(build_root, target_path=target_path, subfolders=['app', 'datafile'])

        # content zip
        content_folder = os.path.join(build_root, 'content')
        if not os.path.exists(content_folder):
            os.makedirs(content_folder, exist_ok=True)
        await FileSystem.update_folder_checksum(content_folder)
        content_path = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{app_version}_content.zip')
        await FileSystem.zip_folder_to(build_root, target_path=content_path, subfolders=['content'])

        # save publish record
        blob = json.dumps(package_data, ensure_ascii=False).encode('utf-8')
        ApplicationPublishModel.create(
            app_id=self.app_id,
            app_version=app_version,
            description=description,
            version_number=version_number,
            publish_type=publish_type,
            publish_date=datetime.fromisoformat(publish_date),
            package_data=blob,
        )

        # update latest version
        state = await self.get_state()
        state.latest_version = app_version
        state.save()

    async def create_package(self, description):
        from highorder_editor.model import ApplicationPublishModel
        state = await self.get_state()
        if not state or not state.latest_version:
            latest_package = None
        else:
            latest_package = ApplicationPublishModel.get_or_none((ApplicationPublishModel.app_id==self.app_id) & (ApplicationPublishModel.app_version==state.latest_version))
        return await self.do_create_package(latest_package=latest_package, description=description)

    async def publish_package(self, version):
        from highorder_editor.model import ApplicationPublishModel
        if version == 'building':
            await self.publish_building()
            return
        package = ApplicationPublishModel.get_or_none((ApplicationPublishModel.app_id==self.app_id) & (ApplicationPublishModel.app_version==version))
        if not package:
            raise Exception(f'package version {version} not exists')

        # apply content
        content_file = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{version}_content.zip')
        await FileSystem.unzip_to(content_file, get_publish_content_root(self.app_id), subfolder='content')

        # copy core to release root
        core_file = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{version}_core.zip')
        release_file = os.path.join(get_publish_release_root(self.app_id), f'APP_{self.app_id}_{version}.zip')
        await FileSystem.copy_file(core_file, release_file)
        await self.update_publish_state(version)

    async def update_publish_state(self, version):
        state = await self.get_state()
        current_version = state.current_version
        previous_version = state.previous_version if version == current_version else current_version
        prevprev_version = None if (previous_version == state.previous_version or version == state.previous_version) else state.previous_version

        release_data = json.dumps({
            'current': version,
            'previous': previous_version,
            'release_date': datetime.now().isoformat()
        }).encode('utf-8')
        release_file = os.path.join(get_publish_release_root(self.app_id), 'release.json')
        await FileSystem.write(release_file, release_data)

        if prevprev_version:
            prevprev_file = os.path.join(get_publish_release_root(self.app_id), f'APP_{self.app_id}_{prevprev_version}.zip')
            await FileSystem.delete(prevprev_file)

        state.previous_version = previous_version
        state.current_version = version
        state.save()

    async def publish_building(self):
        package_data = await self.get_package_data()
        now = datetime.now()
        version = 'b{}'.format(now.strftime('%y%m%d%H%M%S'))
        manifest = package_data['manifest']
        manifest['app_version'] = version
        manifest['description'] = f"auto building package of {version}"
        manifest['publish_type'] = 'major'

        await self._write_all_app_configs(package_data)

        # core zip to release root
        target_path = os.path.join(get_publish_release_root(self.app_id), f'APP_{self.app_id}_{version}.zip')
        await FileSystem.zip_folder_to(ApplicationFolder.get_app_build_root(self.app_id), target_path=target_path, subfolders=['app', 'datafile'])

        # update content and copy into content root
        content_folder = os.path.join(ApplicationFolder.get_app_build_root(self.app_id), 'content')
        await FileSystem.update_folder_checksum(content_folder)
        await FileSystem.copy_dir_to(ApplicationFolder.get_app_build_root(self.app_id), get_publish_content_root(self.app_id), subfolder='content')

        await self.update_publish_state(version)

    async def get_all_packages(self):
        from highorder_editor.model import ApplicationPublishModel
        ret = []
        query = ApplicationPublishModel.select().where(ApplicationPublishModel.app_id==self.app_id).order_by(ApplicationPublishModel.version_number.desc())
        for pub in query:
            ret.append({
                'app_id': pub.app_id,
                'app_version': pub.app_version,
                'description': pub.description,
                'publish_type': pub.publish_type,
                'publish_date': pub.publish_date,
            })
        return ret

    async def get_all_publish(self):
        from highorder_editor.model import ApplicationPublishModel
        ret = []
        query = ApplicationPublishModel.select().where(ApplicationPublishModel.app_id==self.app_id).order_by(ApplicationPublishModel.created.desc())
        for pub in query:
            ret.append({
                'app_id': pub.app_id,
                'app_version': pub.app_version,
                'description': pub.description,
                'publish_type': pub.publish_type,
                'publish_date': pub.publish_date,
            })
        return ret

# Alias for backward compatibility
Application = ApplicationDB


class ApplicationSetupService:
    @classmethod
    async def load(cls, app_id, server_url):
        setup_hola = await ApplicationStorage.load_app_hola(app_id, 'setup.hola')
        inst = cls(app_id, setup_hola, server_url)
        return inst

    def __init__(self, app_id, hola, server_url):
        self.app_id = app_id
        self.hola = hola
        self.server_url = server_url

    async def save_setup_hola(self, code=""):
        self.hola = code
        await ApplicationStorage.write_app_hola(self.app_id, 'setup.hola', code)

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
        app = await Application.load(self.app_id)
        valid_keys = await app.get_valid_clientkeys()
        if not valid_keys:
            await app.create_client_key()
            valid_keys = await app.get_valid_clientkeys()
        ck = valid_keys[0]
        client_key = ck['client_key']
        client_secret = ck['client_secret']
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
            return response
        else:
            error_type = response['error_type']
            error_msg = response['error_msg']
            raise Exception(f'Setup Failed: {error_type} \nmsg="{error_msg}"')

