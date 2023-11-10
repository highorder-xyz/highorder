import redis
from redis.asyncio.sentinel import Sentinel
import redis.asyncio as aredis
from basepy.config import settings
from urllib.parse import urlparse
from contextlib import asynccontextmanager

g_sentinel = None
g_redis = None


def parse_redis_url(url):
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 6379
    return (host, port, parsed.username, parsed.password)


@asynccontextmanager
async def get_redis():
    global g_sentinel, g_redis
    conn = None
    try:
        if g_sentinel == None or g_redis == None:
            urls = list(map(lambda x: parse_redis_url(x), settings.app.redis_urls))
            if len(urls) >= 2:
                g_sentinel = Sentinel(urls)
            else:
                host, port, username, password = urls[0]
                creds_provider = None
                if username and password:
                    creds_provider = redis.UsernamePasswordCredentialProvider(
                        username, password
                    )
                g_redis = aredis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True,
                    credential_provider=creds_provider,
                )
        if g_sentinel:
            conn = g_sentinel.master_for("mymaster")
        elif g_redis:
            conn = g_redis
        yield conn
    finally:
        if conn:
            await conn.close()


class InstantDataStorageService:
    def __init__(self, app_id, name):
        self.key_prefix = f"a:{app_id[2:]}:{name}"

    @classmethod
    async def load(cls, app_id, name):
        return cls(app_id, name)

    async def expire(self, name, time, nx=False, xx=False, gt=False, lt=False):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.expire(f"{prefix}:{name}", time, nx, xx, gt, lt)

    async def expireat(self, name, when, nx=False, xx=False, gt=False, lt=False):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.expireat(f"{prefix}:{name}", when, nx, xx, gt, lt)

    async def get(self, name):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.get(f"{prefix}:{name}")

    async def set(
        self,
        name,
        value,
        ex=None,
        px=None,
        nx=False,
        xx=False,
        keepttl=False,
        get=False,
        exat=None,
        pxat=None,
    ):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.set(
                f"{prefix}:{name}", value, ex, px, nx, xx, keepttl, get, exat, pxat
            )

    async def setex(self, name, time, value):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.setex(f"{prefix}:{name}", time, value)

    async def setnx(self, name, value):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.setnx(f"{prefix}:{name}", value)

    async def hexists(self, name, key):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hexists(f"{prefix}:{name}", key)

    async def hget(self, name, key):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hget(f"{prefix}:{name}", key)

    async def hgetall(self, name):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hgetall(f"{prefix}:{name}")

    async def hlen(self, name):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hlen(f"{prefix}:{name}")

    async def hsetnx(self, name, key, value):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hsetnx(f"{prefix}:{name}", key, value)

    async def hset(self, name, key=None, value=None, mapping=None, items=None):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hset(f"{prefix}:{name}", key, value, mapping, items)

    async def hmget(self, name, keys, *args):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hmget(f"{prefix}:{name}", keys, *args)

    async def hmset(self, name, mapping):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.hmset(f"{prefix}:{name}", mapping)

    async def lindex(self, name, index):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lindex(f"{prefix}:{name}", index)

    async def llen(self, name):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.llen(f"{prefix}:{name}")

    async def lpop(self, name, count=None):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lpop(f"{prefix}:{name}", count)

    async def lpush(self, name, *values):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lpush(f"{prefix}:{name}", *values)

    async def lpushx(self, name, *values):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lpushx(f"{prefix}:{name}", *values)

    async def lrem(self, name, count, value):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lrem(f"{prefix}:{name}", count, value)

    async def lset(self, name, index, value):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.lset(f"{prefix}:{name}", index, value)

    async def zadd(
        self,
        name,
        mapping,
        nx=False,
        xx=False,
        ch=False,
        incr=False,
        gt=False,
        lt=False,
    ):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.zadd(f"{prefix}:{name}", mapping, nx, xx, ch, incr, gt, lt)

    async def zcard(self, name):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.zcard(f"{prefix}:{name}")

    async def zcount(self, name, min, max):
        prefix = self.key_prefix
        async with get_redis() as r:
            return await r.zcount(f"{prefix}:{name}", min, max)


class UserInstantDataStorageService(InstantDataStorageService):
    def __init__(self, user_id, name):
        self.key_prefix = f"u:{user_id[2:]}:{name}"

    @classmethod
    async def load(cls, user_id, name):
        return cls(user_id, name)
