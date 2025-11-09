import mimetypes
import random
import tempfile
import time
from datetime import datetime
import os


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

RANDOM_CHARSET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

def random_string(num, prefix='', lower=True):
    generated = ''.join(random.choice(RANDOM_CHARSET) for _ in range(num))
    rst = f'{prefix}{generated}'
    if lower:
        rst = rst.lower()
    return rst

def extract_name_in_email(email):
    index = email.find('@')
    return email[0:index]

class IDGenerator(object):
    shift_list = [35, 30, 25, 20, 15, 10, 5, 0]
    charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

    @classmethod
    def format_ts(cls):
        now_ts = int(datetime.now().timestamp())
        id_list = []
        for n in cls.shift_list:
            c = cls.charset[(now_ts >> n) & 31]
            id_list.append(c)
        assert len(id_list) == 8
        return ''.join(id_list)

    @classmethod
    def random_id(cls, number=10, lower=False):
        generated = ''.join(random.choice(cls.charset) for _ in range(number))
        if lower:
            generated = generated.lower()
        return '{}'.format(generated)

    @classmethod
    def prefix_random_id(cls, prefix, number=10, lower=False):
        assert len(prefix) == 2
        generated = ''.join(random.choice(cls.charset) for _ in range(number))
        if lower:
            return '{}{}'.format(prefix.lower(), generated.lower())
        else:
            return '{}{}'.format(prefix.upper(), generated.upper())

    @classmethod
    def time_random_id(cls, number=6, lower=False):
        timestr = cls.format_ts()
        generated = ''.join(random.choice(cls.charset) for _ in range(number))
        if lower:
            return '{}{}'.format(timestr.lower(), generated.lower())
        else:
            return '{}{}'.format(timestr.upper(), generated.upper())

    @classmethod
    def prefix_time_random_id(cls, prefix, number=6, lower=False):
        assert len(prefix) == 2
        timestr = cls.format_ts()
        generated = ''.join(random.choice(cls.charset) for _ in range(number))
        if lower:
            return '{}{}{}'.format(prefix.lower(), timestr.lower(), generated.lower())
        else:
            return '{}{}{}'.format(prefix.upper(), timestr.upper(), generated.upper())


class ApplicationFolder:
    root_folder = os.getcwd()
    upload_dir = tempfile.mkdtemp()

    @classmethod
    def set_root(cls, root_path):
        cls.root_folder = os.path.abspath(root_path)

    @classmethod
    def get_upload_dir(cls):
        return cls.upload_dir

    @classmethod
    def get_app_root(cls, app_id):
        app_root = os.path.join(cls.root_folder, f'APP_{app_id}', 'app')
        if not os.path.exists(app_root):
            os.makedirs(app_root, exist_ok=True)
        return app_root

    @classmethod
    def get_content_root(cls, app_id):
        content_root = os.path.join(cls.root_folder, f'APP_{app_id}', 'content')
        if not os.path.exists(content_root):
            os.makedirs(content_root, exist_ok=True)
        return content_root

    @classmethod
    def get_datafile_root(cls, app_id):
        datafile_root = os.path.join(cls.root_folder, f'APP_{app_id}', 'datafile')
        if not os.path.exists(datafile_root):
            os.makedirs(datafile_root, exist_ok=True)
        return datafile_root


def get_readable_filesize(size):
    units = ['', 'KB', 'MB', 'GB', 'TB']
    num = size
    idx = 0
    for idx in range(len(units)):
        if num > 1024:
            num = num / 1024.0
        else:
            break

    return f'{num:.1F} {units[idx]}'

def get_readable_date(date, short=False):
    if not date:
        return 'None'
    if short:
        return date.strftime('%H:%M:%S')
    return date.strftime('%Y-%m-%d %H:%M:%S')


def get_media_type(fpath):
    return mimetypes.guess_type(fpath)[0]

