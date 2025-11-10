from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from postmodel import models
from postmodel.transaction import in_transaction

from highorder.base.model import MetaverModel, DB_NAME


class InstantKV(MetaverModel):
    class Meta:
        table = "instant_kv"
        primary_key = ("prefix", "name", "field")
        db_name = DB_NAME

    prefix = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    field = models.CharField(max_length=256, default="")
    value = models.TextField()
    expire_at = models.DatetimeField(null=True)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


class InstantDataStorageDBService:
    def __init__(self, app_id: str, name: str):
        # keep same prefix convention as Redis version
        self.key_prefix = f"a:{app_id[2:]}:{name}"

    @classmethod
    async def load(cls, app_id: str, name: str) -> "InstantDataStorageDBService":
        return cls(app_id, name)

    async def _purge_expired(self, name: str) -> None:
        now = _now_utc()
        await InstantKV.filter(prefix=self.key_prefix, name=name).filter(
            expire_at__lte=now
        ).delete()

    async def _set_expire_at(self, name: str, expire_at: Optional[datetime]) -> int:
        # update TTL for all rows under the same key (string or hash)
        q = InstantKV.filter(prefix=self.key_prefix, name=name)
        if expire_at is None:
            return await q.update(expire_at=None)
        else:
            return await q.update(expire_at=expire_at)

    # ----- key TTL -----
    async def expire(self, name: str, time: int, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        await self._purge_expired(name)
        # Simplified semantics: ignore nx/xx/gt/lt for now
        expire_at = _now_utc() + timedelta(seconds=int(time))
        updated = await self._set_expire_at(name, expire_at)
        return updated > 0

    async def expireat(self, name: str, when, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        await self._purge_expired(name)
        # when can be int (unix ts) or datetime
        if isinstance(when, (int, float)):
            expire_at = datetime.fromtimestamp(int(when), timezone.utc)
        elif isinstance(when, datetime):
            expire_at = when
        else:
            expire_at = _now_utc()
        updated = await self._set_expire_at(name, expire_at)
        return updated > 0

    # ----- simple string value -----
    async def get(self, name: str):
        await self._purge_expired(name)
        row = await InstantKV.filter(prefix=self.key_prefix, name=name, field="").first()
        if not row:
            return None
        if row.expire_at and row.expire_at <= _now_utc():
            await InstantKV.filter(prefix=self.key_prefix, name=name).delete()
            return None
        return row.value

    async def set(
        self,
        name: str,
        value,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: Optional[int] = None,
        pxat: Optional[int] = None,
    ):
        await self._purge_expired(name)
        prev = await InstantKV.filter(prefix=self.key_prefix, name=name, field="").first()
        if nx and prev:
            return prev.value if get else False
        if xx and not prev:
            return None if get else False

        expire_at: Optional[datetime] = None
        if keepttl and prev:
            expire_at = prev.expire_at
        if ex is not None:
            expire_at = _now_utc() + timedelta(seconds=int(ex))
        elif exat is not None:
            expire_at = datetime.fromtimestamp(int(exat), timezone.utc)
        elif px is not None:
            expire_at = _now_utc() + timedelta(milliseconds=int(px))
        elif pxat is not None:
            expire_at = datetime.fromtimestamp(int(pxat) / 1000, timezone.utc)

        oldval = prev.value if (prev and get) else None
        if prev:
            prev.value = str(value)
            if not keepttl:
                prev.expire_at = expire_at
            await prev.save(update_fields=["value", "expire_at"])
        else:
            await InstantKV.create(
                prefix=self.key_prefix,
                name=name,
                field="",
                value=str(value),
                expire_at=expire_at,
            )
        return oldval if get else True

    async def setex(self, name: str, time: int, value):
        expire_at = _now_utc() + timedelta(seconds=int(time))
        await self._purge_expired(name)
        prev = await InstantKV.filter(prefix=self.key_prefix, name=name, field="").first()
        if prev:
            prev.value = str(value)
            prev.expire_at = expire_at
            await prev.save(update_fields=["value", "expire_at"])
        else:
            await InstantKV.create(
                prefix=self.key_prefix,
                name=name,
                field="",
                value=str(value),
                expire_at=expire_at,
            )
        return True

    async def setnx(self, name: str, value):
        await self._purge_expired(name)
        prev = await InstantKV.filter(prefix=self.key_prefix, name=name, field="").first()
        if prev:
            return False
        await InstantKV.create(
            prefix=self.key_prefix,
            name=name,
            field="",
            value=str(value),
            expire_at=None,
        )
        return True

    # ----- hash operations -----
    async def hexists(self, name: str, key: str):
        await self._purge_expired(name)
        row = await InstantKV.filter(prefix=self.key_prefix, name=name, field=key).first()
        return bool(row)

    async def hget(self, name: str, key: str):
        await self._purge_expired(name)
        row = await InstantKV.filter(prefix=self.key_prefix, name=name, field=key).first()
        return row.value if row else None

    async def hgetall(self, name: str):
        await self._purge_expired(name)
        rows = await InstantKV.filter(prefix=self.key_prefix, name=name).exclude(field="").all()
        result: Dict[str, str] = {}
        for r in rows:
            # If any row has expired_at set but we didn't purge yet, skip it
            if r.expire_at and r.expire_at <= _now_utc():
                continue
            result[r.field] = r.value
        return result

    async def hlen(self, name: str):
        await self._purge_expired(name)
        count = await InstantKV.filter(prefix=self.key_prefix, name=name).exclude(field="").count()
        return count

    async def hset(self, name: str, key: Optional[str] = None, value: Optional[str] = None, mapping: Optional[Dict[str, str]] = None, items: Optional[Iterable[Tuple[str, str]]] = None):
        await self._purge_expired(name)
        added = 0
        now_items: List[Tuple[str, str]] = []
        if mapping:
            now_items.extend(list(mapping.items()))
        if items:
            now_items.extend(list(items))
        if key is not None:
            now_items.append((key, value if value is not None else ""))

        # Determine TTL from any existing row under this key
        any_row = await InstantKV.filter(prefix=self.key_prefix, name=name).first()
        ttl = any_row.expire_at if any_row else None

        # Upsert each field
        for k, v in now_items:
            row = await InstantKV.filter(prefix=self.key_prefix, name=name, field=k).first()
            if row:
                row.value = str(v)
                await row.save(update_fields=["value"])
            else:
                await InstantKV.create(
                    prefix=self.key_prefix,
                    name=name,
                    field=k,
                    value=str(v),
                    expire_at=ttl,
                )
                added += 1
        return added

    async def hmget(self, name: str, keys: Iterable[str], *args):
        await self._purge_expired(name)
        key_list: List[str] = list(keys) + list(args)
        values: List[Optional[str]] = []
        for k in key_list:
            row = await InstantKV.filter(prefix=self.key_prefix, name=name, field=k).first()
            values.append(row.value if row else None)
        return values

    async def hmset(self, name: str, mapping: Dict[str, str]):
        await self.hset(name, mapping=mapping)
        return True


class UserInstantDataStorageDBService(InstantDataStorageDBService):
    def __init__(self, user_id: str, name: str):
        self.key_prefix = f"u:{user_id[2:]}:{name}"

    @classmethod
    async def load(cls, user_id: str, name: str) -> "UserInstantDataStorageDBService":
        return cls(user_id, name)


# ---------------------------------
# One-row-per-key JSON-packed model
# ---------------------------------

class InstantKVPack(MetaverModel):
    class Meta:
        table = "instant_kv_pack"
        primary_key = ("prefix", "name")
        db_name = DB_NAME

    prefix = models.CharField(max_length=128)
    name = models.CharField(max_length=256)
    data = models.JSONField()
    expire_at = models.DatetimeField(null=True)


class InstantDataStorageDBJsonService:
    def __init__(self, app_id: str, name: str):
        self.key_prefix = f"a:{app_id[2:]}:{name}"

    @classmethod
    async def load(cls, app_id: str, name: str) -> "InstantDataStorageDBJsonService":
        return cls(app_id, name)

    async def _purge_expired(self, name: str) -> None:
        now = _now_utc()
        await InstantKVPack.filter(prefix=self.key_prefix, name=name, expire_at__lte=now).delete()

    async def _get_pack(self, name: str) -> Optional[InstantKVPack]:
        pack = await InstantKVPack.filter(prefix=self.key_prefix, name=name).first()
        if not pack:
            return None
        if pack.expire_at and pack.expire_at <= _now_utc():
            await InstantKVPack.filter(prefix=self.key_prefix, name=name).delete()
            return None
        return pack

    async def _ensure_pack(self, name: str) -> InstantKVPack:
        pack = await self._get_pack(name)
        if pack:
            return pack
        return await InstantKVPack.create(prefix=self.key_prefix, name=name, data={}, expire_at=None)

    # ----- key TTL -----
    async def expire(self, name: str, time: int, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return False
        # Simplified for nx/xx/gt/lt: same as Redis default path we use
        pack.expire_at = _now_utc() + timedelta(seconds=int(time))
        await pack.save(update_fields=["expire_at"])
        return True

    async def expireat(self, name: str, when, nx: bool = False, xx: bool = False, gt: bool = False, lt: bool = False):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return False
        if isinstance(when, (int, float)):
            expire_at = datetime.utcfromtimestamp(int(when))
        elif isinstance(when, datetime):
            expire_at = when
        else:
            expire_at = _now_utc()
        pack.expire_at = expire_at
        await pack.save(update_fields=["expire_at"])
        return True

    # ----- simple string value -----
    async def get(self, name: str):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return None
        return pack.data.get("_")

    async def set(
        self,
        name: str,
        value,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
        get: bool = False,
        exat: Optional[int] = None,
        pxat: Optional[int] = None,
    ):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        existed = bool(pack and ("_" in (pack.data or {})))
        oldval = pack.data.get("_") if (pack and get and existed) else None

        if nx and existed:
            return oldval if get else False
        if xx and not existed:
            return None if get else False

        if not pack:
            pack = await self._ensure_pack(name)

        # TTL
        new_expire_at: Optional[datetime] = pack.expire_at if keepttl else None
        if ex is not None:
            new_expire_at = _now_utc() + timedelta(seconds=int(ex))
        elif exat is not None:
            new_expire_at = datetime.utcfromtimestamp(int(exat))
        elif px is not None:
            new_expire_at = _now_utc() + timedelta(milliseconds=int(px))
        elif pxat is not None:
            new_expire_at = datetime.utcfromtimestamp(int(pxat) / 1000)

        data = dict(pack.data or {})
        data["_"] = str(value)
        pack.data = data
        pack.expire_at = new_expire_at
        await pack.save(update_fields=["data", "expire_at"])
        return oldval if get else True

    async def setex(self, name: str, time: int, value):
        pack = await self._ensure_pack(name)
        data = dict(pack.data or {})
        data["_"] = str(value)
        pack.data = data
        pack.expire_at = _now_utc() + timedelta(seconds=int(time))
        await pack.save(update_fields=["data", "expire_at"])
        return True

    async def setnx(self, name: str, value):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if pack and "_" in (pack.data or {}):
            return False
        pack = pack or await self._ensure_pack(name)
        data = dict(pack.data or {})
        data["_"] = str(value)
        pack.data = data
        await pack.save(update_fields=["data"])
        return True

    # ----- hash operations -----
    async def hexists(self, name: str, key: str):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return False
        return key in (pack.data or {}) and key != "_"

    async def hget(self, name: str, key: str):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return None
        if key == "_":
            return None
        val = (pack.data or {}).get(key)
        return None if val is None else str(val)

    async def hgetall(self, name: str):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return {}
        result: Dict[str, str] = {}
        for k, v in (pack.data or {}).items():
            if k == "_":
                continue
            result[k] = str(v)
        return result

    async def hlen(self, name: str):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        if not pack:
            return 0
        return len([k for k in (pack.data or {}).keys() if k != "_"])

    async def hset(self, name: str, key: Optional[str] = None, value: Optional[str] = None, mapping: Optional[Dict[str, str]] = None, items: Optional[Iterable[Tuple[str, str]]] = None):
        await self._purge_expired(name)
        pack = await self._ensure_pack(name)
        data = dict(pack.data or {})
        before_keys = set([k for k in data.keys() if k != "_"])

        now_items: List[Tuple[str, str]] = []
        if mapping:
            now_items.extend(list(mapping.items()))
        if items:
            now_items.extend(list(items))
        if key is not None:
            now_items.append((key, value if value is not None else ""))

        for k, v in now_items:
            if k == "_":
                continue
            data[k] = str(v)

        pack.data = data
        await pack.save(update_fields=["data"])

        after_keys = set([k for k in data.keys() if k != "_"])
        added = len(after_keys - before_keys)
        return added

    async def hmget(self, name: str, keys: Iterable[str], *args):
        await self._purge_expired(name)
        pack = await self._get_pack(name)
        key_list: List[str] = list(keys) + list(args)
        if not pack:
            return [None for _ in key_list]
        data = pack.data or {}
        return [str(data[k]) if (k in data and k != "_") else None for k in key_list]

    async def hmset(self, name: str, mapping: Dict[str, str]):
        await self.hset(name, mapping=mapping)
        return True


class UserInstantDataStorageDBJsonService(InstantDataStorageDBJsonService):
    def __init__(self, user_id: str, name: str):
        self.key_prefix = f"u:{user_id[2:]}:{name}"

    @classmethod
    async def load(cls, user_id: str, name: str) -> "UserInstantDataStorageDBJsonService":
        return cls(user_id, name)


InstantDataStorageService = InstantDataStorageDBJsonService
UserInstantDataStorageService = UserInstantDataStorageDBJsonService