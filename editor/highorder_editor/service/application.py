

from dataclasses import dataclass, field
import tempfile
from typing import List

from highorder_editor.base.helpers import (
    get_app_build_root, get_config_root, get_publish_content_root, get_content_root, get_datafile_root, get_media_type,
    get_publish_package_root, get_publish_release_root, get_upload_dir, random_string
)
from datetime import datetime
import os
from basepy.asynclib.threaded import threaded
from basepy.config import settings
from highorder_editor.base.fs import FileSystem
import dataclass_factory
from dataclass_factory.schema_helpers import isodatetime_schema
import json
from dictdiffer import diff
import hmac
import hashlib
import httpx


factory = dataclass_factory.Factory(schemas={
        datetime: isodatetime_schema,
    })

@dataclass
class ApplicationClientKey:
    app_id: str
    client_key: str
    client_secret: str
    valid: bool

@dataclass
class ApplicationSummary:
    app_id: str
    app_name: str
    client_keys: List[ApplicationClientKey] = field(default_factory=list)

@dataclass
class ApplicationManifest:
    app_id: str
    app_version: str
    description: str
    publish_type: str
    publish_date: datetime


@threaded
def write_app_configs(app_id, package_data):
    app_config_root = get_config_root(app_id)
    if not os.path.exists(app_config_root):
        os.makedirs(app_config_root, exist_ok=True)
    for key in package_data:
        with open(os.path.join(app_config_root, f'{key}.json'), 'w') as f:
            f.write(json.dumps(package_data[key], ensure_ascii=False))

@threaded
def write_app_hola(app_id, name, code):
    app_config_root = get_config_root(app_id)
    if not os.path.exists(app_config_root):
        os.makedirs(app_config_root, exist_ok=True)
    with open(os.path.join(app_config_root, name), 'w') as f:
        f.write(code)

def translate_upload_path(up_path):
    if up_path.startswith('/_f/'):
        return os.path.join(get_upload_dir(), up_path[4:])
    return up_path

class ApplicationContentService:
    def __init__(self, model, **kwargs):
        assert model != None
        self.model = model

    @classmethod
    async def load(cls, app_id):
        model = await ApplicationConfigModel.load(app_id=app_id, key="content")
        if model == None:
            model = await ApplicationConfigModel.create(app_id=app_id, key="content", config={"main":{"files":[]}})
        return cls(model)

    @property
    def config(self):
        return self.model.config

    def get_collections(self):
        return self.model.config.keys()

    async def add_collection(self, name):
        if name not in self.model.config:
            self.model.config[name] = {'files': []}
            await self.model.save()

    def get_collection_root(self, collection):
        collection_root = os.path.join(get_content_root(self.model.app_id), collection)
        if not os.path.exists(collection_root):
            os.makedirs(collection_root, exist_ok=True)
        return collection_root

    async def save_files(self, collection, data_files):
        collection_data = self.model.config.setdefault(collection, {})
        files_meta = collection_data.setdefault('files', [])
        collection_root = self.get_collection_root(collection)
        data_dirs = []
        for file in data_files:
            src_path = translate_upload_path(file)
            filename = os.path.basename(file)
            data_dirs.append(os.path.dirname(src_path))
            dest_path = os.path.join(collection_root, filename)
            statinfo = os.stat(src_path)
            await FileSystem.copy_file(src_path, dest_path)

            others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
            others_meta.append(factory.dump(UploadedFileRecord(
                name=filename,
                size=statinfo.st_size,
                media_type = get_media_type(src_path),
                uploaded=datetime.now()
            )))
            files_meta = others_meta

        self.model.config[collection]['files'] = files_meta
        await self.save()
        await self.remove_uploaded_files(data_dirs)

    async def remove_uploaded_files(self, data_dirs):
        for folder in data_dirs:
            await FileSystem.rmtree(folder)

    async def get_files(self, collection, page=1):
        files_meta = self.model.config.get(collection).get('files', [])
        files = [factory.load(file_meta, UploadedFileRecord) for file_meta in files_meta]
        return files

    async def delete_file(self, collection, filename):
        files_meta = self.model.config.get(collection, {}).get('files', [])
        others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
        self.model.config[collection]['files'] = others_meta
        await self.save()
        collection_root = self.get_collection_root(collection)
        dest = os.path.join(collection_root, filename)
        await FileSystem.remove(dest)


    async def save(self):
        await self.model.save()
        await write_app_configs(self.model.app_id, {'content': self.model.config})


