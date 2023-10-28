import base64
import hashlib
import os
import shutil
from basepy.asynclib.threaded import threaded

class FileSystem:
    def __init__(self):
        pass

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
    @threaded
    def copy_file(cls, src_file, dest_file):
        shutil.copy(src_file, dest_file)

    @classmethod
    def file_md5(cls, fpath):
        with open(fpath, "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            return file_hash.hexdigest()
