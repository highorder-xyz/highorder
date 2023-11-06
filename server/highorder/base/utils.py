import string
import random
from datetime import datetime
import time

import base64
import hashlib
import json
import hmac

class IDPrefix:
    USER = 'UU'
    PROFILE = 'UP'
    SESSION = 'SS'
    OBJECT = 'OB'

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



def random_str(number=10):
    generated = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(number))
    return generated


def random_id(prefix, number=10):
    assert len(prefix) == 2
    generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(number))
    return '{}{}'.format(prefix.upper(), generated)


def time_random_id(prefix, number=6):
    assert len(prefix) == 2
    generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(number))
    return '{}{}{}'.format(prefix.upper(), IDGenerator.format_ts(), generated)


class AutoList(list):
    def add(self, list_or_obj):
        if isinstance(list_or_obj, (list, tuple)):
            self.extend(list_or_obj)
        elif list_or_obj:
            self.append(list_or_obj)

    @property
    def first(self):
        if len(self) > 0:
            return self[0]
        else:
            return None


class StampToken:
    DEFAULT_STAMP = {
        "stamp_id": "stamp_id",
        "stamp_secret": "stamp_secret",
        "hash_method": "sha1"
    }
    def __init__(self, stamps = None):
        self.version = 'v1'
        self.stamps = stamps or []
        self.stamps.insert(0, self.DEFAULT_STAMP)

    def signature(self, stamp_id, body):
        stamp = next(filter(lambda x: x['stamp_id'] == stamp_id, self.stamps), None)
        if not stamp:
            raise Exception('no related stamp info found for stamp_id {stamp_id}')
        secret = stamp['stamp_secret']
        hash_method = stamp['hash_method']
        if hash_method == 'sha256':
            digestmod = hashlib.sha256
        elif hash_method == 'sha1':
            digestmod = hashlib.sha1
        else:
            raise Exception(f'stamp token hashmethod {hash_method} not supported')
        sign = hmac.new(
            bytes(secret, 'latin-1'),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest().lower()
        return sign


    def make(self, stamp_id, content):
        body = json.dumps({
            "m": {
                "ts": int(time.time()),
            },
            "c": content
        }, separators=(',', ':'))
        body = base64.b64encode(body.encode('utf-8'))
        sign = self.signature(stamp_id, body)
        return f'{self.version}.{stamp_id}.{sign}.' + body.decode('utf-8')


    def verify(self, token):
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        try:
            version, stamp_id, sign, body = token.split('.')
        except:
            return False

        _sign = self.signature(stamp_id, body.encode('utf-8'))
        if _sign == sign:
            return True
        return False

    def load(self, token, ignore_error=False):
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        try:
            version, stamp_id, sign, body = token.split('.')
        except:
            return None

        _sign = self.signature(stamp_id, body.encode('utf-8'))
        if _sign != sign:
            if ignore_error:
                return None
            else:
                raise Exception(f'sign not right.')

        body = bytes(body, encoding='utf-8')
        obj = json.loads(base64.b64decode(body).decode('utf-8'))
        return obj['c']

