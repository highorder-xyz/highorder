import base64
import hashlib
import os
import shutil
from basepy.asynclib.threaded import threaded
import zipfile


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

    @classmethod
    @threaded
    def copy_dir_to(cls, src_root, dest_root, subfolder=None):
        base = os.path.join(src_root, subfolder) if subfolder else src_root
        for root, dirs, files in os.walk(base):
            rel = os.path.relpath(root, base)
            target_dir = os.path.join(dest_root, rel) if rel != '.' else dest_root
            os.makedirs(target_dir, exist_ok=True)
            for f in files:
                src = os.path.join(root, f)
                dst = os.path.join(target_dir, f)
                shutil.copy(src, dst)

    @classmethod
    @threaded
    def zip_folder_to(cls, build_root, target_path, subfolders):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with zipfile.ZipFile(target_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for sub in subfolders:
                folder = os.path.join(build_root, sub)
                if not os.path.isdir(folder):
                    continue
                for base, _, files in os.walk(folder):
                    for name in files:
                        full = os.path.join(base, name)
                        arc = os.path.relpath(full, build_root)
                        zf.write(full, arcname=arc)

    @classmethod
    @threaded
    def unzip_to(cls, zip_path, dest_root, subfolder=None):
        os.makedirs(dest_root, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            if not subfolder:
                zf.extractall(dest_root)
            else:
                # Extract only contents under given subfolder
                members = [m for m in zf.namelist() if m.startswith(subfolder.rstrip('/') + '/')]
                for m in members:
                    zf.extract(m, dest_root)

    @classmethod
    @threaded
    def update_folder_checksum(cls, folder):
        mapping = {}
        base_len = len(folder.rstrip(os.sep)) + 1
        for root, _, files in os.walk(folder):
            for f in files:
                path = os.path.join(root, f)
                rel = path[base_len:].replace('\\', '/') if len(path) > base_len else f
                mapping[rel] = cls.file_md5(path)
        out = os.path.join(folder, 'checksums.json')
        import json
        with open(out, 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(mapping, ensure_ascii=False))

    @classmethod
    @threaded
    def write(cls, file_path, data: bytes):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(data)

    @classmethod
    @threaded
    def delete(cls, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
