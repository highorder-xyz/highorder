from highorder.base.model import MetaverModel
from postmodel import models
from highorder.base.utils import random_id, time_random_id, IDPrefix
from functools import partial

import json
from datetime import datetime


class User(MetaverModel):
    class Meta:
        table = "user"
        primary_key = ("app_id", "user_id")
        unique_together = (("app_id", "user_name"),)
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(
        max_length=256, default=partial(time_random_id, IDPrefix.USER, 10)
    )
    user_name = models.CharField(max_length=256)
    deactive = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    sessions = models.JSONField()


class UserAuth(MetaverModel):
    class Meta:
        table = "user_auth"
        primary_key = ("app_id", "email")
        indexes = (("app_id", "user_id"),)
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    salt = models.CharField(max_length=32)
    password_hash = models.CharField(max_length=2048, null=True)
    email = models.CharField(max_length=128)


class SocialAccount(MetaverModel):
    class Meta:
        table = "social_account"
        primary_key = ("app_id", "social_id")
        indexes = (("app_id", "user_id"),)
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    social_id = models.CharField(max_length=512)
    user_id = models.CharField(max_length=256)
    platform = models.CharField(max_length=64)
    platform_app = models.CharField(max_length=256)
    open_id = models.CharField(max_length=256)
    union_id = models.CharField(max_length=256)
    auth_info = models.JSONField()
    link_status = models.BooleanField(default=False)


class Session(MetaverModel):
    class Meta:
        table = "session"
        primary_key = ("app_id", "session_token")
        db_name = "highorder"

    session_token = models.CharField(
        max_length=256, default=partial(time_random_id, IDPrefix.SESSION, 20)
    )
    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256, null=True)
    expire_time = models.DatetimeField(null=True)
    session_type = models.CharField(max_length=32)
    session_data = models.JSONField()
    device_info = models.JSONField()
    country_code = models.CharField(max_length=32, null=True)
    ip = models.CharField(max_length=128, null=True)
    is_valid = models.BooleanField(null=True, default=True)


class HolaObject(MetaverModel):
    class Meta:
        table = "hola_object"
        primary_key = ("app_id", "object_id")
        indexes = (("app_id", "object_name"),)
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    object_name = models.CharField(max_length=512)
    object_id = models.CharField(max_length=512)
    value = models.JSONField()


class HolaVariable(MetaverModel):
    class Meta:
        table = "hola_variable"
        primary_key = ("app_id", "user_id")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    variable = models.JSONField()


class HolaSessionVariable(MetaverModel):
    class Meta:
        table = "hola_session_variable"
        primary_key = ("app_id", "session_token")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    session_token = models.CharField(max_length=256)
    variable = models.JSONField()


class HolaPageState(MetaverModel):
    class Meta:
        table = "hola_page_state"
        primary_key = ("app_id", "user_id")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    page_state = models.JSONField()


class HolaSessionPageState(MetaverModel):
    class Meta:
        table = "hola_session_page_state"
        primary_key = ("app_id", "session_token")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    session_token = models.CharField(max_length=256)
    page_state = models.JSONField()


class HolaPlayableState(MetaverModel):
    class Meta:
        table = "hola_playable_state"
        primary_key = ("app_id", "user_id")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    playable_state = models.JSONField()


class HolaSessionPlayableState(MetaverModel):
    class Meta:
        table = "hola_session_playable_state"
        primary_key = ("app_id", "session_token")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    session_token = models.CharField(max_length=256)
    playable_state = models.JSONField()


class HolaPlayer(MetaverModel):
    class Meta:
        table = "hola_player"
        primary_key = ("app_id", "user_id")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    state = models.JSONField()
    profile = models.JSONField()
    attribute = models.JSONField()
    currency = models.JSONField()


class HolaThing(MetaverModel):
    class Meta:
        table = "hola_thing"
        primary_key = ("app_id", "thing_id")
        indexes = (("app_id", "device_id"),)
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    thing_id = models.CharField(max_length=256, default=partial(time_random_id, IDPrefix.THING, 20))
    device_id = models.CharField(max_length=256)
    device_type = models.CharField(max_length=128)
    device_info = models.JSONField()
    bind_to = models.JSONField()
    home_url = models.CharField(max_length=1024, null=True)
    related = models.JSONField()

class HolaSessionPlayer(MetaverModel):
    class Meta:
        table = "hola_session_player"
        primary_key = ("app_id", "session_token")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    session_token = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    state = models.JSONField()
    profile = models.JSONField()
    attribute = models.JSONField()
    currency = models.JSONField()


class HolaPlayerItembox(MetaverModel):
    class Meta:
        table = "hola_player_itembox"
        primary_key = ("app_id", "user_id", "name")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    attrs = models.JSONField()
    detail = models.JSONField()


class HolaSessionPlayerItembox(MetaverModel):
    class Meta:
        table = "hola_session_player_itembox"
        primary_key = ("app_id", "session_token", "name")
        db_name = "highorder"

    app_id = models.CharField(max_length=128)
    session_token = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    attrs = models.JSONField()
    detail = models.JSONField()
