
from highorder.base.model import MetaverModel
from postmodel import models
from highorder.base.utils import random_id, time_random_id

class HolaObject(MetaverModel):
    class Meta:
        table = 'hola_object'
        primary_key = ('app_id', 'object_id')
        indexes = (("app_id", "object_name"), )

    app_id = models.CharField(max_length=128)
    object_name = models.CharField(max_length=512)
    object_id = models.CharField(max_length=512)
    value = models.JSONField()


class HolaVariable(MetaverModel):
    class Meta:
        table = 'hola_variable'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    variable = models.JSONField()


class HolaPageState(MetaverModel):
    class Meta:
        table = 'hola_page_state'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    page_state = models.JSONField()

class HolaPlayableState(MetaverModel):
    class Meta:
        table = 'hola_playable_state'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    playable_state = models.JSONField()

class HolaPlayer(MetaverModel):
    class Meta:
        table = 'hola_player'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    attribute = models.JSONField()
    currency = models.JSONField()

class HolaPlayerItembox(MetaverModel):
    class Meta:
        table = 'hola_player_itembox'
        primary_key = ('app_id', 'user_id', 'name')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    attrs = models.JSONField()
    detail = models.JSONField()


class HolaPlayerTask(MetaverModel):
    class Meta:
        table = 'hola_player_task'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    task = models.JSONField()
