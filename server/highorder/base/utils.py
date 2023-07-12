import string
import random
from datetime import datetime


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



def random_id(prefix, number=10):
    assert len(prefix) == 2
    generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(number))
    return '{}{}'.format(prefix.upper(), generated)


def time_random_id(prefix, number=6):
    assert len(prefix) == 2
    generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(number))
    return '{}{}{}'.format(prefix.upper(), IDGenerator.format_ts(), generated)