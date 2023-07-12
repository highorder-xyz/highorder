
from highorder.base.model import MetaverModel
from postmodel import models
from highorder.base.utils import random_id, time_random_id

class QuestVariable(MetaverModel):
    class Meta:
        table = 'quest_variable'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    variable = models.JSONField()


class QuestPageState(MetaverModel):
    class Meta:
        table = 'quest_page_state'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    page_state = models.JSONField()

class QuestPlayableState(MetaverModel):
    class Meta:
        table = 'quest_playable_state'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    playable_state = models.JSONField()

class QuestPlayer(MetaverModel):
    class Meta:
        table = 'quest_player'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    attribute = models.JSONField()
    currency = models.JSONField()

class QuestPlayerItembox(MetaverModel):
    class Meta:
        table = 'quest_player_itembox'
        primary_key = ('app_id', 'user_id', 'name')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    attrs = models.JSONField()
    detail = models.JSONField()


class QuestPlayerTask(MetaverModel):
    class Meta:
        table = 'quest_player_task'
        primary_key = ('app_id', 'user_id')

    app_id = models.CharField(max_length=128)
    user_id = models.CharField(max_length=256)
    task = models.JSONField()


class QuestArena(MetaverModel):
    class Meta:
        table = 'quest_arena'
        primary_key = ('app_id', 'arena_id')

    app_id = models.CharField(max_length=128)
    arena_id = models.CharField(max_length=256)
    attrs = models.JSONField()
    itemboxes = models.JSONField()