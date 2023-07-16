import os
from basepy.asynclib.threaded import threaded
import json
from basepy.config import settings
from .configdata import ApplicationAccount, ApplicationSummary
import dataclass_factory
import time
from zipfile import ZipFile

factory = dataclass_factory.Factory()

class FileCache:
    _cache = {}

    @classmethod
    async def get(cls, filepath, parse_method="raw", max_cached = -1, cache_policy = 'normal'):
        if filepath in cls._cache:
            meta  = cls._cache[filepath]['meta']
            if 'expires' in meta:
                expired = time.time() - meta['expires']
                if expired >= 0:
                    del cls._cache[filepath]

                elif parse_method not in cls._cache[filepath]:
                    del cls._cache[filepath]
                else:
                    return cls._cache[filepath]['meta'], cls._cache[filepath][parse_method]
            else:
                file_meta = await cls.get_meta(filepath)
                if meta['modified'] != file_meta['modified'] or meta['size'] != file_meta['size']:
                    del cls._cache[filepath]
                else:
                    return cls._cache[filepath]['meta'], cls._cache[filepath][parse_method]

        if filepath not in cls._cache:
            meta, data = await cls.get_file_info(filepath, parse_method)

            if not data:
                data = {} if  parse_method == 'json' else ""

            now = int(time.time())
            if cache_policy == 'normal' and max_cached > 0:
                meta['expires'] = now + max_cached
            elif cache_policy == 'align':
                if max_cached < 60:
                    raise Exception(f'max cached time must greater than 60 when cache policy is align.')
                else:
                    meta['expires'] = now + (max_cached - (now % max_cached))
            cls._cache[filepath] = {
                'meta': meta,
                parse_method: data
            }
            return meta, data


    @classmethod
    @threaded
    def get_file_info(cls, filepath, parse_method):
        meta = cls._get_meta(filepath)
        if not meta['exist']:
            return meta, None

        if isinstance(filepath, str):
            with open(filepath, 'rb') as f:
                data = f.read()
                if parse_method == 'json':
                    data = json.loads(data)
                return meta, data
        elif isinstance(filepath, (list, tuple)):
            fpath = filepath[0]
            with ZipFile(fpath, 'r') as zfile:
                with zfile.open(filepath[1], 'r') as somefile:
                    data = somefile.read()
                    if parse_method == 'json':
                        data = json.loads(data)
                    return meta, data

        else:
            raise Exception(f'filepath only support str or tuple, but got {type(filepath)}.')

    @classmethod
    @threaded
    def get_meta(cls, filepath):
        return cls._get_meta(filepath)

    @classmethod
    def _get_meta(cls, filepath):
        if isinstance(filepath, (list, tuple)):
            fpath = filepath[0]
        else:
            fpath = filepath

        if not os.path.exists(fpath):
            meta = {'exist': False, 'size': 0, 'modified': None}
            return meta
        else:
            statinfo = os.stat(fpath)
            meta = {'size': statinfo.st_size, 'modified': statinfo.st_mtime, 'exist':True}
            return meta

class ConfigLoader:
    def __init__(self, app_id):
        self.app_id = app_id
        self.config_dir = os.path.abspath(os.path.join(settings.server.config_dir, f'APP_{app_id}'))
        self.config_file = None
        self.max_cached = -1
        self._account = None
        self._client_keys = None

    @property
    def account(self):
        return self._account

    @property
    def client_keys(self):
        return self._client_keys

    async def load(self):
        release_file = os.path.join(self.config_dir, 'release.json')
        meta, data = await FileCache.get(release_file, parse_method="json", max_cached=120, cache_policy='align')

        if meta['exist']:
            version = data['current']
            config_file = f'APP_{self.app_id}_{version}.zip'
            self.config_file = os.path.join(self.config_dir, config_file)
            self.max_cached = 1200

        jsondata = await self.get_config('app')
        app_summary = factory.load(jsondata, ApplicationSummary)
        self._client_keys = app_summary.client_keys

        jsondata = await self.get_config('account')
        account = factory.load(jsondata, ApplicationAccount)
        self._account = account

    def get_filepath(self, name):
        if self.config_file:
            return (self.config_file, name)
        else:
            return os.path.join(self.config_dir, name)

    async def get_config(self, name):
        jsonfile = self.get_filepath(f'app/{name}.json')
        meta, data = await FileCache.get(jsonfile, parse_method="json", max_cached=self.max_cached)
        return data

    async def get_datafile(self, name):
        jsonfile = self.get_filepath(f'datafile/{name}.json')
        meta, data = await FileCache.get(jsonfile, parse_method="json", max_cached=self.max_cached)
        return data
