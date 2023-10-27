import base64
import hashlib
import io
import json
import os
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, field
import shutil
from basepy.asynclib.threaded import threaded
import zipfile
import tempfile
from pathlib import PurePosixPath

objects_storage_schemes = ['cos', 's3', 'minio', 'oss', 'obs']

@threaded
def get_file_md5(filepath, digest='hex'):
    content_md5 = hashlib.new('md5')
    with open(filepath, 'rb') as f:
        content_md5.update(f.read())

    if digest == 'hex':
        return content_md5.hexdigest()
    elif digest == 'base64':
        return base64.b64encode(content_md5.digest()).decode('utf-8')
    else:
        return content_md5.digest()

def get_file_md5_sync(filepath, digest='hex'):
    content_md5 = hashlib.new('md5')
    with open(filepath, 'rb') as f:
        content_md5.update(f.read())

    if digest == 'hex':
        return content_md5.hexdigest()
    elif digest == 'base64':
        return base64.b64encode(content_md5.digest()).decode('utf-8')
    else:
        return content_md5.digest()

def get_content_md5(content, digest='hex'):
    content_md5 = hashlib.new('md5')
    content_md5.update(content)

    if digest == 'hex':
        return content_md5.hexdigest()
    elif digest == 'base64':
        return base64.b64encode(content_md5.digest()).decode('utf-8')
    else:
        return content_md5.digest()

@dataclass
class FileResourceInfo:
    path: str
    location: str = field(default='local')
    bucket: str = field(default='')
    credential_key: str = field(default='')
    args: dict = field(default_factory=dict)

    @classmethod
    def parse(cls, filepath):
        if filepath.find('://') != -1:
            p = urlparse(filepath)
            if '+' in p.scheme:
                scheme, credential_key = p.scheme.split('+', 2)
            else:
                scheme, credential_key = p.scheme, ""
            if scheme in objects_storage_schemes:
                region = ''
                args = {}
                if p.query:
                    args = parse_qs(p.query)
                return cls(location=scheme, path=p.path, bucket=p.netloc, credential_key=credential_key, args=args)
            else:
                raise Exception(f'not supported fileresource url {filepath}')
        else:
            return cls(location='local', path=filepath, bucket='')

    def joinpath(self, *args):
        if self.location == 'local':
            self.path = os.path.join(*args)
        else:
            self.path = PurePosixPath(self.path).joinpath(*args).as_posix()


class FileSystem:
    def __init__(self):
        pass

    @classmethod
    @threaded
    def shutil_copy(cls, src, dest):
        shutil.copy(src, dest)

    @classmethod
    @threaded
    def shutil_move(cls, src, dest):
        temp_target = f'{dest}.tmp'
        shutil.move(src, temp_target)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                shutil.rmtree(dest, ignore_errors=True)
            else:
                os.remove(dest)
        os.rename(temp_target, dest)

    @classmethod
    @threaded
    def rmtree(cls, dest):
        shutil.rmtree(dest, ignore_errors=True)

    @classmethod
    @threaded
    def remove(cls, dest):
        if os.path.exists(dest):
            os.remove(dest)

    @classmethod
    @threaded
    def rename(cls, src, dest):
        if os.path.exists(src):
            os.remove(src)
        os.rename(src, dest)

    @classmethod
    @threaded
    def get_files(cls, root):
        return cls.walk_all_files(root)

    @classmethod
    def walk_all_files(cls, root):
        all_files = []
        rootlen = len(root) + 1
        for base, _, files in os.walk(root):
            for file in files:
                fn = os.path.join(base, file)
                relative_path = fn[rootlen:]
                relative_path = relative_path.replace("\\", '/')
                all_files.append((fn, relative_path))
        return all_files


    @classmethod
    async def write(cls, dest_file, data):
        dest_res = FileResourceInfo.parse(dest_file)
        with open(f'{dest_res.path}.tmp', 'rb') as f:
            f.write(data)
        await cls.rename(f'{dest_res.path}.tmp', dest_res.path)

    @classmethod
    async def read(cls, dest_file):
        dest_res = FileResourceInfo.parse(dest_file)
        with open(dest_res.path, 'rb') as f:
            return f.read()

    @classmethod
    async def delete(cls, dest_file):
        dest_res = FileResourceInfo.parse(dest_file)
        await cls.remove(dest_res.path)


    @classmethod
    async def copy_file(cls, src_file, dest_file):
        src_res = FileResourceInfo.parse(src_file)
        dest_res = FileResourceInfo.parse(dest_file)
        await cls.shutil_copy(src_res.path, dest_res.path)

    @classmethod
    def file_md5(cls, fpath):
        with open(fpath, "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            return file_hash.hexdigest()