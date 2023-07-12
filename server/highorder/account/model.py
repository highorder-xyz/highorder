
from email.policy import default
from highorder.base.model import MetaverModel
from postmodel import models
from highorder.base.utils import random_id, time_random_id
from functools import partial

import json
from datetime import datetime

class User(MetaverModel):
    class Meta:
        table = 'user'
        primary_key = ('app_id', 'user_id')
        unique_together = (('app_id', 'user_name'),)

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256, default=partial(time_random_id, 'UU', 10))
    user_name = models.CharField(max_length=256)
    deactive = models.BooleanField(default=False)
    is_frozen = models.BooleanField(default=False)
    sessions = models.JSONField()


class UserProfile(MetaverModel):
    class Meta:
        table = 'profile'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256, default=partial(time_random_id, 'UU', 10))
    nick_name = models.CharField(max_length=256)
    avatar_url = models.CharField(max_length=2048)
    extra = models.JSONField()

class UserAuth(MetaverModel):
    class Meta:
        table = 'user_auth'
        primary_key = ('app_id', 'email')
        indexes = (("app_id", "user_id"), )

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    salt = models.CharField(max_length=32)
    password_hash = models.TextField(null=True)
    email = models.CharField(max_length=128)


class UserAuthAnonymous(MetaverModel):
    class Meta:
        table = 'user_auth_anonymous'
        primary_key = ('app_id', 'local_uid')
        indexes = (("app_id", "custom_uid"), )

    app_id = models.CharField(max_length=128)
    local_uid = models.CharField(max_length=256)
    custom_uid = models.CharField(max_length=256)
    user_id = models.CharField(max_length=256)

class Phone(MetaverModel):
    class Meta:
        table = 'user_phone'
        primary_key = ('app_id', 'phone_number')
        indexes =(("app_id", "user_id"), )

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=32)
    link_status = models.BooleanField(default=False)



class SocialAccount(MetaverModel):
    class Meta:
        table = 'social_account'
        primary_key = ('app_id', 'social_id')
        indexes = (('app_id', 'user_id'),)

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
        table = 'session'
        primary_key = ('app_id', 'session_token')
        indexes = (('app_id', 'user_id'))

    session_token = models.CharField(max_length=256, default=partial(time_random_id, 'US', 20))
    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    expire_time = models.DatetimeField(null=True)
    session_type = models.CharField(max_length=32)
    session_data = models.JSONField()
    device_info = models.JSONField()
    country_code = models.CharField(max_length=32,null=True)
    ip = models.CharField(max_length=128, null=True)
    is_valid = models.BooleanField(null=True, default=True)

class UserTags(MetaverModel):
    class Meta:
        table = 'user_tags'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    tags = models.JSONField()