class ApplicationDataFileService:
    def __init__(self, model, **kwargs):
        assert model != None
        self.model = model

    @classmethod
    async def load(cls, app_id):
        model = await ApplicationConfigModel.load(app_id=app_id, key="datafile")
        if model == None:
            model = await ApplicationConfigModel.create(app_id=app_id, key="datafile", config={"files":[]})
        return cls(model)

    @property
    def config(self):
        return self.model.config

    async def save_files(self, data_files):
        files_meta = self.model.config.setdefault('files', [])
        data_dirs = []
        for file in data_files:
            src_path = translate_upload_path(file)
            filename = os.path.basename(file)
            data_dirs.append(os.path.dirname(src_path))
            dest_path = os.path.join(get_datafile_root(self.model.app_id), filename)
            statinfo = os.stat(src_path)
            await FileSystem.copy_file(src_path, dest_path)

            others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
            others_meta.append(factory.dump(UploadedFileRecord(
                name=filename,
                size=statinfo.st_size,
                media_type = 'json',
                uploaded=datetime.now()
            )))
            files_meta = others_meta

        self.model.config['files'] = files_meta
        await self.save()
        await self.remove_uploaded_files(data_dirs)

    async def remove_uploaded_files(self, data_dirs):
        for folder in data_dirs:
            await FileSystem.rmtree(folder)

    async def get_files(self, page=1):
        files_meta = self.model.config.get('files', [])
        files = [factory.load(file_meta, UploadedFileRecord) for file_meta in files_meta]
        return files

    async def delete_file(self, filename):
        files_meta = self.model.config.get('files', [])
        others_meta = list(filter(lambda x: x['name'] != filename, files_meta))
        self.model.config['files'] = others_meta
        await self.save()
        dest = os.path.join(get_datafile_root(app_id=self.model.app_id), filename)
        await FileSystem.remove(dest)


    async def save(self):
        await self.model.save()
        await write_app_configs(self.model.app_id, {'datafile': self.model.config})


class Application():
    def __init__(self, model, **kwargs):
        assert model != None
        self.model = model
        self.members = []
        self.workspace_name = None
        self.hola_model = None

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
        m = await ApplicationModel.load(app_id=app_id)
        if not m:
            return None
        inst = cls(m)
        await inst.check_app_info()
        return inst

    async def save_profile(self, name, description):
        if name:
            self.model.name = name
        if description:
            self.model.description = description
        await self.model.save()

    async def load_hola_model(self, force=True):
        if not self.hola_model or force:
            model = await ApplicationHolaModel.load(app_id=self.app_id)
            if model == None:
                model = await ApplicationHolaModel.create(
                    app_id = self.app_id,
                    hola = {},
                    code = {}
                )
            self.hola_model = model

    async def get_state(self):
        state = await ApplicationStateModel.load(app_id=self.app_id)
        if not state:
            state = await ApplicationStateModel.create(app_id=self.app_id)
        return state

    async def get_hola_config(self):
        await self.load_hola_model()
        return self.hola_model.hola

    async def get_hola_code(self):
        await self.load_hola_model()
        return self.hola_model.code.get('main.hola', '')

    async def save_hola_config(self, config):
        if not self.hola_model:
            raise Exception('hola model not loaded')
        self.hola_model.hola = config
        await self.hola_model.save()
        await write_app_configs(self.app_id, {'main.hola': config})

    async def save_hola_code(self, code):
        if not self.hola_model:
            await self.load_hola_model()
        self.hola_model.code = {"main.hola": code}
        await self.hola_model.save()
        await write_app_hola(self.app_id, 'main.hola', code)

    async def write_app_info(self):
        client_keys = await self.get_valid_clientkeys()
        app = ApplicationSummary(
            app_id = self.app_id,
            app_name = self.name,
            client_keys = client_keys
        )
        await write_app_configs(self.app_id, {'app': factory.dump(app)})

    async def check_app_info(self):
        app_config_file = os.path.join(get_config_root(self.app_id), 'app.json')
        if not os.path.exists(app_config_file):
            await self.write_app_info()


    async def get_valid_clientkeys(self):
        clientkeys = []
        keys = await ApplicationClientKeyModel.filter(app_id=self.app_id).order_by('-created')
        for key in keys:
            clientkeys.append(ApplicationClientKey(app_id=key.app_id,
                client_key=key.clientkey_id,
                client_secret = key.clientkey_secret,
                valid = key.valid))
        return clientkeys

    async def get_client_secret(self, client_key):
        keys = await ApplicationClientKeyModel.filter(app_id=self.app_id, clientkey_id=client_key).order_by('-created').all()
        if not keys:
            return None
        return keys[0].clientkey_secret

    async def create_client_key(self):
        key_id = random_string(8)
        key_secret = random_string(32)
        clientkey = await ApplicationClientKeyModel.create(app_id = self.app_id,
                clientkey_id = key_id, clientkey_secret = key_secret, valid=True
            )
        await self.write_app_info()
        return clientkey

    def next_major_version(self, version):
        major, minor = version.split('.')
        major = int(major)
        minor = int(minor)
        major = major + 1
        minor = 0
        return f'{major}.{minor}', major*10000 + minor

    def next_minor_version(self, version):
        major, minor = version.split('.')
        major = int(major)
        minor = int(minor)
        minor = minor + 1
        if minor > 9999:
            raise Exception('minor version not allowed to be greater than 9999. ')
        return f'{major}.{minor}', major*10000 + minor

    async def get_package_data(self):
        publish_date = datetime.now()

        package_data = {}
        manifest = ApplicationManifest(
            app_id = self.app_id,
            app_version = '',
            description = '',
            publish_type = '',
            publish_date = publish_date,
        )

        package_data['manifest'] = factory.dump(manifest)

        client_keys = await self.get_valid_clientkeys()
        app = ApplicationSummary(
            app_id = self.app_id,
            app_name = self.name,
            client_keys = client_keys
        )

        package_data['app'] = factory.dump(app)

        for key in ['content', 'datafile']:
            model = await ApplicationConfigModel.load(app_id = self.app_id, key=key)
            package_data[key] = model.config

        hola_model = await ApplicationHolaModel.load(app_id = self.app_id)
        package_data['main.hola'] = hola_model.hola
        return package_data

    async def do_create_package(self, latest_package, description):
        package_data = await self.get_package_data()
        publish_date = package_data['manifest']['publish_date']

        if latest_package:
            latest_package_data = latest_package.package_data
            latest_version = latest_package.app_version
            first = {
                'hola': latest_package_data['hola'],
            }
            second = {
                'hola': package_data['hola'],
            }

            d = list(diff(first, second))
            if len(d) > 0:
                publish_type = 'major'
                app_version, version_number = self.next_major_version(latest_version)
            else:
                first = {
                    'content': latest_package_data['content'],
                    'datafile': latest_package_data['datafile'],
                }
                second = {
                    'content': package_data['content'],
                    'datafile': package_data['datafile']
                }

                datadiff = list(diff(first, second))
                if len(datadiff) > 0:
                    publish_type = 'minor'
                    app_version, version_number = self.next_minor_version(latest_version)
                else:
                    raise Exception('No changes found to latest release, No package need to be created.')

        else:
            app_version = '1.0'
            version_number = '10000'
            publish_type = 'major'

        manifest = package_data['manifest']
        manifest['app_version'] = app_version
        manifest['description'] = description
        manifest['publish_type'] = publish_type

        await write_app_configs(self.app_id, package_data)

        target_path = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{app_version}_core.zip')
        await FileSystem.zip_folder_to(get_app_build_root(self.app_id), target_path=target_path, subfolders=['app', 'datafile'])


        content_folder = os.path.join(get_app_build_root(self.app_id), 'content')
        if not os.path.exists(content_folder):
            os.makedirs(content_folder, exist_ok=True)
        await FileSystem.update_folder_checksum(content_folder)

        content_path = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{app_version}_content.zip')
        await FileSystem.zip_folder_to(get_app_build_root(self.app_id), target_path=content_path, subfolders=['content'])

        await ApplicationPublishModel.create(
            app_id = self.app_id,
            app_version = app_version,
            description = description,
            version_number = version_number,
            publish_type = publish_type,
            publish_date = publish_date,
            package_data = package_data,
        )

        state = await self.get_state()
        state.latest_version = app_version
        await state.save()

    async def create_package(self, description):
        state = await self.get_state()
        if not state or state.latest_version == None:
            latest_package = None
        else:
            latest_package = await ApplicationPublishModel.load(app_id=self.app_id, app_version=state.latest_version)
        return await self.do_create_package(latest_package=latest_package, description=description)

    async def publish_package(self, version):
        if version == 'building':
            await self.publish_building()
            return
        package = await ApplicationPublishModel.load(app_id=self.app_id, app_version=version)
        if not package:
            raise Exception(f'package version {version} not exists')
        _, temp_content_file = tempfile.mkstemp()
        content_file = os.path.join(get_publish_package_root(self.app_id), f'APP_{self.app_id}_{version}_content.zip')
        await FileSystem.copy_file(content_file, temp_content_file)

        await FileSystem.unzip_to(temp_content_file, get_publish_content_root(self.app_id), subfolder="content")
        await FileSystem.remove(temp_content_file)


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
        release_file = os.path.join(get_publish_release_root(self.app_id), f'release.json')
        await FileSystem.write(release_file, release_data)

        if prevprev_version:
            prevprev_file = os.path.join(get_publish_release_root(self.app_id), f'APP_{self.app_id}_{prevprev_version}.zip')
            await FileSystem.delete(prevprev_file)

        state.previous_version = previous_version
        state.current_version = version
        await state.save()


    async def publish_building(self):
        package_data = await self.get_package_data()
        now = datetime.now()
        version = 'b{}'.format(now.strftime('%y%m%d%H%M%S'))
        manifest = package_data['manifest']
        manifest['app_version'] = version
        manifest['description'] = f"auto building package of {version}"
        manifest['publish_type'] = "major"

        await write_app_configs(self.app_id, package_data)

        target_path = os.path.join(get_publish_release_root(self.app_id), f'APP_{self.app_id}_{version}.zip')
        await FileSystem.zip_folder_to(get_app_build_root(self.app_id), target_path=target_path, subfolders=['app', 'datafile'])

        content_folder = os.path.join(get_app_build_root(self.app_id), 'content')
        await FileSystem.update_folder_checksum(content_folder)

        await FileSystem.copy_dir_to(get_app_build_root(self.app_id), get_publish_content_root(self.app_id), subfolder="content")

        await self.update_publish_state(version)


    async def get_all_packages(self):
        ret = []
        all_packages = await ApplicationPublishModel.filter(app_id=self.app_id).order_by("-version_number")
        for pub in all_packages:
            ret.append(ApplicationManifest(app_id=pub.app_id, app_version=pub.app_version,
                description=pub.description,
                publish_type=pub.publish_type,
                publish_date=pub.publish_date))
        return ret

    async def get_all_publish(self):
        ret = []
        all_pub = await ApplicationPublishModel.filter(app_id=self.app_id).order_by("-created")
        for pub in all_pub:
            ret.append(ApplicationManifest(app_id=pub.app_id, app_version=pub.app_version,
                description=pub.description,
                publish_type=pub.publish_type,
                publish_date=pub.publish_date))
        return ret


class ApplicationSetupService:
    @classmethod
    async def load_or_create(cls, app_id, server_name):
        server = cls.get_server_byname(server_name)
        if not server:
            raise Exception(f'Server with name: {server_name} not exists.')
        m = await ApplicationSetupModel.load(app_id=app_id, server_name=server_name)
        if not m:
            m = await ApplicationSetupModel.create(app_id=app_id, server_name=server_name, hola="")
        inst = cls(m, server)
        return inst

    def __init__(self, model, server):
        self.model = model
        self.server = server

    @property
    def app_id(self):
        return self.model.app_id

    @property
    def server_name(self):
        return self.model.server_name

    @property
    def hola(self):
        return self.model.hola

    @property
    def last_run_date(self):
        return self.model.last_run_date

    @property
    def last_run_hola(self):
        return self.model.last_run_hola

    async def save_setup_hola(self, hola_code=""):
        self.model.hola = hola_code
        await self.model.save()

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
        client_key = self.server['client_key']
        client_secret = self.server['client_secret']
        server_url = self.server['server_url']
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
        hola_code = self.model.hola
        response = await self.call_setup_service(hola_code)
        if response['ok']:
            self.model.last_run_hola = hola_code
            self.model.last_run_date = datetime.now()
            await self.model.save()
        else:
            error_type = response['error_type']
            error_msg = response['error_msg']
            raise Exception(f'Setup Failed: {error_type} \nmsg="{error_msg}"')

