from dataclasses import dataclass, field
import inspect
import operator
from .account import (
    AccountService,
    SessionService,
    SocialAccountService,
    UserAuthService,
    UserService,
)
from highorder.base.compiler import Compiler
from highorder.base.utils import (
    AutoList,
    time_random_id,
    IDPrefix,
    StampToken,
    random_str,
)
from highorder.base.munch import munchify, Munch
from highorder.base.router import Router
from highorder.base.model import DB_NAME
import os
import copy
import random
from datetime import date, timedelta, datetime
from typing import List, Any, Mapping, Sequence
from .data import (
    ClientRequestContext,
    InitAdCommand,
    LimitObject,
    PageDefine,
    PlayableApplyCommand,
    PlayableApplyCommandArg,
    PlayableCompletedArg,
    PlayableConfig,
    HolaInterfaceDefine,
    PageInterface,
    SetSessionCommand,
    SetSessionCommandArg,
    ShowAdCommand,
    ShowAdCommandArg,
    ShowAlertCommand,
    ShowAlertCommandArg,
    ShowModalCommand,
    ShowModalCommandArg,
    ShowMotionCommand,
    ShowMotionCommandArg,
    ShowPageCommand,
    ShowPageCommandArg,
    UpdatePageCommand,
    UpdatePageCommandArg,
    UpdatePageInterface,
    CloseModalCommand,
    CloseModalCommandArg,
)
from .model import (
    HolaPageState,
    HolaPlayableState,
    HolaPlayer,
    HolaPlayerItembox,
    HolaVariable,
    HolaSessionPageState,
    HolaSessionPlayableState,
    HolaSessionPlayer,
    HolaSessionPlayerItembox,
    HolaSessionVariable,
    HolaObject,
    HolaResource,
    HolaThing,
)
from .builtin import (HolaBulitin, EXPR_BUILTINS)
from postmodel.models import QueryExpression
from postmodel.transaction import in_transaction
from .transformer import (
    FilterExprTransformer,
    expr_dump,
    DatetimeFormatter
)
import json

import dataclass_factory
from likepy import restrictedexpr, restrictedpy
from highorder.base.instant import (
    InstantDataStorageService,
    UserInstantDataStorageService,
)
from highorder.base.loader import ApplicationFolder
from basepy.asynclog import logger
import zlib
from .extension import HolaServiceRegister
from functools import reduce
from string import Formatter

factory = dataclass_factory.Factory()

def get_page_size_name(page_width):
    if page_width <= 300:
        return "xmall"
    elif page_width <= 480:
        return "small"
    elif page_width <= 768:
        return "medium"
    elif page_width <= 1200:
        return "large"
    elif page_width <= 1680:
        return "xlarge"
    elif page_width > 1680:
        return "xxlarge"


def with_context(context, **kwargs):
    origin_context = context
    context = copy.copy(origin_context)
    for k, v in kwargs.items():
        context[k] = munchify(v)
    return context


class ValueNotEnoughError(Exception):
    def __init__(self, name):
        self.name = name


class AttributeValueNotEnoughError(ValueNotEnoughError):
    def __init__(self, name):
        self.name = name


class CurrencyValueNotEnoughError(ValueNotEnoughError):
    def __init__(self, name):
        self.name = name


builtin = HolaBulitin()


class DataTypeParser:
    @classmethod
    def parse(self, type_obj):
        if type_obj in ['bool', 'number', 'string', 'object']:
            return type_obj
        elif type_obj in ['color', 'datetime']:
            return 'string'
        elif isinstance(type_obj, dict):
            return type_obj.get('type')
        elif isinstance(type_obj, str):
            index = type_obj.find('[')
            if index > 0:
                return type_obj[:index]
            else:
                return type_obj
        else:
            return 'unknown'

class ShowMessageService:
    @classmethod
    def show(cls, message: str, route_back: bool = False):
        confirm = {"text": "confirm", "action": ""}
        if route_back:
            confirm["action"] = "route.back"
        return ShowModalCommand(
            args=ShowModalCommandArg(
                elements=[{"type": "paragraph", "text": message, "align": "center"}],
                confirm=confirm,
            )
        )



class HolaThingService:
    @classmethod
    async def create(cls, app_id, config_def, device_info):
        info = copy.copy(device_info or {})
        device_id = info.pop('device_id')
        device_type = info.pop('device_type')
        device_info = info
        thing = await HolaThing.get_or_none(app_id = app_id, device_id = device_id)
        if not thing:
            thing = await HolaThing.create(
                app_id = app_id,
                device_id = device_id,
                device_type = device_type,
                device_info = info,
                home_url = "",
                bind_to = {},
                related = {}
            )

        return cls(app_id, config_def, thing)

    @classmethod
    async def load(cls, app_id, thing_id):
        thing = await HolaThing.load(app_id = app_id, thing_id = thing_id)
        return cls(app_id, [], thing)

    def __init__(self, app_id, config_def, thing):
        self.app_id = app_id
        self.config_def = config_def
        self.thing = thing

    def get_home_url(self):
        home_url = self.thing.home_url
        if home_url:
            return home_url

        for _conf in self.config_def:
            for config in _conf.get('elements', []):
                if config.get('type') != 'thing-route-config':
                    continue
                if config.get('device_type') == self.thing.device_type:
                    home_url = config.get('home_url')
                    if home_url:
                        break
        return home_url

    @property
    def bind_to(self):
        return self.thing.bind_to

    async def get_bind_to_obj(self):
        bind_to = self.thing.bind_to
        if not bind_to: return None
        _id = bind_to.get('object_id') or bind_to.get('_id')
        _name = bind_to.get('object_name') or bind_to.get('_name')
        if not _id or not _name or _name == 'thing':
            return None
        bind_to_obj = await self.load_obj(_name, _id)
        if bind_to_obj:
            return bind_to_obj

    async def load_obj(self, obj_name, obj_id):
        if obj_name == 'player':
            m = await HolaPlayer.load(app_id = self.app_id, user_id=obj_id)
            if m:
                obj = HolaDataObject(
                    self.app_id, obj_name, obj_id, m.to_dict()
                )
                return obj
        elif obj_name == 'thing':
            return None
        else:
            m = await HolaObject.load(
                app_id=self.app_id, object_name = obj_name, object_id = obj_id
            )
            if m:
                obj = HolaDataObject(
                    self.app_id,
                    obj_name,
                    m.object_id,
                    copy.copy(m.value),
                    created = m.created.isoformat(),
                    updated = m.updated.isoformat(),
                    data_ver = m.data_ver
                )
                return obj

    async def update(self, **kwargs):
        if 'bind_to' in kwargs:
            self.thing.bind_to = kwargs['bind_to']

        if 'home_url' in kwargs:
            self.thing.home_url = kwargs['home_url']

        if 'related' in kwargs:
            self.thing.related = kwargs['related']

        await self.thing.save()


class HolaDialogService:
    @classmethod
    def build_confirm_dialog(
        cls, message: str, handler: dict, confirm=None, cancel=None
    ):
        st = StampToken()
        args = ShowModalCommandArg(
            title="CONFIRM DIALOG",
            content=message,
            confirm={
                "text": confirm or "Confirm",
                "click": st.make("stamp_id", handler),
            },
            cancel={"text": cancel or "Cancel"},
        )
        return ShowModalCommand(args=args)


class HolaPageStateService:
    def __init__(self, unique_id, page_state, storage_svc):
        self.unique_id = unique_id
        self.page_state = page_state
        self.storage_svc = storage_svc

    def get_instant_store(self, limit):
        limit_key = limit.get_instant_key()
        instant_name = short_hash(f"pagestate:{limit_key}")
        instant_storage = UserInstantDataStorageService(self.unique_id, "d")
        return (instant_storage, instant_name)

    async def get_instant_view_viewed(self, route, tag, limit):
        store, name = self.get_instant_store(limit)
        value = await store.hget(name, f"{route}:{tag}:viewed")
        if not value:
            return False
        try:
            if int(value) > 0:
                return True
            else:
                return False
        except:
            await logger.warning(
                f"instant contain wrong type data: {value}, expect int."
            )
            return False

    async def set_instant_view_viewed(self, route, tag, limit):
        store, name = self.get_instant_store(limit)
        await store.hset(name, f"{route}:{tag}:viewed", 1)
        await store.expire(name, limit.get_expire())

    async def set_view_showed(self, route, tag="", limit=None):
        if limit:
            limitobj = factory.load(limit, LimitObject)
            return await self.set_instant_view_viewed(route, tag, limitobj)
        else:
            state = self.page_state.setdefault(route, {})
            state[f"{tag}viewed"] = True
            await self.storage_svc.save_page_state(self.page_state)

    async def get_view_showed(self, route, tag="", limit=None):
        if limit:
            limitobj = factory.load(limit, LimitObject)
            return await self.get_instant_view_viewed(route, tag, limitobj)
        else:
            state = self.page_state.get(route, {})
            return state.get(f"{tag}viewed", False)

    async def get_set_view_hooked(self, route, hook, tag, limit):
        limitobj = factory.load(limit, LimitObject)
        viewed = await self.get_instant_view_viewed(route, f"{hook}_{tag}", limitobj)
        await self.set_instant_view_viewed(route, f"{hook}_{tag}", limitobj)
        return viewed


def short_hash(value):
    if type(value) in (str,):
        return hex(zlib.adler32(value.encode("utf-8")))[2:]
    else:
        return hex(zlib.adler32(value))[2:]


class ChallengeService:
    @classmethod
    def create(cls, hola_svc, name, challenges):
        filtered = filter(lambda x: x.name == name, challenges)
        if filtered:
            challenge_def = filtered[0]
            return cls(hola_svc, challenge_def)
        return None

    def __init__(self, hola_svc, challenge_def):
        self.hola_svc = hola_svc
        self.app_id = hola_svc.app_id
        self.user_id = hola_svc.user_id
        self.challenge_def = challenge_def
        self.name = challenge_def.name
        self.limit = challenge_def.limit
        limit_key = self.limit.get_instant_key()
        self.instant_name = short_hash(f"challenge:{challenge_def.name}:{limit_key}")
        self.instant_storage = UserInstantDataStorageService(self.user_id, "d")

    async def load(self):
        instant_data = await self.instant_storage.hgetall(self.instant_name)
        if not instant_data:
            instant_data = {
                "times": self.challenge_def.limit.value,
                "levelgot": 0,
                "succeed": 0,
            }
            await self.instant_storage.hmset(self.instant_name, instant_data)
            await self.instant_storage.expire(
                self.instant_name, self.limit.get_expire()
            )
        return instant_data

    async def info(self):
        instant_data = await self.load()
        return dict(
            times_left=int(instant_data["times"]),
            current_level=int(instant_data["levelgot"]) + 1,
            total_level=int(self.challenge_def.levels.count),
            succeed_levels=int(instant_data["succeed"]),
        )

    async def random_select(self, collection):
        if collection.type == "playable-collection":
            name = collection.name
            levels = await self.hola_svc.get_playable_levels(name)
            return random.choice(levels)

    async def get_playable(self):
        levels_config = self.challenge_def.levels
        if levels_config.select:
            method = levels_config.select.method
            collection = levels_config.select.collection
            if method == "random":
                playable = await self.random_select(collection)
                playable["collection"] = collection.name
                playable["challenge"] = self.name
                return playable
        return None

    async def playable_completed(self, args: PlayableCompletedArg):
        instant_data = await self.instant_storage.hgetall(self.instant_name)
        if args.succeed:
            instant_data["succeed"] = int(instant_data["succeed"]) + 1
        instant_data["levelgot"] = int(instant_data["levelgot"]) + 1
        await self.instant_storage.hmset(self.instant_name, instant_data)

    async def is_completed(self):
        instant_data = await self.instant_storage.hgetall(self.instant_name)
        if int(instant_data.get("levelgot", 0)) >= self.challenge_def.levels.count:
            instant_data = {
                "times": int(instant_data["times"]) - 1,
                "levelgot": 0,
                "succeed": 0,
            }
            await self.instant_storage.hmset(self.instant_name, instant_data)
            return True
        else:
            return False

    async def is_limited(self):
        instant_data = await self.instant_storage.hgetall(self.instant_name)
        if int(instant_data.get("times", 0)) <= 0:
            return True
        else:
            return False


class HolaStorageService:
    def __init__(self, session, hola_svc):
        self.session = session
        self.session_token = session.session_token
        self.app_id = session.app_id
        self.user_id = session.user_id
        self.hola_svc = hola_svc
        self._models = {}

    async def get_profile(self):
        player = await self.load_player()
        return player.profile

    def get_variable_value(self, vardef, context):
        if "value" in vardef:
            return self.hola_svc.eval_value(vardef["value"], context)
        elif "initial" in vardef:
            return vardef["initial"]
        else:
            raise Exception("Either variable initial or value muse be defined.")

    def init_variables(self, context):
        init = {}
        for vardef in self.hola_svc.variables_def:
            name = vardef["name"]
            init[name] = self.get_variable_value(vardef, context)
        return init

    async def load_variables_model(self, context=None):
        if "hola_variable" in self._models:
            return self._models["hola_variable"]
        var = await HolaVariable.load(app_id=self.app_id, user_id=self.user_id)
        if context == None:
            return var
        if not var:
            v = self.init_variables(context)
            var = await HolaVariable.create(
                app_id=self.app_id, user_id=self.user_id, variable=v
            )
        else:
            for vardef in self.hola_svc.variables_def:
                if vardef["name"] not in var.variable:
                    var.variable[vardef["name"]] = self.get_variable_value(
                        vardef, context
                    )
            await var.save()
        self._models["hola_variable"] = var
        return var

    async def load_session_variables_model(self, context=None):
        if "hola_session_variable" in self._models:
            return self._models["hola_session_variable"]
        var = await HolaSessionVariable.load(
            app_id=self.app_id, session_token=self.session_token
        )
        if context == None:
            return var
        if not var:
            v = self.init_variables(context)
            var = await HolaSessionVariable.create(
                app_id=self.app_id, session_token=self.session_token, variable=v
            )
        else:
            for vardef in self.hola_svc.variables_def:
                if vardef["name"] not in var.variable:
                    var.variable[vardef["name"]] = self.get_variable_value(
                        vardef, context
                    )
            await var.save()
        self._models["hola_session_variable"] = var
        return var

    async def load_variables(self, context):
        if not self.user_id:
            var = await self.load_session_variables_model(context)
            return munchify(var.to_dict())
        else:
            var = await self.load_variables_model(context)
            return munchify(var.to_dict())

    async def load_player_model(self):
        if "hola_player" in self._models:
            return self._models["hola_player"]
        player = await HolaPlayer.load(app_id=self.app_id, user_id=self.user_id)
        if not player:
            player = await HolaPlayer.create(
                app_id=self.app_id,
                user_id=self.user_id,
                name="",
                state={},
                profile={},
                attribute=self.hola_svc.get_attribute_initial(),
                currency=self.hola_svc.get_currency_initial(),
            )
        else:
            for attr_def in self.hola_svc.attribute_def:
                if attr_def["name"] not in player.attribute:
                    initial = attr_def.get("initial")
                    if initial != None:
                        player.attribute[attr_def["name"]] = initial
            await player.save()
        self._models["hola_player"] = player
        return player

    async def load_session_player_model(self):
        if "hola_session_player" in self._models:
            return self._models["hola_session_player"]
        player = await HolaSessionPlayer.load(
            app_id=self.app_id, session_token=self.session_token
        )
        if not player:
            player = await HolaSessionPlayer.create(
                app_id=self.app_id,
                session_token=self.session_token,
                name="",
                state={},
                profile={},
                attribute=self.hola_svc.get_attribute_initial(),
                currency=self.hola_svc.get_currency_initial(),
            )
        else:
            for attr_def in self.hola_svc.attribute_def:
                if attr_def["name"] not in player.attribute:
                    initial = attr_def.get("initial")
                    if initial != None:
                        player.attribute[attr_def["name"]] = initial
            await player.save()
        self._models["hola_session_player"] = player
        return player

    async def load_player(self):
        if not self.user_id:
            player = await self.load_session_player_model()
            return munchify(player.to_dict())
        else:
            player = await self.load_player_model()

        player = munchify(player.to_dict())
        player._id = player.user_id
        return player

    async def save_player(self, player):
        if not self.user_id:
            _model = await self.load_session_player_model()
        else:
            _model = await self.load_player_model()
        _model.name = player.name
        _model.profile = player.profile
        _model.state = player.state
        _model.attribute = player.attribute
        _model.currency = player.currency
        await _model.save()

    async def load_session_player_itembox_model(self, name="default"):
        if "hola_session_player_itembox" in self._models:
            return self._models["hola_session_player_itembox"]
        item = await HolaSessionPlayerItembox.load(
            app_id=self.app_id, session_token=self.session_token, name=name
        )
        if not item:
            item = await HolaSessionPlayerItembox.create(
                app_id=self.app_id,
                session_token=self.session_token,
                name=name,
                attrs={},
                detail={"items": self.hola_svc.get_item_initial()},
            )
        self._models["hola_session_player_itembox"] = item
        return item

    async def load_player_itembox_model(self, name="default"):
        if "hola_player_itembox" in self._models:
            return self._models["hola_player_itembox"]
        item = await HolaPlayerItembox.load(
            app_id=self.app_id, user_id=self.user_id, name=name
        )
        if not item:
            item = await HolaPlayerItembox.create(
                app_id=self.app_id,
                user_id=self.user_id,
                name=name,
                attrs={},
                detail={"items": self.hola_svc.get_item_initial()},
            )
        self._models["hola_player_itembox"] = item
        return item

    async def load_itembox(self, name="default"):
        if not self.user_id:
            itembox = await self.load_session_player_itembox_model(name)
            return munchify(itembox.to_dict())
        else:
            itembox = await self.load_itembox_model(name)
            return munchify(itembox.to_dict())

    async def save_itembox(self, itembox):
        if not self.user_id:
            _model = await self.load_session_player_itembox_model(itembox.name)
        else:
            _model = await self.load_player_itembox_model(itembox.name)
        _model.name = itembox.name
        _model.attrs = itembox.attrs
        _model.detail = itembox.detail
        await _model.save()

    async def load_session_playable_state_model(self):
        if "hola_session_playable_state" in self._models:
            return self._models["hola_session_playable_state"]
        state = await HolaSessionPlayableState.load(
            app_id=self.app_id, sesion_token=self.sesion_token
        )
        if not state:
            state = await HolaSessionPlayableState.create(
                app_id=self.app_id, sesion_token=self.sesion_token, playable_state={}
            )
        self._models["hola_session_playable_state"] = state
        return state

    async def load_playable_state_model(self):
        if "hola_playable_state" in self._models:
            return self._models["hola_playable_state"]
        state = await HolaPlayableState.load(app_id=self.app_id, user_id=self.user_id)
        if not state:
            state = await HolaPlayableState.create(
                app_id=self.app_id, user_id=self.user_id, playable_state={}
            )
        self._models["hola_playable_state"] = state
        return state

    async def load_playable_state(self):
        if not self.user_id:
            state = await self.load_session_playable_state_model()
        else:
            state = await self.load_playable_state_model()
        return munchify(state.to_dict())

    async def get_playable_state(self, collection, level_id):
        playable_state = await self.load_playable_state().playable_state
        collection_def = await self.hola_svc.get_playable_collection_define(collection)
        iter_type = collection_def.iter_type
        content = playable_state.get(collection, {})
        if iter_type == "sequence":
            content["level_id"] = level_id
            try:
                if int(content["level_id"]) >= level_id:
                    return {"succeed": True}
                else:
                    return {}
            except:
                return {}
        elif iter_type == "daily":
            if level_id not in content:
                return {}
            else:
                return {"succeed": content[level_id]}
        return {}

    async def set_playable_state(self, collection, level_id, succeed=True):
        playable_state = await self.load_playable_state().playable_state
        collection_def = await self.hola_svc.get_playable_collection_define(collection)
        iter_type = collection_def.iter_type
        if iter_type == "sequence":
            content = playable_state.setdefault(collection, {})
            if succeed:
                content["level_id"] = level_id
        elif iter_type == "daily":
            content = playable_state.setdefault(collection, {})
            if level_id not in content:
                content[level_id] = succeed
            else:
                if not content[level_id]:
                    content[level_id] = succeed
        if not self.user_id:
            _model = await self.load_session_playable_state_model()
        else:
            _model = await self.load_playable_state_model()
        _model.playable_state = playable_state
        await _model.save()

    async def load_session_page_state_model(self):
        if "hola_session_page_state" in self._models:
            return self._models["hola_session_page_state"]
        app_id, session_token = self.app_id, self.session_token
        page_state_model = await HolaSessionPageState.load(
            app_id=app_id, session_token=session_token
        )
        if page_state_model == None:
            page_state_model = await HolaSessionPageState.create(
                app_id=app_id, session_token=session_token, page_state={}
            )
        self._models["hola_session_page_state"] = page_state_model
        return page_state_model

    async def load_page_state_model(self):
        if "hola_page_state" in self._models:
            return self._models["hola_page_state"]
        app_id, user_id = self.app_id, self.user_id
        page_state_model = await HolaPageState.load(app_id=app_id, user_id=user_id)
        if page_state_model == None:
            page_state_model = await HolaPageState.create(
                app_id=app_id, user_id=user_id, page_state={}
            )
        self._models["hola_page_state"] = page_state_model
        return page_state_model

    async def load_page_state_service(self):
        if not self.user_id:
            page_state_model = await self.load_session_page_state_model()
        else:
            page_state_model = await self.load_page_state_model()
        return HolaPageStateService(self.user_id, page_state_model.page_state, self)

    async def save_page_state(self, page_state):
        if not self.user_id:
            _model = await self.load_session_page_state_model()
        else:
            _model = await self.load_page_state_model()
        _model.page_state = page_state
        await _model.save()


class HolaDataObject(Munch):
    def __init__(self, app_id, name, _id, data, **kwargs):
        args = {
            '_app_id': app_id,
            '_name': name,
            '_id': _id
        }
        args.update(data or {})
        args.update(kwargs)
        super().__init__(args)


class HolaDataObjectService:
    def __init__(self, app_id, name, hola_svc):
        self.app_id = app_id
        self.name = name
        self.hola_svc = hola_svc

    def new(self, *args, **kwargs):
        value = dict(*args, **kwargs)
        _id = time_random_id(IDPrefix.OBJECT, 30)
        return HolaDataObject(self.app_id, self.name, _id, value)

    async def create(self, *args, **kwargs):
        raw_value = dict(*args, **kwargs)
        if self.name == 'thing':
            raise Exception(f'thing can not be created.')
        if self.name == "player":
            return await self.create_player(**value)
        else:
            _id = time_random_id(IDPrefix.OBJECT, 30)
            value = {}
            obj_def = self.hola_svc.get_object_by_name(self.name)

            for el in obj_def.get("elements", []):
                k = el.get("name")
                if not k:
                    continue
                if k in raw_value:
                    value[k] = raw_value[k]
            m = await HolaObject.create(
                app_id=self.app_id, object_name=self.name, object_id=_id, value=value
            )
            return HolaDataObject(self.app_id, self.name, _id, value,
                    created = m.created.isoformat(),
                    updated = m.updated.isoformat(),
                    data_ver = m.data_ver)

    async def create_player(self, **kwargs):
        hola_init = HolaInitService(self.hola_svc)
        attribute_init = hola_init.get_attribute_initial()
        currency_init = hola_init.get_currency_initial()
        state_init = {}
        profile_init = {}
        r_args = kwargs
        state_init.update(r_args.get("state", {}))
        profile_init.update(r_args.get("profile", {}))
        attribute_init.update(r_args.get("attribute", {}))
        currency_init.update(r_args.get("currency", {}))

        if "name" in kwargs and "password" in kwargs:
            name, password = kwargs["name"], kwargs["password"]
            user_id = await UserAuthService.add_user(self.app_id, name, password)
            player = await HolaPlayer.create(
                app_id=self.app_id,
                user_id=user_id,
                name=name,
                state=state_init,
                profile=profile_init,
                attribute=attribute_init,
                currency=currency_init,
            )

            return HolaDataObject(
                self.app_id, self.name, user_id, player.to_dict()
            )
        else:
            raise Exception(f"can't create player withiout name and password.")

    def build_query_expr(self, filter_expr, **kwargs):
        order_by = kwargs.get("order_by")
        limit = kwargs.get("limit")
        ft = FilterExprTransformer(
            target = "it",
            rename = "value",
            expr_cls = QueryExpression, **kwargs
        )
        if filter_expr:
            qexpr = ft.transform(filter_expr)
            qexpr = operator.and_(
                QueryExpression(app_id=self.app_id, object_name=self.name), qexpr
            )
        else:
            qexpr = QueryExpression(app_id=self.app_id, object_name=self.name)

        query_expr = HolaObject.filter(qexpr)
        if order_by:
            query_expr = query_expr.order_by(*ft.transform_order_by(order_by))
        if limit:
            query_expr = query_expr.limit(limit)
        return query_expr

    def build_native_query_expr(self, model_class, filter_expr, **kwargs):
        order_by = kwargs.get("order_by")
        limit = kwargs.get("limit")
        ft = FilterExprTransformer(target="it", rename="", expr_cls = QueryExpression, **kwargs)
        if filter_expr:
            qexpr = ft.transform(filter_expr)
            qexpr = operator.and_(QueryExpression(app_id=self.app_id), qexpr)
        else:
            qexpr = QueryExpression(app_id=self.app_id)

        # print(expr_dump(qexpr))
        query_expr = model_class.filter(qexpr)
        if order_by:
            query_expr = query_expr.order_by(*ft.transform_order_by(order_by))
        if limit:
            query_expr = query_expr.limit(limit)
        return query_expr

    async def load(self, obj_name, obj_id):
        if obj_name == 'player':
            m = await HolaPlayer.load(app_id = self.app_id, user_id=obj_id)
            if m:
                obj = HolaDataObject(
                    self.app_id, obj_name, obj_id, m.to_jsondict()
                )
                return obj
        elif obj_name == 'thing':
            return None
        else:
            m = await HolaObject.load(
                app_id=self.app_id, object_name = obj_name, object_id = obj_id
            )
            if m:
                obj = HolaDataObject(
                    self.app_id,
                    obj_name,
                    m.object_id,
                    copy.copy(m.value),
                    created = m.created.isoformat(),
                    updated = m.updated.isoformat(),
                    data_ver = m.data_ver
                )
                return obj

    async def query(self, filter_expr, **kwargs):
        if self.name == "player":
            query_expr = self.build_native_query_expr(HolaPlayer, filter_expr, **kwargs)
            hobjects = list(await query_expr.all())
            objects = [
                HolaDataObject(
                    self.app_id, self.name, m.pk[1], m.to_jsondict()
                )
                for m in hobjects
            ]
            return objects
        elif self.name == "thing":
            query_expr = self.build_native_query_expr(HolaThing, filter_expr, **kwargs)
            hobjects = list(await query_expr.all())
            for obj in hobjects:
                bind_to = obj.bind_to
                if not bind_to: continue
                _id = bind_to.get('object_id') or bind_to.get('_id')
                _name = bind_to.get('object_name') or bind_to.get('_name')
                if not _id or not _name or _name == 'thing':
                    continue
                bind_to_obj = await self.load(_name, _id)
                if bind_to_obj:
                    obj.bind_to = bind_to_obj
            objects = [
                HolaDataObject(
                    self.app_id, self.name, m.pk[1], m.to_jsondict()
                )
                for m in hobjects
            ]
            return objects
        else:
            query_expr = self.build_query_expr(filter_expr, **kwargs)
            hobjects = list(await query_expr.all())
            objects = [
                HolaDataObject(
                    self.app_id,
                    self.name,
                    m.object_id,
                    copy.copy(m.value),
                    created = m.created.isoformat(),
                    updated = m.updated.isoformat(),
                    data_ver = m.data_ver
                )
                for m in hobjects
            ]
            return objects

    async def delete(self, *args, **kwargs):
        dargs = dict(*args, **kwargs)
        if self.name == "player":
            user_id = kwargs["user_id"]

            await HolaPlayer.filter(app_id=self.app_id, user_id=user_id).delete()
            await UserAuthService.delete_user(self.app_id, user_id)
        else:
            _id = kwargs["_id"]
            m = HolaObject.load(
                app_id=self.app_id, object_name=self.name, object_id=_id
            )
            if m:
                await m.delete()

    async def update(self, *args, **kwargs):
        up_args = dict(*args, **kwargs)
        if self.name == "player":
            user_id = up_args["user_id"]

            player = await HolaPlayer.load(app_id=self.app_id, user_id=user_id)

            new_password = up_args.get("password")
            if new_password:
                await UserAuthService.update_user(
                    app_id = self.app_id,
                    user_id = user_id,
                    password = new_password
                )

            for k in ["profile", "state", "attribute", "currency"]:
                if k in up_args and up_args[k]:
                    setattr(player, k, up_args[k])

            await player.save()
        elif self.name == "thing":
            thing_id = up_args.get('_id') or up_args.get('thing_id')
            thing_svc = await HolaThingService.load(app_id=self.app_id, thing_id=thing_id)
            await thing_svc.update(**up_args)
        else:
            _id = kwargs["_id"]
            m = await HolaObject.load(
                app_id=self.app_id, object_name=self.name, object_id=_id
            )

            obj_def = self.hola_svc.get_object_by_name(self.name)
            new_value = {}

            for el in obj_def.get("elements", []):
                k = el.get("name")
                if not k:
                    continue
                if k in kwargs:
                    new_value[k] = kwargs[k]
            if m and len(new_value) > 0:
                m.value.update(new_value)
                await m.save()

    async def delete_from(self, filter_expr, **kwargs):
        query_expr = self.builde_query_expr(filter_expr, **kwargs)
        await query_expr.all().delete()


class HolaResourceService:
    pass


class HolaSetupService:
    @classmethod
    async def create(cls, app_id, config_loader, **kwargs):
        inst = cls(app_id, config_loader)
        return inst

    def __init__(self, app_id, config_loader):
        self.app_id = app_id
        self.config_loader = config_loader
        self.currency_def = []
        self.attribute_def = []
        self.attributes = {}

    async def load(self):
        hola_dict = await self.config_loader.get_config("main.hola")
        hola_def = factory.load(hola_dict, HolaInterfaceDefine)
        for obj in hola_def.objects:
            obj_type = obj.get("type", "")
            if obj_type == "currency":
                self.currency_def.append(obj)
            elif obj_type == "attribute":
                self.attribute_def.append(obj)
                self.attributes[obj["name"]] = obj

    async def handle_request(self, request_cmd):
        args = request_cmd.args
        await self.load()
        if request_cmd.command == "app_setup":
            return await self.handle_app_setup(args)
        else:
            await logger.error(f"no handler for request command {request_cmd.command}")
        return None

    async def handle_app_setup(self, args):
        if "hola" in args:
            c = Compiler()
            hola_ast = c.compile(args["hola"])
        elif "hola.json" in args:
            hola_ast = args["hola.json"]
        else:
            raise Exception("app_setup parameter error.")
        info = AutoList()
        for setup in hola_ast["objects"]:
            info.add(await self.execute_setup(setup))
        return info

    async def execute_setup(self, setup):
        obj_type = setup["type"]
        if obj_type == "user-init":
            return await self.setup_user_init(setup)
        else:
            raise Exception(f"no setup executor for {obj_type}")

    async def setup_user_init(self, setup):
        auth = setup.get("auth")
        if not auth:
            return
        attributes = {}
        for key, value in setup.items():
            if key in self.attributes:
                attributes[key] = value

        app_id = self.app_id
        user_id = await UserAuthService.add_user(app_id, auth["name"], auth["password"])
        player = await HolaPlayer.load(app_id=app_id, user_id=user_id)
        if not player:
            player = await HolaPlayer.create(
                app_id=app_id,
                user_id=user_id,
                name=auth["name"],
                state={},
                profile={},
                attribute=self.get_attribute_initial(),
                currency=self.get_currency_initial(),
            )
        player.attribute.update(attributes)
        await player.save()

    def get_attribute_initial(self):
        attribute_initial = {}
        for attribute in self.attribute_def:
            initial = attribute.get("initial")
            if initial != None:
                attribute_initial[attribute["name"]] = initial
        return attribute_initial

    def get_currency_initial(self):
        currency_initial = {}
        for currency in self.currency_def:
            initial = currency.get("initial", 0)
            currency_initial[currency["name"]] = initial
        return currency_initial


class HolaInitService:
    def __init__(self, hola_svc):
        self.hola_svc = hola_svc

    def get_attribute_initial(self):
        attribute_initial = {}
        for attribute in self.hola_svc.attribute_def:
            initial = attribute.get("initial")
            if initial != None:
                attribute_initial[attribute["name"]] = initial
        return attribute_initial

    def get_currency_initial(self):
        currency_initial = {}
        for currency in self.hola_svc.currency_def:
            initial = currency.get("initial", 0)
            currency_initial[currency["name"]] = initial
        return currency_initial


class HolaService:
    @classmethod
    async def create(cls, app_id, session, config_loader, request_context, **kwargs):
        inst = cls(app_id, session, config_loader, **kwargs)
        await inst.load(request_context)
        return inst

    def __init__(self, app_id, session, config_loader, **kwargs):
        self.app_id = app_id
        self.user_id = session.user_id if session else None
        self.user = None
        self.session = session
        self.config_loader = config_loader
        self.router = Router()
        self.host_url = kwargs.get("host_url", "")
        self._commands = AutoList()

    async def load(self, request_context):
        hola_dict = await self.config_loader.get_config("main.hola")
        hola_def = factory.load(hola_dict, HolaInterfaceDefine)
        self.widgets = []
        self.components = []
        self.interfaces = []
        self.modals = []
        all_interfaces = hola_def.interfaces
        page_width = request_context.page_size.get("width", 0)
        psize_name = get_page_size_name(page_width)
        platform_name = request_context.platform

        for interface_def in all_interfaces:
            interface_type = interface_def.get("type", "")
            if interface_type == "page":
                page_def = factory.load(interface_def, PageDefine)
                valid_page_size = page_def.valid.get("page_size", None)
                valid_platform = page_def.valid.get("platform", None)
                if (not valid_page_size) and (not valid_platform):
                    self.router.add(page_def.route, page_def.route)
                    self.interfaces.append(page_def)
                elif (
                    isinstance(valid_page_size, (str,))
                    and valid_page_size == psize_name
                ) or (
                    isinstance(valid_page_size, (list, tuple))
                    and psize_name in valid_page_size
                ):
                    self.router.add(page_def.route, page_def.route)
                    self.interfaces.append(page_def)
                elif (
                    isinstance(valid_platform, (str,))
                    and valid_platform == platform_name
                ) or (
                    isinstance(valid_platform, (list, tuple))
                    and platform_name in valid_platform
                ):
                    self.router.add(page_def.route, page_def.route)
                    self.interfaces.append(page_def)
            elif interface_type == "component":
                self.components.append(interface_def)
            elif interface_type == "modal":
                self.modals.append(interface_def)

        self.variables_def = []
        self.objects_def = []
        self.config_def = []
        self.attribute_def = []
        self.item_def = []
        self.itembox_def = []
        self.currency_def = []
        for obj in hola_def.objects:
            obj_type = obj.get("type", "")
            if obj_type == "currency":
                self.currency_def.append(obj)
            elif obj_type == "item":
                self.item_def.append(obj)
            elif obj_type == "itembox":
                self.itembox_def.append(obj)
            elif obj_type == "attribute":
                self.attribute_def.append(obj)
            elif obj_type == "variable":
                self.variables_def.append(obj)
            elif obj_type == "object-meta":
                self.objects_def.append(obj)
            elif obj_type == 'config':
                self.config_def.append(obj)

        self.action_def = {}
        for action in hola_def.actions:
            if action.get("type") != "action":
                continue
            name = action["name"]
            if name in self.action_def:
                raise Exception(f"duplicated name {name} in action define.")
            self.action_def[name] = action

        self.ad_init_def = hola_def.advertisement.init
        self.ad_objects_def = hola_def.advertisement.show
        self.playable_collections_def = hola_def.playable.collections
        self.playable_challenges_def = hola_def.playable.challenges
        if self.session is None:
            self.session = await SessionService.create(app_id=self.app_id)
            self._commands.add(
                SetSessionCommand(
                    args=SetSessionCommandArg(
                        session=self.session.get_data_dict(), user=None
                    )
                )
            )
        if self.user_id:
            self.user = await UserService.load(self.app_id, self.user_id)
        self.storage_svc = HolaStorageService(self.session, self)

    def get_object_by_name(self, name):
        filtered = list(filter(lambda x: x["name"] == name, self.objects_def))
        if len(filtered) > 0:
            return filtered[0]
        return None

    def get_ad_object_by_name(self, name):
        filtered = list(filter(lambda x: x["name"] == name, self.ad_objects_def))
        if len(filtered) > 0:
            return filtered[0]
        return None

    async def load_objects(self, context):
        objects = {}
        for obj_def in self.objects_def:
            if "values" in obj_def:
                objects[obj_def["name"]] = obj_def["values"]
        return objects

    async def load_variables_to_context(self, context):
        var = await self.storage_svc.load_variables(context)
        context.variable = var.variable
        objects = await self.load_objects(context)
        context.objects = munchify(objects)

    def get_attribute_initial(self):
        attribute_initial = {}
        for attribute in self.attribute_def:
            initial = attribute.get("initial")
            if initial != None:
                attribute_initial[attribute["name"]] = initial
        return attribute_initial

    def get_currency_initial(self):
        currency_initial = {}
        for currency in self.currency_def:
            initial = currency.get("initial", 0)
            currency_initial[currency["name"]] = initial
        return currency_initial

    def get_currency_define(self, name=None):
        if not name:
            return self.currency_def[0]
        else:
            filtered = list(filter(lambda x: x["name"] == name, self.currency_def))
            if filtered:
                return filtered[0]
            else:
                raise Exception(f"no currency define with name {name}")

    def get_attribute_define(self, name):
        filtered = list(filter(lambda x: x["name"] == name, self.attribute_def))
        if filtered:
            return filtered[0]
        else:
            raise Exception(f"no attribute define with name {name}")

    async def load_player_to_context(self, context):
        player = await self.storage_svc.load_player()
        info = {}
        info.update(player.attribute)
        info.update({"currency": player.currency})
        info.update({"attribute": player.attribute})
        context.player = munchify(info)

    def get_item_initial(self):
        item_initial = []
        for item in self.item_def:
            initial = item.get("initial")
            if initial:
                item_initial.append(
                    {
                        "type": "item",
                        "name": item["name"],
                        "display_name": item["display_name"],
                        "count": initial,
                    }
                )
        return item_initial

    def get_itembox_define(self, name="default"):
        filtered = list(filter(lambda x: x["name"] == name, self.itembox_def))
        if filtered:
            return filtered[0]
        else:
            raise Exception(f"no itembox define with name {name}")

    async def get_player_item_info(self, item_name):
        items = (await self.storage_svc.load_itembox()).detail.get("items", [])
        filtered = list(filter(lambda x: x["name"] == item_name, items))
        have = len(filtered) > 0
        item = filtered[0] if have else {}
        return item

    async def get_itembox_items(self, name):
        itembox = await self.storage_svc.load_itembox(name=name)
        return itembox.detail.get("items", [])

    async def get_item_info(
        self,
        item_name,
    ):
        filtered = list(filter(lambda x: x["name"] == item_name, self.item_def))
        if filtered:
            item = filtered[0]
            ret = dict(
                type="item",
                name=item_name,
                display_name=item["display_name"],
                description=item.get("description"),
                icon=self.expand_link(item.get("icon")),
                effect_name=item.get("effect_name"),
                price=item.get("price"),
            )
            itembox = await self.storage_svc.load_itembox()
            count = 0
            for item in itembox.detail.get("items", []):
                if item["name"] == item_name:
                    count = item.get("count", 0)
                    break
            ret["count"] = count
            return ret
        else:
            raise Exception("no item<{item_name}> info found.")

    def get_page_def(self, route):
        page_route, route_args = self.router.match(route)
        page_def = self.get_page_def_by_route(page_route)
        return page_def, route_args

    def get_page_def_by_route(self, route):
        page_def = None
        for _interface in self.interfaces:
            if _interface.route == route:
                page_def = _interface
                break
        if page_def == None:
            raise Exception(f'no page routed to  "{route}" found.')
        return page_def

    def get_modal_def(self, name):
        modals = filter(lambda x: x["name"] == name, self.modals)
        modal = next(modals)
        return modal

    def expand_link(self, raw_link):
        if not raw_link:
            return raw_link
        if isinstance(raw_link, str):
            if raw_link == "~" or raw_link.startswith("~/"):
                relative = raw_link[1:].lstrip("/")
                content_root_url = ApplicationFolder.get_content_url_root(
                    self.app_id, self.host_url
                )
                return f"{content_root_url}/{relative}"
            else:
                return raw_link
        elif isinstance(raw_link, (dict, Mapping)):
            if "format" in raw_link:
                expr = raw_link["format"]
                return expr.format(
                    content=ApplicationFolder.get_content_url_root(
                        self.app_id, self.host_url
                    )
                )
            else:
                raise Exception("not allowed link format.")

    async def _create_context(self, page_context, page_locals):
        profile = await self.storage_svc.get_profile()
        user = self.user.get_data_dict() if self.user else {}
        user.update(profile)
        user["weixin"] = {"login": self.session.weixin_login}
        if self.user:
            user["authed"] = True
            user["name"] = self.user.user_name
            user["user_id"] = self.user.user_id
        else:
            user["authed"] = False

        ret = {
            "__builtins__": EXPR_BUILTINS,
            "home_url": "/",
            "user": user,
            "client": page_context or {},
            "locals": page_locals or {},
            "fn": builtin,
            "content": ApplicationFolder.get_content_url_root(
                self.app_id, self.host_url
            ),
        }
        ret.update(dict(playable={}, change={}))
        return munchify(ret)

    def _get_obj_from_context(self, parts, context):
        obj = context
        for part in parts:
            if obj:
                obj = getattr(obj, part, {})
        return obj

    async def get_item_define(self, item_name):
        filtered = list(filter(lambda x: x["name"] == item_name, self.item_def))
        if len(filtered) > 0:
            return filtered[0]
        else:
            raise Exception(f"item def of {item_name} not found.")

    async def transform_item_action(self, obj, context):
        origin_context = context
        item_name = obj["name"]
        item_def = await self.get_item_define(item_name)
        item = copy.copy(item_def)
        ret = dict(
            type="button",
            display_name=item_def["display_name"],
            description=item_def.get("description"),
            icon=self.expand_link(item_def.get("icon")),
            effect_name=item_def.get("effect_name"),
        )
        player_item_info = await self.get_player_item_info(item_name)
        if not player_item_info:
            ret["count"] = 0
        else:
            ret["count"] = player_item_info.get("count", 1)

        item["count"] = ret["count"]

        context = copy.copy(origin_context)
        context.item = munchify(item)
        if "open_modal" in obj:
            ret["open_modal"] = await self.transform_element(obj["open_modal"], context)

        if "open_modal_args" in obj:
            ret["open_modal_args"] = self.eval_object(obj["open_modal_args"], context)

        return ret

    async def transform_item_info_widget(self, obj, context):
        original_context = context
        context = copy.copy(original_context)
        widgets = []
        item_name = self.eval_value(obj["item_name"], context)
        item_def = await self.get_item_define(item_name)
        show = obj.get("show", {})
        widget = {
            "type": "icon-text",
            "text": item_def["display_name"]
            if show.get("display_name") == True
            else None,
            "icon": self.expand_link(item_def.get("icon"))
            if show.get("icon") == True
            else None,
            "style": {"text_weight": "bold"},
        }
        widgets.append(widget)

        if show.get("description", False) == True:
            widgets.append(
                {"type": "paragraph", "text": item_def.get("description", "")}
            )

        count_def = obj.get("count")
        if count_def:
            template = count_def.get("template")
            template_have = count_def.get("template_have")
            template_not = count_def.get("template_not")
            items = (await self.storage_svc.load_itembox()).detail.get("items", [])
            filtered = list(filter(lambda x: x["name"] == item_name, items))
            have = len(filtered) > 0
            item = filtered[0] if have else {}
            context.item = munchify(item)
            if "count" not in item:
                item["count"] = 1
            if template:
                widgets.append(
                    {"type": "paragraph", "text": self.eval_value(template, context)}
                )
            elif template_have and have:
                widgets.append(
                    {
                        "type": "paragraph",
                        "text": self.eval_value(template_have, context),
                    }
                )
            elif template_not:
                widgets.append(
                    {
                        "type": "paragraph",
                        "text": self.eval_value(template_not, context),
                    }
                )
        return {"type": "column", "elements": widgets}

    def get_item_widget_defines(self, item_name, widget_name):
        widget_defines = []
        for el in self.widgets:
            if (
                el["type"] == "item-widget"
                and el["name"] == widget_name
                and item_name in el["item"]
            ):
                widget_defines.append(el)
        return widget_defines

    def get_context_items(self, context):
        if "itemlist" in context:
            return context.itemlist
        elif "playable" in context and "itemlist" in context["playable"]:
            return context.playable.itemlist
        else:
            raise Exception("no items in context.")

    async def transform_item_widget(self, obj, context):
        widget_name = obj["widget_name"]

        origin_context = context
        context = copy.copy(origin_context)
        if "item" not in context:
            item_name = self.eval_value(obj["item_name"], context)
            item_filtered = list(
                filter(lambda x: x.name == item_name, self.get_context_items(context))
            )
            if len(item_filtered) == 0:
                await logger.warning(
                    f"no valid item named {item_name} found in context"
                )
                return {"type": "column", "elements": []}

            item = item_filtered[0]
            context.item = item

        item_name = context.item.name
        widget_defines = self.get_item_widget_defines(item_name, widget_name)
        if len(widget_defines) == 0:
            raise Exception(
                f"not item-widget for item: {item_name} and widget: {widget_name}"
            )

        widget_define = widget_defines[0]
        elements = AutoList()

        for el in widget_define["elements"]:
            elements.add(await self.transform_element(el, context))

        return {"type": "column", "elements": elements}

    async def transform_item_price(self, obj, context):
        widgets = []
        item_name = self.eval_value(obj["item_name"], context)
        currency_def = self.get_currency_define()
        item_def = await self.get_item_define(item_name)
        show = obj.get("show", {})
        widget = {"type": "icon-text"}
        if show.get("icon"):
            widget["icon"] = self.expand_link(currency_def.get("icon"))

        text = "{}".format(item_def.get("price", "unknown"))
        if show.get("display_name"):
            text = text + "  {}".format(currency_def["display_name"])
        widget["text"] = text

        widgets.append(widget)

        return widgets

    def get_change_list_defines(self, widget_name):
        widget_defines = []
        for el in self.widgets:
            if el["type"] == "change-list" and el["name"] == widget_name:
                widget_defines.append(el)
        return widget_defines

    def get_change_widget_define(self, change_type, widget_name):
        widget_defines = []
        for el in self.widgets:
            if el["type"] == "change-widget" and el["name"] == widget_name:
                if el["change_type"] == change_type:
                    widget_defines.append(el)
                elif (
                    isinstance(el["change_type"], (list, tuple))
                    and change_type in el["change_type"]
                ):
                    widget_defines.append(el)
        return widget_defines[0] if widget_defines else None

    async def transform_attribute_change_widget(self, change_widget_define, context):
        elements = AutoList()
        for el in change_widget_define["elements"]:
            elements.add(await self.transform_element(el, context))
        return elements

    async def transform_currency_change_widget(self, change_widget_define, context):
        elements = AutoList()
        for el in change_widget_define["elements"]:
            elements.add(await self.transform_element(el, context))
        return elements

    async def transform_item_change_widget(self, change_widget_define, context):
        elements = AutoList()
        for el in change_widget_define["elements"]:
            elements.add(await self.transform_element(el, context))
        return elements

    async def transform_change_list(self, obj, context):
        origin_context = context
        widget_name = obj["widget_name"]

        widget_defines = self.get_change_list_defines(widget_name)
        if len(widget_defines) == 0:
            raise Exception(f"not change-list with widget name: {widget_name}")

        widget_define = widget_defines[0]
        elements = AutoList()

        changes = context.changes
        if obj.get("changes"):
            changes = self.eval_value(obj["changes"], context)

        change_widget_names = widget_define["widget_names"]

        for change in changes:
            name = change["target_name"]
            target_type = change["target_type"]

            if target_type == "player.itembox":
                change_widget_name = change_widget_names.get(change["target"])
                if not change_widget_name:
                    continue
                change_widget_define = self.get_change_widget_define(
                    change["target"], change_widget_name
                )
            else:
                change_widget_name = change_widget_names.get(target_type, "default")
                change_widget_define = self.get_change_widget_define(
                    target_type, change_widget_name
                )

            if not change_widget_define:
                await logger.warning(
                    f"no schange_widget_define for {target_type}::{name}."
                )
                continue

            context = copy.copy(origin_context)
            context.change = change
            if target_type == "player.attribute":
                context2 = copy.copy(context)
                obj = copy.copy(self.get_attribute_define(name=name))
                obj.pop("type")
                context2.attribute = munchify(self.eval_object(obj, context2))
                elements.add(
                    await self.transform_attribute_change_widget(
                        change_widget_define, context2
                    )
                )

            elif target_type == "player.currency":
                context2 = copy.copy(context)
                obj = copy.copy(self.get_currency_define(name=name))
                obj.pop("type")
                context2.currency = munchify(self.eval_object(obj, context2))
                elements.add(
                    await self.transform_currency_change_widget(
                        change_widget_define, context2
                    )
                )

            elif target_type == "player.itembox":
                for changed_item in change.value:
                    item_name = changed_item.name
                    context2 = copy.copy(context)
                    item_info = copy.copy(await self.get_item_define(item_name))
                    item_info.pop("type", None)
                    item_info.pop("attributes", None)
                    item_info.update(changed_item)
                    context2.item = munchify(item_info)
                    elements.add(
                        await self.transform_item_change_widget(
                            change_widget_define, context2
                        )
                    )

        return elements

    async def transform_currency_text(self, obj, context):
        currency_name = obj["currency_name"]
        currency_def = self.get_currency_define(currency_name)
        player = await self.storage_svc.load_player()
        return {
            "type": "icon-number",
            "icon": self.expand_link(currency_def["icon"]),
            "number": player.currency.get(currency_name, 0),
            "animate": True,
        }

    async def transform_attribute_text(self, obj, context):
        attribute_name = obj["attribute_name"]
        attribute_def = self.get_attribute_define(attribute_name)
        player = await self.storage_svc.load_player()
        return {
            "type": "icon-number",
            "icon": self.expand_link(attribute_def["icon"]),
            "number": player.attribute.get(attribute_name, 0),
            "animate": True,
        }

    async def transform_qrcode(self, obj, context):
        return {
            "type": "qrcode",
            "code": self.eval_value(obj.get("code", ""), context),
            "text": self.eval_value(obj.get("text", ""), context),
        }

    async def query_playable_status_objects(self, query, context):
        objects = []
        collection = query["collection"]
        level_ids = []
        if "level_ids" in query:
            level_ids = self.eval_value(query["level_ids"], context)
        state = await self.storage_svc.load_playable_state()
        collection_state = state.playable_state.get(collection, {})

        for level_id in level_ids:
            level_status = "unknown"
            if level_id in collection_state:
                level_status = "succeed" if collection_state[level_id] else "failed"
            objects.append(
                {
                    "type": "playable",
                    "collection": collection,
                    "level_id": level_id,
                    "status": level_status,
                }
            )

        return objects

    async def query_objects(self, objdef, context):
        if "type" in objdef:
            obj_type = objdef["type"]
            if obj_type == "playable-state":
                return await self.query_playable_status_objects(
                    objdef["query"], context
                )
            elif obj_type == "item-info":
                return await self.get_item_info(objdef["item_name"])
            elif obj_type == "itembox-items":
                objects = await self.get_itembox_items(name=objdef["itembox_name"])
                if "order" in objdef and objdef["order"] == "desc":
                    objects = list(reversed(objects))
                return objects
            else:
                raise Exception(f"No query function for {obj_type}")
        elif "expr" in objdef:
            return self.eval_value(objdef, context)
        else:
            raise Exception(f"Not support objects define: {objdef}")

    async def transform_nav_menu(self, obj, context):
        elements = AutoList()
        if "elements" in obj:
            for el in obj["elements"]:
                elements.add(await self.transform_element(el, context))

        if "elements_dynamic" in obj:
            elements.add(
                await self.transform_elements_dynamic(obj["elements_dynamic"], context)
            )

        style = None
        if "style" in obj:
            style = self.eval_object(obj["style"], context)

        return {"type": "nav-menu", "style": style, "elements": elements}

    async def transform_nav_menu_item(self, obj, context):
        ret = {
            "type": "menu_item",
            "icon": self.expand_link(self.eval_value(obj.get("icon"), context)),
            "text": self.eval_value(obj.get("text", ""), context),
            "sub_text": self.eval_value(obj.get("sub_text", ""), context),
        }

        if "disable" in obj:
            ret["disable"] = self.eval_value(obj["disable"], context) or False

        if "disable_text" in obj:
            ret["disable_text"] = self.eval_value(obj["disable_text"], context)

        if "route" in obj:
            ret["route"] = self.eval_value(obj["route"], context)

        if "open_url" in obj:
            ret["open_url"] = obj["open_url"]

        if "open_modal" in obj:
            ret["open_modal"] = await self.transform_element(obj["open_modal"], context)

        if "open_modal_args" in obj:
            ret["open_modal_args"] = self.eval_object(obj["open_modal_args"], context)

        return ret

    async def transform_menu_item(self, element, context):
        transformed = {
            "type": "menu-item",
            "label": self.eval_value(element.get("label", ""), context),
            "name": self.eval_value(element.get("name", ""), context),
            "icon": self.eval_value(element.get("icon"), context),
        }

        if "events" in element:
            transformed["handlers"] = await self.transform_events(
                element["events"], context
            )

        return transformed

    async def transform_events(self, events, context):
        handlers = {}
        st = StampToken()
        for key, value in events.items():
            v = await self.transform_any(value, context)
            token = st.make("stamp_id", v)
            handlers[key] = token
        return handlers

    async def transform_modal(self, obj, context):
        ret = {
            "type": "modal",
            "name": self.eval_value(obj.get("name", ""), context),
            "title": self.eval_value(obj.get("title", ""), context),
        }

        if "title_action" in obj:
            title_action = obj["title_action"]
            ret["title_action"] = self.eval_object(title_action, context)
        if "elements" in obj:
            elements = AutoList()
            for el in obj.get("elements", []):
                elements.add(await self.transform_element(el, context))
            ret["elements"] = elements
        if "content" in obj:
            ret["content"] = self.eval_value(obj["content"], context)
        if "style" in obj:
            ret["style"] = self.eval_object(obj["style"], context)
        if "content_link" in obj:
            ret["content_link"] = self.expand_link(
                self.eval_value(obj["content_link"], context)
            )
        if "confirm" in obj:
            cond = obj["confirm"].get("condition")
            if not cond or (cond and self.eval_condition(cond, context)):
                ret["confirm"] = self.eval_object(
                    obj["confirm"], context, ignore_keys=["args", "click"]
                )
                ret["confirm"].pop("click", None)
        if "cancel" in obj:
            cond = obj["cancel"].get("condition")
            if not cond or (cond and self.eval_condition(cond, context)):
                ret["cancel"] = self.eval_object(
                    obj["cancel"], context, ignore_keys=["args", "click"]
                )
                ret["cancel"].pop("click", None)
        if "handlers" in obj:
            ret["handlers"] = [
                await self.transform_element(action, context)
                for action in obj["handlers"]
            ]
        return ret

    def get_object_type(self, obj):
        if "type" in obj:
            return obj["type"]
        else:
            return "object"

    async def transform_elements_dynamic(self, dynamic, context):
        origin_context = context
        elements = AutoList()
        objects_def = dynamic["objects"]
        template_def = dynamic["template"]
        objects = AutoList()

        if isinstance(objects_def, (dict, Mapping)):
            objects.add(await self.query_objects(objects_def, context))
        elif isinstance(objects_def, (list, Sequence)):
            for objdef in objects_def:
                objects.add(await self.query_objects(objdef, context))

        for obj in objects:
            context = copy.copy(origin_context)
            obj_type = self.get_object_type(obj)
            context[obj_type] = munchify(obj)
            if isinstance(template_def, (dict, Mapping)):
                elements.append(await self.transform_element(template_def, context))
            elif isinstance(template_def, (list, Sequence)):
                sub_elements = AutoList()
                for sub_template_def in template_def:
                    sub_elements.append(
                        await self.transform_element(sub_template_def, context)
                    )
                elements.append(sub_elements)

        return elements

    async def transform_data_table(self, element, context):
        transformed = {"type": "data-table", "data": [], "columns": AutoList()}

        data = element.get("data")
        if data:
            table_data = await self.transform_element(data, context)
            transformed["data"] = [x.to_dict() for x in table_data]

        transformed_data = transformed["data"]
        for index, v in enumerate(transformed_data):
            v["_index"] = index

        for el in element.get("elements", []):
            if el["type"] == "table-column":
                if "elements" in el and len(el["elements"]) > 0:
                    rand_name = random_str(6)
                    field_name = f"__col_{rand_name}"
                    for v in transformed_data:
                        v[field_name] = [
                            await self.transform_element(
                                x, with_context(context, field=v)
                            )
                            for x in el["elements"]
                        ]
                    transformed["columns"].add(
                        {
                            "type": "table-column",
                            "field": field_name,
                            "label": self.eval_value(el.get("label", ""), context),
                        }
                    )
                else:
                    el_transformed = await self.transform_table_column(el, context)
                    transformed["columns"].add(el_transformed)

        if "paginator" in element:
            transformed["paginator"] = element.get("paginator")

        return transformed

    async def transform_table_column(self, element, context):
        transformed = {
            "type": "table-column",
            "field": self.eval_value(element.get("field", ""), context),
            "label": self.eval_value(element.get("label", ""), context),
            "elements": AutoList(),
        }
        for el in element.get("elements", []):
            el_transformed = await self.transform_element(el, context)
            transformed["elements"].add(el_transformed)
        return transformed

    async def transform_toolbar(self, element, context):
        transformed = {
            "type": "toolbar",
            "start_elements": AutoList(),
            "elements": AutoList(),
            "end_elements": AutoList(),
        }

        for name in ["start_elements", "elements", "end_elements"]:
            for el in element.get(name, []):
                el_transformed = await self.transform_element(el, context)
                transformed[name].append(el_transformed)
        return transformed

    async def transform_dropdown(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        value = None

        if 'value' in element:
            value = self.eval_value(element.get("value", ""), context)
        elif name:
            value = context.locals.deep_get(name, None)

        transformed = {
            "type": "dropdown",
            "name": name,
            "label": self.eval_value(element.get("label", ""), context),
            "validate": self.eval_object(element.get("validate", {}), context),
            "options": AutoList(),
        }

        if value:
            transformed['value'] = value

        transformed["options"].add(await self.transform_any(element.get("options", []), context))

        return transformed

    async def  option(self, element, context):
        transformed = {
            "label": self.eval_value(element.get("label", ""), context),
            "name": self.eval_value(element.get("name", ""), context),
        }
        return transformed

    async def transform_table_view(self, obj, context):
        ret = {"type": "table-view", "columns": obj["columns"]}
        if "show" in obj:
            ret["show"] = {}
            for k, v in obj["show"].items():
                ret["show"][k] = self.eval_value(v, context)

        elements = AutoList()

        if "elements_dynamic" in obj:
            elements.add(
                await self.transform_elements_dynamic(obj["elements_dynamic"], context)
            )

        ret["rows"] = elements

        return ret

    async def transform_card(self, obj, context):
        ret = {
            "type": "card",
            "title": self.eval_value(obj.get("title", ""), context),
            "text": self.eval_value(obj.get("text", ""), context),
        }

        if "image_src" in obj:
            ret["image_src"] = self.eval_value(obj["image_src"], context)

        elements = AutoList()
        for el in obj.get("elements", []):
            elements.add(await self.transform_element(el, context))

        ret["elements"] = elements

        return ret

    async def transform_card_swiper(self, obj, context):
        ret = {"type": "card-swiper", "title": obj.get("title", "")}
        elements = AutoList()

        if "elements_dynamic" in obj:
            elements.add(
                await self.transform_elements_dynamic(obj["elements_dynamic"], context)
            )

        ret["elements"] = elements
        return ret

    def transform_text(self, obj, context):
        ret = {"text": []}
        for text in obj["text"]:
            ret["text"].append(self.eval_value(text, context))
        return ret

    async def transform_row(self, obj, context):
        elements = AutoList()
        for el in obj.get("elements", []):
            elements.add(await self.transform_element(el, context))
        style = {}
        if "style" in obj:
            style = self.eval_value(obj.get("style", {}), context)
        return {"type": "row", "elements": elements, "style": style}

    async def transform_column(self, obj, context):
        elements = AutoList()
        origin_context = context
        context = copy.copy(origin_context)
        if "elements" in obj:
            for el in obj["elements"]:
                elements.add(await self.transform_element(el, context))
        if "element_template" in obj and "value" in obj:
            template = obj["element_template"]
            value = self.eval_value(obj["value"], context)
            for v in value:
                context.value = munchify(v)
                if isinstance(template, (dict, Mapping)):
                    elements.add(await self.transform_element(template, context))
                elif isinstance(template, (list, tuple, Sequence)):
                    row_elements = AutoList()
                    for row_el in template:
                        row_elements.add(await self.transform_element(row_el, context))
                    elements.add({"type": "row", "elements": row_elements})
        style = {}
        if "style" in obj:
            style = self.eval_value(obj.get("style", {}), context)

        return {"type": "column", "elements": elements, "style": style}

    async def transform_button(self, element, context):
        transformed = {
            "type": element["type"],
            "text": self.eval_value(element.get("text", ""), context),
            "name": self.eval_value(element.get("name", ""), context),
            "icon": self.expand_link(self.eval_value(element.get("icon"), context)),
        }
        if "href" in element:
            transformed["href"] = self.eval_value(element["href"], context)

        if "open_new" in element:
            transformed["open_new"] = self.eval_value(element["open_new"], context)

        if "sub_text" in element:
            transformed["sub_text"] = self.eval_value(element["sub_text"], context)

        if "route" in element:
            transformed["route"] = self.eval_value(element["route"], context)

        if "style" in element:
            style = self.eval_object(element["style"], context)
            transformed["style"] = style

        if "disable" in element:
            transformed["disable"] = (
                self.eval_value(element["disable"], context) or False
            )

        if "disable_text" in element:
            transformed["disable_text"] = self.eval_value(
                element["disable_text"], context
            )

        if "open_modal" in element:
            transformed["open_modal"] = await self.transform_element(
                element["open_modal"], context
            )

        if "open_modal_args" in element:
            transformed["open_modal_args"] = self.eval_object(
                element["open_modal_args"], context
            )

        if "show_ad" in element:
            transformed["show_ad"] = self.eval_object(
                element.get("show_ad", {}), context
            )

        if "action" in element:
            transformed["action"] = self.eval_value(element["action"], context)
            if "action_condition" in element:
                transformed["action_condition"] = self.eval_object(
                    element["action_condition"], context
                )
            if "action_props" in element:
                transformed["action_props"] = self.eval_object(
                    element["action_props"], context
                )
            transformed["args"] = self.eval_object(element.get("args", {}), context)

        if "events" in element:
            transformed["handlers"] = await self.transform_events(
                element["events"], context
            )

        return transformed

    async def transform_menu(self, element, context):
        transformed = {
            "type": element["type"],
            "label": self.eval_value(element.get("label", ""), context),
            "icon": self.eval_value(element.get("icon"), context),
            "items": AutoList(),
        }

        items = transformed["items"]
        for el in element.get("elements", []):
            if el.get("type") == "menu-item":
                items.add(await self.transform_element(el, context))
            else:
                items.add(await self.transform_any(el, context))

        return transformed

    async def transform_navbar(self, obj, context):
        ret = {
            "type": "navbar",
            "show_home": obj.get("show_home", False),
            "show_back": obj.get("show_back", False),
            "show_profile": obj.get("show_profile", False),
            "title": self.eval_value(obj.get("title", ""), context),
        }
        elements = AutoList()
        if "elements" in obj:
            for element in obj["elements"]:
                transformed = await self.transform_element(element, context)
                elements.add(transformed)
            ret["elements"] = elements
        return ret

    async def transform_input(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        value = ""

        if 'value' in element:
            value = self.eval_value(element.get("value", ""), context)
        elif name:
            value = context.locals.deep_get(name, None)

        transformed = {
            "type": "input",
            "label": self.eval_value(element.get("label", ""), context),
            "name": name,
            "value": value,
            "validate": self.eval_object(element.get("validate", {}), context),
            "password": True if element.get("password") == True else False,
        }
        return transformed

    async def transform_checkbox(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        value = False

        if 'value' in element:
            value = self.eval_value(element.get("value", ""), context)
        elif name:
            value = context.locals.deep_get(name, None)

        value = True if value == True else False

        transformed = {
            "type": "checkbox",
            "text": self.eval_value(element.get("text", ""), context),
            "name": name,
            "value": value
        }
        if 'check_strike' in element:
            transformed['check_strike'] =  self.eval_value(element["check_strike"], context)
        return transformed

    async def transform_textarea(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        value = ""

        if 'value' in element:
            value = self.eval_value(element.get("value", ""), context)
        elif name:
            value = context.locals.deep_get(name, None)

        transformed = {
            "type": "textarea",
            "label": self.eval_value(element.get("label", ""), context),
            "name": name,
            "value": value,
        }
        return transformed

    async def transform_datetime_format(self, element, context):
        transformed = ""
        raw_value = context.deep_get(element["value"])
        if raw_value:
            dt_value = DatetimeFormatter.parse(raw_value)
            dt_value = DatetimeFormatter.to_local(dt_value, context.client.get('timezone', {}).get('offset', 0))
            return DatetimeFormatter.format(dt_value, element.get("format"))
        return transformed

    async def transform_calendar(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        value = None

        if 'value' in element:
            value = self.eval_value(element.get("value", ""), context)
        elif name:
            value = context.locals.deep_get(name, None)

        transformed = {
            "type": "calendar",
            "label": self.eval_value(element.get("label", ""), context),
            "name": name,
            "value_format": self.eval_value(element.get("value_format", "yy-mm-dd"), context),
            "icon": True,
            "show_date": True
        }
        if value:
            transformed['value'] = value

        for k in ['min_value', 'max_value', 'range', 'locale', 'icon', 'show_date', 'show_time']:
            if k in element:
                transformed[k] = self.eval_value(element[k], context)
        return transformed

    async def transform_multi_select(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        values = None

        if 'values' in element:
            values = self.eval_value(element.get("values", ""), context)
        elif name:
            values = context.locals.deep_get(name, None)

        transformed = {
            "type": "multi-select",
            "label": self.eval_value(element.get("label", ""), context),
            "name": name,
            "values": values,
            "options": [],
            "chips": True
        }
        for k in ['options', 'chips']:
            if k in element:
                transformed[k] = await self.transform_any(element[k], context)
        return transformed

    async def transform_tag(self, element, context):
        name = self.eval_value(element.get("name", ""), context)
        transformed = {
            "type": "tag",
            "text": self.eval_value(element.get("text", ""), context),
            "color": self.eval_value(element.get("color", ""), context)
        }
        return transformed

    async def transform_logo(self, obj, context):
        ret = {
            "type": "logo",
        }
        for name in ["image_src", "text"]:
            if name in obj:
                ret[name] = self.eval_value(obj[name], context=context)
        return ret

    async def transform_create_object(self, element, context):
        transformed = {"type": "create-object"}
        transformed.update(self.eval_object(element, context))
        return transformed

    async def transform_format(self, element, context):
        return self.eval_value(element, context)

    async def transform_expr(self, element, context):
        return self.eval_value(element, context)


    async def transform_popup_menu(self, element, context):
        menu_element = copy.copy(element)
        menu_element['type'] = 'menu'
        transformed = await self.transform_element(menu_element, context)
        transformed = self.wrap_menu_with_button(transformed)
        return transformed

    def wrap_menu_with_button(self, menu_element):
        btn_element = {
            "type": "button",
            "text": menu_element["label"],
            "icon": menu_element["icon"],
            "style": {"tags": ["text"]},
            "events": {},
        }

        btn_element["events"]["click"] = {
            "type": "open-menu",
            "menu": {"items": menu_element["items"]},
        }

        return btn_element

    async def transform_header(self, obj, context):
        ret = {
            "type": "header",
        }
        for name in ["start_elements", "elements", "end_elements"]:
            if name in obj:
                elements = AutoList()
                for element in obj[name]:
                    transformed = await self.transform_element(element, context)
                    if element["type"] == "menu":
                        transformed = self.wrap_menu_with_button(transformed)
                    elements.add(transformed)
                ret[name] = elements
        return ret

    async def transform_hero(self, obj, context):
        elements = AutoList()
        elements.add(await self.transform_any(obj.get("elements", []), context))
        ret = {
            "type": "hero",
            "title": self.eval_value(obj.get("title"), context),
            "text": self.eval_value(obj.get("text"), context),
            "elements": elements,
        }
        if "image_src" in obj:
            ret["image_src"] = self.eval_value(obj["image_src"], context)
        return ret

    async def load_info_object(self, target):
        if not target:
            return None
        parts = target.split("/")
        if parts[0] == "challenge":
            name = parts[1]
            challenge_def = await self.get_playable_challenge_define(name)
            challenge = ChallengeService(self, challenge_def)
            return await challenge.info()

    async def load_value(self, value_def, context):
        if "collection" in value_def:
            level_id = value_def.get("level_id", None)
            return await self.get_playable(value_def["collection"], level_id=level_id)
        else:
            await logger.error(f"load value not supported. {value_def}")
        return {}

    async def transform_context(self, context_def, context):
        for obj_def in context_def:
            if obj_def["type"] == "info-object":
                name = obj_def["name"]
                target = obj_def["target"]
                context[name] = munchify(await self.load_info_object(target))


    async def transform_locals(self, locals_def, context):
        transformed = {
            "type": "locals"
        }
        for k, v in locals_def.items():
            transformed[k] = await self.transform_any(v, context)
        return transformed

    async def transform_data_format_operations(self, data, format_ops, context):
        _data = data
        if isinstance(format_ops, (list, tuple)):
            for format_op in format_ops:
                _data = await self.transform_data_format_one(_data, format_op, context)
        else:
            _data = await self.transform_data_format_op(_data, format_ops, context)
        return _data


    async def transform_data_format_op(self, data, format_op, context):
        _data = data
        if format_op.get('type') == 'data-format':
            _data = await self.transform_data_format(_data, format_op, context)
        else:
            await logger.warning(f'not valid data format operation')
        return _data


    async def transform_data_format(self, data, format_op, context):
        _data = data or await self.transform_element(format_op.get('data', {}), context)
        if not _data:
            return _data
        for el in format_op.get('elements', []):
            el_type = el.get('type', '').replace('-', '_')
            if not el_type:
                continue
            name = f'transform_{el_type}'
            transform_func = getattr(self, name, None)
            if not transform_func:
                await logger.warning(
                    f"no data transform for element {el_type}."
                )
            elif inspect.iscoroutinefunction(transform_func):
                _data = await transform_func(_data, el, context)
            elif callable(transform_func):
                _data = transform_func(_data, el, context)
        return _data

    async def transform_data_filter(self, data, element, context):
        _data = {}
        keys = element.get('keys', [])
        for k in keys:
            if k in data:
                _data[k] = data[k]
        return _data

    async def transform_data_extract(self, data, element, context):
        _data = data
        key = element.get('key', '')
        if key not in data or 'expr' not in element:
            return data
        value = data[key]
        if isinstance(value, (list, tuple)):
            new_value =  []
            for v in value:
                data_context = with_context(context, it=v)
                new_value.append(self.eval_expr_value(element['expr'], data_context))
            _data[key] = new_value
        else:
            data_context = with_context(context, it=value)
            _data[key] = self.eval_expr_value(element['expr'], data_context)
        return _data

    async def transform_any(self, element, context):
        if isinstance(element, (list, tuple)):
            transformed = []
            for el in element:
                transformed.append(await self.transform_any(el, context))
            return transformed
        elif isinstance(element, (dict, Mapping)):
            transformed = {}
            if "type" in element:
                if element['type'] in ['expr', 'format']:
                    return self.eval_value(element, context)
                else:
                    return await self.transform_element(element, context)
            else:
                transformed = await self.transform_object(element, context)
            return transformed
        else:
            transformed = self.eval_value(element, context)
            return transformed

    async def transform_object(self, element, context):
        transformed = {}
        for k, v in element.items():
            transformed[k] = await self.transform_any(v, context)
        return transformed

    def get_transform_func(self, element_type):
        element_type = element_type.replace("-", "_").lower()
        transform_func_name = f"transform_{element_type}"
        transform_func = getattr(self, transform_func_name, None)
        return transform_func

    async def transform_element(self, element, context):
        if not element:
            return element
        if "condition" in element:
            cond_value = self.eval_condition(element["condition"], context)
            if cond_value == False:
                return None

        if element['type'] in ['modal', 'action']:
            _locals = await self.transform_any(element.get("locals", {}), context)
            new_locals = copy.copy(_locals)
            new_locals.update(context.locals.to_dict() or {})
            context = with_context(context,
                            _locals= new_locals,
                            locals= new_locals)
        elif "locals" in element:
            _locals = await self.transform_any(element["locals"], context)
            new_locals = copy.copy(context.locals or {})
            new_locals.update(_locals)
            context = with_context(context,
                            _locals= _locals,
                            locals= new_locals)

        if 'locals_format' in element:
            formated_locals = await self.transform_data_format_operations(
                context._locals, element["locals_format"], context
            )
            context._locals = munchify(formated_locals)
            context.locals.update(formated_locals)

        if "visible" in element:
            visible = self.eval_value(element["visible"], context)
            if not visible:
                return None

        transform_func = self.get_transform_func(element["type"])
        transformed = None
        if not transform_func:
            await logger.warning(
                f"no transform for element {element['type']}, use transform_object instead."
            )
            transformed = await self.transform_object(element, context)
        elif inspect.iscoroutinefunction(transform_func):
            transformed = await transform_func(element, context)
        elif callable(transform_func):
            transformed = transform_func(element, context)

        if (
            transformed
            and isinstance(transformed, dict)
            and ("style" not in transformed)
            and "style" in element
        ):
            transformed["style"] = await self.transform_any(element["style"], context)

        if 'locals' in element or element["type"] in ['modal']:
            transformed['locals'] = context._locals.to_dict()

        if "events" in element and 'handlers' not in transformed:
            transformed["handlers"] = await self.transform_events(
                element["events"], context
            )
            transformed.pop('events', None)
        return transformed

    async def transform_side_bar(self, element, context):
        transformed = {"type": "side-bar", "elements": AutoList()}

        for el in element.get("elements", []):
            transformed["elements"].add(
                await self.transform_element(copy.copy(el), context)
            )

        return transformed

    async def transform_foreach(self, element, context):
        transformed = AutoList()
        origin_context = context
        model = element.get("model")
        model_data = None
        if model:
            model_data = await self.transform_model(model, context)

        if model_data:
            context = copy.copy(origin_context)
            for obj in model_data:
                for sub_element in element.get("elements", []):
                    context.it = obj
                    transformed.add(await self.transform_element(sub_element, context))
        elif 'alt' in element:
            transformed.add(await self.transform_any(element['alt'], context))

        return transformed

    async def transform_model(self, element, context):
        el_type = element.get("type")
        if el_type == "query":
            return await self.transform_query(element, context)
        elif el_type == 'expr':
            return self.eval_value(element, context)
        elif el_type == 'local-value':
            return await self.transform_local_value(element, context)
        else:
            await logger.warning(f"no transform for model {el_type}.")

    async def transform_match(self, element, context):
        default = await self.transform_any(element.get('default'), context)
        conditions = []

        for el in element.get('elements', []):
            if el.get('type') != 'case-value':
                continue
            case = await self.transform_any(el.get('case'), context)
            if case:
                matched_value = await self.transform_any(el.get('value'), context)
                return matched_value
        return default

    async def transform_query(self, element, context):
        name = element["from"].split(".")[-1]
        filter_expr = ""
        if 'filter' in element:
            filter_expr = await self.transform_any(element['filter'], context)
        order_by = element.get("order_by")
        limit = element.get("limit")
        kwargs = {}
        if order_by:
            kwargs["order_by"] = order_by
        if limit:
            kwargs["limit"] = limit
        dataobj_svc = HolaDataObjectService(self.app_id, name, self)
        formated_filter = self.eval_format_value(filter_expr, context)
        kwargs['context'] = context
        objects = await dataobj_svc.query(formated_filter, **kwargs)
        obj_meta = self.get_object_by_name(name)
        if not obj_meta:
            return objects
        lookup_fields = {}
        formula_fields = {}
        for el in obj_meta.get('elements', []):
            if 'lookup' in el and 'name' in el:
                lookup_fields[el['name']] = (el['lookup'], DataTypeParser.parse(el.get('data_type', '')))
            if 'formula' in el and 'name' in el:
                formula_fields[el['name']] = (el['formula'], DataTypeParser.parse(el.get('data_type', '')))
        for obj in objects:
            related_context = with_context(context, meta=obj)
            for field, lookup in lookup_fields.items():
                if field in obj and obj.get(field, "") == None:
                    if lookup[1] == 'list':
                        obj[field] = []
                    else:
                        obj[field] = None
                    continue
                related_objects = await self.transform_lookup(lookup[0], related_context)
                if lookup[1] == 'list':
                    obj[field] = related_objects
                elif related_objects:
                    obj[field] = related_objects[0]
            for field, lookup in formula_fields.items():
                related_context = with_context(context, meta=obj)
                related_value = self.eval_expr_value(lookup[0], related_context)
                obj[field] = related_value
        return objects

    async def transform_lookup(self, element, context):
        name = element["from"].split(".")[-1]
        filter_expr = element.get("filter") or ""
        order_by = element.get("order_by")
        kwargs = {}
        if order_by:
            kwargs["order_by"] = order_by

        kwargs['context'] = context
        dataobj_svc = HolaDataObjectService(self.app_id, name, self)
        formated_filter = self.eval_format_value(filter_expr, context)

        objects = await dataobj_svc.query(formated_filter, **kwargs)
        obj_meta = self.get_object_by_name(name)
        if not obj_meta:
            return objects

        lookup_fields = {}
        for el in obj_meta.get('elements', []):
            if 'lookup' in el and 'name' in el:
                lookup_fields[el['name']] = (el['lookup'], DataTypeParser.parse(el.get('data_type')))
        for obj in objects:
            related_context = with_context(context, meta=obj)
            for field, lookup in lookup_fields.items():
                if field in obj and obj.get(field, "") == None:
                    if lookup[1] == 'list':
                        obj[field] = []
                    else:
                        obj[field] = None
                    continue
                related_objects = await self.transform_lookup(lookup[0], related_context)
                if lookup[1] == 'list':
                    obj[field] = related_objects
                elif related_objects:
                    obj[field] = related_objects[0]
        return objects


    async def transform_local_value(self, element, context):
        field = element["field"]
        return context.deep_get(field, None)

    async def transform_component_use(self, element, context):
        component_name = self.eval_value(element["name"], context)
        component = self.get_component(component_name, context)
        transformed = AutoList()
        for element in component.get("elements", []):
            transformed.add(
                await self.transform_element(copy.copy(element), context)
            )
        return transformed

    async def transform_paragraph(self, element, context):
        transformed = {
            "type": "paragraph",
            "text": self.eval_value(element["text"], context),
        }

        if "align" in element:
            transformed["align"] = self.eval_value(element["align"], context)

        return transformed

    async def transform_title(self, element, context):
        return {
            "type": "title",
            "level": element.get("level", 3),
            "title": self.eval_value(element["title"], context),
            "sub_title": self.eval_value(element.get("sub_title"), context),
        }

    async def transform_link(self, element, context):
        return {
            "type": "link",
            "text": self.eval_value(element["text"], context),
            "open_mode": self.eval_value(element.get("open_mode", "new"), context),
            "target_url": self.eval_value(element.get("target_url", ""), context),
        }

    async def transform_annotation_text(self, element, context):
        return {
            "type": "annotation-text",
            "text": self.eval_value(element["text"], context),
            "annotation": self.eval_value(element.get("annotation", ""), context),
        }

    async def transform_icon(self, element, context):
        return {
            "type": "icon",
            "icon": self.expand_link(self.eval_value(element.get("icon"), context)),
            "style": self.eval_object(element.get("style", {}), context),
        }

    async def transform_icon_text(self, element, context):
        return {
            "type": "icon-text",
            "icon": self.expand_link(self.eval_value(element.get("icon"), context)),
            "text": self.eval_value(element.get("text", ""), context),
        }

    async def transform_icon_title(self, element, context):
        return {
            "type": "icon-title",
            "icon": self.expand_link(self.eval_value(element.get("icon", ""), context)),
            "count": self.eval_value(element.get("count", 3), context),
        }

    async def transform_plain_text(self, element, context):
        text = await self.transform_any(element["text"], context)
        if isinstance(text, (list, tuple)):
            text = ''.join(text)
        return {"type": "plain-text", "text": text}

    async def transform_status_text(self, element, context):
        label = self.eval_value(element.get('label', ''), context)
        text = await self.transform_any(element["text"], context)
        if isinstance(text, (list, tuple)):
            text = ''.join(text)
        return {"type": "status-text", "text": text, "label": label}

    async def transform_bulleted_list(self, element, context):
        return {
            "type": "bulleted-list",
            "texts": [self.eval_value(text, context) for text in element["texts"]],
        }

    async def transform_progress_bar(self, element, context):
        transformed = {
            "type": "progress-bar",
            "style": self.eval_object(element.get("style", {}), context),
        }

        if "percent" in element:
            percent = self.eval_value(element["percent"], context)
            transformed["percent"] = percent

        if "value" in element:
            value = self.eval_value(element["value"], context)
            transformed["value"] = value

        if "total" in element:
            total = self.eval_value(element["total"], context)
            transformed["total"] = total

        return transformed

    async def transform_progressbar(self, element, context):
        transformed = {
            "type": "progressbar",
            "style": self.eval_object(element.get("style", {}), context),
        }

        if "percent" in element:
            percent = self.eval_value(element["percent"], context)
            transformed["percent"] = percent

        if "value" in element:
            value = self.eval_value(element["value"], context)
            transformed["value"] = value

        if "total" in element:
            total = self.eval_value(element["total"], context)
            transformed["total"] = total

        return transformed

    async def transform_video(self, element, context):
        transformed = {
            "type": "video",
            "video_url": self.eval_value(element.get("video_url", ""), context),
            "autoplay": False,
        }

        if "aspect" in element:
            transformed["aspect"] = self.eval_value(element["aspect"], context)

        if "poster_url" in element:
            transformed["poster_url"] = self.eval_value(element["poster_url"], context)

        if "autoplay" in element:
            transformed["autoplay"] = self.eval_value(element["autoplay"], context)

        if "video_type" in element:
            transformed["video_type"] = self.eval_value(element["video_type"], context)

        if "style" in element:
            style = self.eval_object(element["style"], context)
            transformed["style"] = style

        return transformed

    async def transform_image(self, element, context):
        transformed = {
            "type": "image",
            "image_url": self.eval_value(element.get("image_url", ""), context),
        }

        if "image_type" in element:
            transformed["video_type"] = self.eval_value(element["video_type"], context)

        if "style" in element:
            style = self.eval_object(element["style"], context)
            transformed["style"] = style

        return transformed

    async def transform_icon_button(self, element, context):
        return await self.transform_button(element, context)

    async def transform_star_rating(self, element, context):
        return {
            "type": "star-rating",
            "rating": self.eval_value(element["rating"], context),
            "animate": element.get("animate", True),
        }

    async def transform_separator(self, element, context):
        return {"type": "separator"}

    async def transform_divider(self, element, context):
        return {"type": "divider"}

    async def transform_footer(self, element, context):
        elements = AutoList()
        text = self.eval_value(element.get("text"), context)
        elements.add(await self.transform_element(element.get("element"), context))
        right_elements = AutoList()
        for el in element.get("right_elements", []):
            right_elements.add(await self.transform_element(el, context))
        left_elements = AutoList()
        for el in element.get("left_elements", []):
            left_elements.add(await self.transform_element(el, context))
        return {
            "type": "footer",
            "text": text,
            "element": elements.first,
            "right_elements": right_elements,
            "left_elements": left_elements,
        }

    async def transform_decoration(self, element, context):
        return {
            "type": "decoration",
            "name": element["name"],
            "properties": self.eval_object(element.get("properties", {}), context),
        }

    async def transform_motion(self, element, context):
        return {
            "type": "motion",
            "name": element["name"],
            "properties": self.eval_object(element.get("properties", {}), context),
        }

    async def transform_action_bar(self, element, context):
        elements = AutoList()
        elements.add(await self.transform_element(element.get("element"), context))
        for el in element.get("elements", []):
            elements.add(await self.transform_element(el, context))
        return {"type": "action-bar", "elements": elements}

    def get_component(self, name, context):
        for component in self.components:
            if component.get("name", "") == name:
                return component
        raise Exception(f"component named {name} not found.")

    def transform_playable(self, playable_config):
        def transform_config_object(config):
            content_url_root = ApplicationFolder.get_content_url_root(self.app_id)
            if not isinstance(config, dict):
                return
            for k, v in config.items():
                if (
                    k == "href"
                    or k.endswith("_href")
                    or k.endswith("_link")
                    or k.endswith("_url")
                ):
                    config[k] = v.format(content=content_url_root)
                elif (
                    k.endswith("_hrefs") or k.endswith("_links") or k.endswith("_urls")
                ):
                    config[k] = list(
                        map(lambda x: x.format(content=content_url_root), v)
                    )
                elif isinstance(v, (dict, Mapping)):
                    transform_config_object(v)
                elif isinstance(v, (list, Sequence)):
                    for vv in v:
                        transform_config_object(vv)

        transformed = copy.copy(playable_config)
        transform_config_object(transformed)
        return transformed

    async def get_playable_collection_define(self, collection):
        for conf in self.playable_collections_def:
            if conf.name == collection:
                return conf
        raise Exception(f"no playable collection {collection} found.")

    async def get_playable_challenge_define(self, name):
        for conf in self.playable_challenges_def:
            if conf.name == name:
                return conf
        raise Exception(f"no playable challenge {name} found.")

    def get_static_playable_level(self, levels, level_id=None, level_next=False):
        for idx, level in enumerate(levels):
            if level_id and level["level_id"] == level_id:
                if level_next == False:
                    return level
                else:
                    if idx < len(levels) - 1:
                        return levels[idx + 1]
                    else:
                        return levels[idx]
        return None

    async def get_dynamic_playable_level_config(self, link):
        name = os.path.basename(link)
        name = os.path.splitext(name)[0]
        data = await self.config_loader.get_datafile(name)
        return data

    async def get_playable_levels(self, collection_name):
        collection_def = await self.get_playable_collection_define(collection_name)

        levels_config = []
        if collection_def.configs_link:
            levels_config = await self.get_dynamic_playable_level_config(
                collection_def.configs_link
            )
        elif collection_def.configs:
            levels_config = collection_def.configs

        return levels_config

    async def get_playable(self, collection, level_id=None):
        collection_def = await self.get_playable_collection_define(collection)
        iter_type = collection_def.iter_type

        playable_config = None

        levels_config = []
        if collection_def.configs_link:
            levels_config = await self.get_dynamic_playable_level_config(
                collection_def.configs_link
            )
        elif collection_def.configs:
            levels_config = collection_def.configs

        if iter_type == "sequence":
            level = await self.get_playable_level(collection)
            curr_level_id = level.get("level_id")
            if curr_level_id == None:
                if level_id == None:
                    playable_config = levels_config[0]
                else:
                    playable_config = self.get_static_playable_level(
                        levels_config, level_id, False
                    )
            elif curr_level_id != None:
                playable_config = self.get_static_playable_level(
                    levels_config, curr_level_id, True
                )

        elif iter_type == "daily":
            if level_id == None:
                raise Exception()
            playable_config = self.get_static_playable_level(
                levels_config, level_id, False
            )
        elif iter_type == "random":
            if level_id == None:
                playable_config = random.choice(levels_config)
            else:
                playable_config = self.get_static_playable_level(
                    levels_config, level_id, False
                )
        else:
            raise Exception(f"not supported playable collection iter_type {iter_type}")

        if playable_config:
            playable = self.transform_playable(playable_config)
            playable["collection"] = collection
            return playable
        else:
            raise Exception(f"no collection named {collection}")

    def get_playable_define(self, page_def):
        for element in page_def.elements:
            if element["type"] in ["playable-view"]:
                return element
        raise Exception(f"no playable found in interface {page_def.name}")

    async def get_show_modal_command(self, modal, context):
        component = await self.transform_element(modal, context)
        if component and component["type"] == "modal":
            return ShowModalCommand(args=ShowModalCommandArg(**component))
        else:
            raise Exception(
                f'show modal command not accept valid modal define. but {modal["type"]} got.'
            )

    async def process_page_first_pass(self, page_def, context):
        for element in page_def.elements:
            element_type = element["type"]
            if element_type == "playable-view":
                if "collection" in element:
                    collection = element["collection"]
                    level_id = self.eval_value(element.get("level_id"), context)

                    playable = await self.get_playable(collection, level_id=level_id)
                    context.playable = munchify(playable)
                    return {"playable": playable}
                elif "challenge" in element:
                    name = element["challenge"]["name"]
                    challenge_def = await self.get_playable_challenge_define(name)
                    challenge = ChallengeService(self, challenge_def=challenge_def)
                    context.challenge = munchify(await challenge.info())
                    playable = await challenge.get_playable()
                    context.playable = munchify(playable)
                return {
                    "challenge": challenge,
                    "playable": playable,
                    "playable_def": element,
                }
        return {}

    async def get_show_page_command(self, page_def, context, include_elements=True):
        origin_context = context
        context = copy.copy(origin_context)

        page_route = page_def.route
        if context.get("route_args"):
            page_route = page_route.format(**context.route_args)

        commands = AutoList()
        elements = AutoList()

        transform_elements = include_elements

        if transform_elements:
            ret = await self.process_page_first_pass(page_def, context)
            if ret.get("challenge"):
                challenge = ret["challenge"]
                if await challenge.is_completed():
                    commands.add(
                        await self.handle_events(
                            ret["playable_def"]["challenge"].get("completed"), context
                        )
                    )
                    transform_elements = False
                elif await challenge.is_limited():
                    limited_actions = ret["playable_def"]["challenge"].get("limited")
                    if limited_actions:
                        commands.add(await self.handle_events(limited_actions, context))
                        transform_elements = False
                    else:
                        commands.add(
                            ShowMessageService.show("Challenge limit reached.")
                        )
                        transform_elements = False

        if transform_elements:
            for element in page_def.elements:
                element_type = element["type"]
                if element_type == "playable-view":
                    elements.add(context["playable"].to_dict())
                else:
                    elements.add(
                        await self.transform_element(copy.copy(element), context)
                    )

        page_to = PageInterface(
            name=page_def.name,
            locals=context.locals.to_dict(),
            route=page_route,
            elements=elements,
        )
        if page_def.refresh:
            page_to.refresh = await self.transform_any(page_def.refresh, context)
        commands.add(ShowPageCommand(args=ShowPageCommandArg(page=page_to)))
        return commands

    async def get_playable_level(self, collection):
        state = await self.storage_svc.load_playable_state()
        content = state.playable_state.get(collection, {})
        return content

    async def apply_itembox_change(self, itembox, change):
        items = itembox.detail.get("items", [])
        itembox_def = self.get_itembox_define(itembox.name)
        operator = change["change_operator"]
        if operator == "add":
            value = change["value"]

            for item in value:
                item_name = item["name"]
                item_def = await self.get_item_define(item_name)
                item_stackable = "attributes" not in item_def
                if "count" not in item:
                    item["count"] = 1

                filtered = list(filter(lambda x: x["name"] == item["name"], items))
                if item_stackable:
                    if len(filtered) > 0:
                        filtered[0]["count"] = filtered[0].get("count", 1) + item.get(
                            "count", 1
                        )
                    else:
                        items.append(item)
                else:
                    if len(filtered) > 0:
                        if filtered[0] != item:
                            items.append(item)
                    else:
                        items.append(item)

        else:
            await logger.warning(f"no supported operator {operator} for item changes.")
        capacity = itembox_def.get("capacity", 100)
        if len(items) > capacity:
            itembox.detail["items"] = items[-capacity:]
        else:
            itembox.detail["items"] = items

    async def apply_changes(self, changes):
        player = await self.storage_svc.load_player()
        itemboxes = {}

        for change in changes:
            operator = change["change_operator"]
            name = change["target_name"]
            target_type = change["target_type"]

            if target_type == "player.currency":
                change["value_before"] = player.currency[name]
                if operator == "increase":
                    player.currency[name] += int(change["value"])
                    change["value_after"] = player.currency[name]
                elif operator == "decrease":
                    if player.currency[name] < change["value"]:
                        raise CurrencyValueNotEnoughError(name)
                    player.currency[name] -= int(change["value"])
                    change["value_after"] = player.currency[name]
            elif target_type == "player.attribute":
                change["value_before"] = player.attribute[name]
                if operator == "increase":
                    player.attribute[name] += change["value"]
                    change["value_after"] = player.attribute[name]
                elif operator == "decrease":
                    if player.attribute[name] < change["value"]:
                        raise AttributeValueNotEnoughError(name)
                    player.attribute[name] -= change["value"]
                    change["value_after"] = player.attribute[name]
                elif operator == "set":
                    player.attribute[name] = change["value"]
                    change["value_after"] = player.attribute[name]
                elif operator == "add":
                    player.attribute[name].append(change["value"])
                    change["value_after"] = player.attribute[name]
            elif target_type == "player.itembox":
                if name not in itemboxes:
                    itembox = await self.storage_svc.load_itembox(name=name)
                    itemboxes[name] = itembox
                itembox = itemboxes[name]
                await self.apply_itembox_change(itembox, change)
            else:
                raise Exception(f'not supported change target {change["target"]}')

        await self.storage_svc.save_player(player)
        for name, itembox in itemboxes.items():
            await self.storage_svc.save_itembox(itembox)

    def eval_condition(self, condition, context):
        if isinstance(condition, str):
            expr = condition
        elif isinstance(condition, (dict, Mapping)):
            expr = condition["expr"]
        else:
            raise Exception(f"no valid expression in condition {condition}")

        try:
            ret = restrictedpy.eval(expr, context)
        except Exception as ex:
            logger.sync().error(
                "eval condition error", expr=expr, context=context.to_dict()
            )
            raise (ex)

        if isinstance(ret, bool):
            return ret
        else:
            if ret:
                return True
            else:
                return False

    def eval_match_value(self, value_def, context):
        default_value = self.eval_value(value_def.get("default_value", None), context)
        for match in value_def["match"]:
            condition, value = match["condition"], match["value"]
            if self.eval_condition(condition, context):
                evaluated = self.eval_value(value, context)
                return evaluated
        return default_value

    def eval_choice_value(self, value_def, context):
        count = value_def.get("count", 1)
        choice = value_def["choice"]
        choiced = []
        if isinstance(choice, (list, tuple, Sequence)):
            filtered = list(
                filter(lambda x: x.get("chance", 1) >= random.random(), choice)
            )
            raw_choiced = random.sample(filtered, k=min(count, len(filtered)))
            random.shuffle(raw_choiced)
            choiced = list(map(lambda x: x["value"], raw_choiced))
        elif isinstance(choice, (dict, Mapping)):
            filtered = self.eval_value(choice, context)
            raw_choiced = random.sample(filtered, k=min(count, len(filtered)))
            random.shuffle(raw_choiced)
            choiced = raw_choiced
        if not choiced:
            return None
        return choiced if count > 1 else choiced[0]

    def eval_filter_one_value(self, value_def, context):
        filter_def = value_def["filter_one"]
        objects = self.eval_value(filter_def["objects"], context)
        filtered = []
        filter_func = filter_def["filter_function"]
        for obj in objects:
            t_context = copy.copy(context)
            t_context.object = munchify(obj)
            if self.eval_condition(filter_func, t_context):
                filtered.append(obj)
        return filtered[0] if filtered else None

    def eval_value(self, value_def, context):
        if not value_def:
            return value_def
        if isinstance(value_def, str):
            expr = value_def
            return expr
        elif isinstance(value_def, (dict, Mapping)):
            if "expr" in value_def:
                expr = value_def["expr"]
                return self.eval_expr_value(expr, context)
            elif "format" in value_def:
                expr = value_def["format"]
                return self.eval_format_value(expr, context)
            elif "match" in value_def:
                return self.eval_match_value(value_def, context)
            elif "choice" in value_def:
                return self.eval_choice_value(value_def, context)
            elif "filter_one" in value_def:
                return self.eval_filter_one_value(value_def, context)
            else:
                return self.eval_object(value_def, context)
        else:
            return value_def

    def eval_format_value(self, expr, context):
        f = Formatter()
        parsed = list(f.parse(expr))
        if len(parsed) == 1 and parsed[0][1] == None and parsed[0][2] == None:
            return expr
        try:
            return f.vformat(expr, [], context)
        except Exception as ex:
            logger.sync().error(
                "format error.", expr=expr, context=context.to_dict()
            )
            raise (ex)

    def eval_expr_value(self, expr, context):
        try:
            return restrictedpy.eval(expr, context)
        except Exception as ex:
            logger.sync().error(
                "eval error.", expr=expr, context=context.to_dict()
            )
            raise (ex)


    def eval_ref_object(self, obj, context):
        ref = obj["ref"]
        parts = ref.split("/")
        ns = parts[0]
        if ns == "objects":
            name = parts[1]
            ref_object = self.get_object_by_name(name)
            return self.eval_object(ref_object["value"], context)
        elif ns == "ad_objects":
            name = parts[1]
            ref_object = self.get_ad_object_by_name(name)
            return self.eval_value(ref_object["value"], context)
        return None

    def eval_object_only(self, obj, context, only_keys=None):
        ret = {}
        for k, v in obj.items():
            if only_keys and k in only_keys:
                ret[k] = self.eval_value(v, context)
            else:
                ret[k] = self.eval_value(v, context)

        return ret

    def eval_object(self, obj, context, ignore_keys=None):
        ignored = ignore_keys or []
        if "type" in obj and obj["type"] == "ref-object":
            return self.eval_ref_object(obj, context)
        else:
            ret = {}
            for k, v in obj.items():
                if k == "type":
                    continue
                if ignored and k in ignored:
                    ret[k] = v
                else:
                    ret[k] = self.eval_value(v, context)
        return ret

    def eval_list_or_object(self, obj, context):
        if isinstance(obj, (list, tuple)):
            return [self.eval_object_only(x, context) for x in obj]
        elif isinstance(obj, (dict, Mapping)):
            return self.eval_object_only(obj, context)
        else:
            raise Exception(f"eval list or object, but {type(obj)} given.")

    async def run_change(self, change, context):
        if "condition" in change:
            cond_value = self.eval_condition(change["condition"], context)
            if cond_value == False:
                return None

        if "chance" in change:
            if float(change["chance"]) < random.random():
                return None

        if change["type"] == "change":
            target = change["target"]
            value = self.eval_value(change["value"], context)
            if value:
                parts = target.split(".")
                target_type = ".".join(parts[:2])
                target_name = parts[2] if len(parts) >= 3 else None
                if target_type == "player.currency":
                    if target_name == None:
                        target_name = self.currency_def[0]["name"]

                if target_name == None:
                    raise Exception(f"can not get target_name of target {target}.")

                change_value = value
                if target_type == "player.itembox" and not isinstance(
                    value, (list, tuple)
                ):
                    change_value = [value]

                operator = change["change_operator"]
                name = target_name
                player = await self.storage_svc.load_player()

                if target_type == "player.currency":
                    if operator == "decrease":
                        if player.currency[name] < change_value:
                            raise CurrencyValueNotEnoughError(name)
                elif target_type == "player.attribute":
                    if operator == "decrease":
                        if player.attribute[name] < change_value:
                            raise AttributeValueNotEnoughError(name)

                return {
                    "type": "change",
                    "change_operator": operator,
                    "target": target,
                    "target_type": target_type,
                    "target_name": target_name,
                    "display_name": self.eval_value(
                        change.get("display_name", ""), context
                    ),
                    "value": change_value,
                }
        elif change["type"] == "level_upgrade":
            return await self.run_change_level_upgrade(change, context)
        else:
            await logger.info(f"change type {change['type']} not supported.")
        return None

    def get_player_value(self, player, target):
        parts = target.split(".")
        target_type = ".".join(parts[:2])
        target_name = parts[2] if len(parts) >= 3 else None
        display_name = ""
        if target_type == "player.currency":
            if target_name == None:
                target_name = self.currency_def[0]["name"]
            target_def = self.get_currency_define(target_name)
            display_name = target_def.get("display_name", "")

        if target_name == None:
            raise Exception(f"can not get target_name of target {target}.")

        name = target_name
        if target_type == "player.currency":
            value_before = player.currency[name]
        elif target_type == "player.attribute":
            value_before = player.attribute[name]
            target_def = self.get_attribute_define(target_name)
            display_name = target_def.get("display_name", "")
        else:
            value_before = None

        return {
            "type": "change",
            "target": target,
            "target_type": target_type,
            "target_name": target_name,
            "value_before": value_before,
            "display_name": display_name,
        }

    def build_upgrade_table(self, table):
        new_table = []
        for row in table:
            key = row["key"].strip()
            new_row = copy.copy(row)
            if isinstance(key, str):
                if len(key) < 5:
                    continue
                if key[0] not in ("[", "(") or key[-1] not in ("]", ")"):
                    continue
                s_include = key[0] == "["
                e_include = key[-1] == "]"
                parts = key[1:-1].split(",")
                if len(parts) != 2:
                    continue
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                if not s_include:
                    start = start + 1
                if not e_include:
                    end = end - 1
                if start <= end:
                    new_row["key_start"] = start
                    new_row["key_end"] = end
                    new_table.append(new_row)
            else:
                new_row["key_start"] = key
                new_row["key_end"] = key
                new_table.append(new_row)
        return sorted(new_table, key=lambda x: x["key_start"])

    async def run_change_level_upgrade(self, change, context):
        changes = []
        table = self.build_upgrade_table(
            self.eval_value({"expr": change["table"]}, context)
        )
        targets = change["targets"]
        level_name, value_name, value_required_name = (
            targets["level"],
            targets["value"],
            targets["value_required"],
        )
        player = await self.storage_svc.load_player()
        level_change = self.get_player_value(player, level_name)
        value_change = self.get_player_value(player, value_name)
        value_new = value_change["value_before"]
        value_required_change = self.get_player_value(player, value_required_name)
        value_required_new = value_required_change["value_before"]
        level_increased = 0
        while value_new >= value_required_new:
            value_new -= value_required_new
            level_increased += 1
            if value_new == 0:
                break
            value_required_new = self.get_value_required_for_level(
                table, int(level_change["value_before"]) + level_increased
            )
            if not value_required_new:
                break

        if level_increased > 0:
            level_change["value"] = level_increased
            level_change["change_operator"] = "increase"
            value_change["value"] = value_new
            value_change["change_operator"] = "set"
            value_required_change["value"] = value_required_new
            value_required_change["change_operator"] = "set"
            changes = [level_change, value_change, value_required_change]
        return changes

    def get_value_required_for_level(self, table, key):
        for row in table:
            if key >= row["key_start"] and key <= row["key_end"]:
                return int(row["value"])
        return None

    async def run_process(self, process, context):
        if "condition" in process:
            if not self.eval_condition(process["condition"], context):
                return

        if "call_action" in process:
            args = self.eval_value(process.get("args", {}), context)
            return await self.run_action(process["call_action"], args, context)

        values_gen = {}

        values = process.get("value", {})
        for k, v in values.items():
            values_gen[k] = self.eval_value(v, context)

        if "value" in context:
            context.value.update(values_gen)
        else:
            context.value = munchify(values_gen)

        if "locals" in process:
            context.locals = munchify({})
            await self.transform_locals(process["locals"], context)

        changes_gen = AutoList()

        commands = AutoList()

        changes = process.get("change", [])
        for change in changes:
            try:
                change_result = await self.run_change(change, context)

                if change_result:
                    changes_gen.add(change_result)
            except AttributeValueNotEnoughError as ex:
                not_enough = change.get("not_enough")

                if not_enough:
                    commands.add(await self.handle_events(not_enough, context))
                else:
                    attr_def = self.get_attribute_define(ex.name)
                    display_name = attr_def.get("display_name") or attr_def["name"]
                    commands.add(
                        ShowAlertCommand(
                            ShowAlertCommandArg(
                                text=f"{display_name} not enough.",
                                title="",
                                tags=["error"],
                            )
                        )
                    )
                return commands

            except CurrencyValueNotEnoughError as ex:
                not_enough = change.get("not_enough")

                if not_enough:
                    commands.add(await self.handle_events(not_enough, context))

                else:
                    currency_def = self.get_currency_define(ex.name)
                    display_name = (
                        currency_def.get("display_name") or currency_def["name"]
                    )
                    commands.add(
                        ShowAlertCommand(
                            ShowAlertCommandArg(
                                text=f"{display_name} not enough.",
                                title="",
                                tags=["error"],
                            )
                        )
                    )
                return commands
            except Exception as ex:
                await logger.exception("run change exception")
                commands.add(
                    ShowAlertCommand(
                        ShowAlertCommandArg(
                            text="Sever Error, Please Try Later.",
                            title="",
                            tags=["error"],
                        )
                    )
                )
                return commands

        await logger.debug("changes gen", changes=changes_gen)

        try:
            if len(changes_gen) > 0:
                await self.apply_changes(changes_gen)
        except AttributeValueNotEnoughError as ex:
            attr_def = self.get_attribute_define(ex.name)
            display_name = attr_def.get("display_name") or attr_def["name"]
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text=f"{display_name} not enough.", title="", tags=["error"]
                    )
                )
            )
        except CurrencyValueNotEnoughError as ex:
            currency_def = self.get_currency_define(ex.name)
            display_name = currency_def.get("display_name") or currency_def["name"]
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text=f"{display_name} not enough.", title="", tags=["error"]
                    )
                )
            )
        except Exception as ex:
            await logger.exception("apply change exception")
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text="Sever Error, Please Try Later.", title="", tags=["error"]
                    )
                )
            )
        else:
            if "changes" in context:
                context.changes.extend(list(map(lambda x: munchify(x), changes_gen)))
            else:
                context.changes = list(map(lambda x: munchify(x), changes_gen))

            change_object = {}
            for change in changes_gen:
                change_object[change["target_name"]] = change

            context.change = munchify(change_object)

            effects = process.get("effect", [])
            if len(changes_gen) > 0:
                await self.load_player_to_context(context)
                for effect in effects:
                    name = effect.get("action") or effect.get("name")
                    if "value" in effect:
                        origin_context = context
                        context = copy.copy(origin_context)
                        value = self.eval_object(effect["value"], context)
                        context.value = munchify(value)
                    commands.add(
                        await self.transform_effect(
                            name, effect.get("args", {}), context
                        )
                    )

            finals = process.get("final", [])
            if finals:
                await self.load_player_to_context(context)
                for effect in finals:
                    name = effect.get("action") or effect.get("name")
                    if "value" in effect:
                        origin_context = context
                        context = copy.copy(origin_context)
                        value = self.eval_object(effect["value"], context)
                        context.value = munchify(value)
                    commands.add(
                        await self.transform_effect(
                            name, effect.get("args", {}), context
                        )
                    )

        return commands

    async def run_action(self, name, args, context):
        origin_context = context
        context = copy.copy(origin_context)
        context.args = munchify(args or {})
        action_def = self.action_def.get(name)
        if not action_def:
            raise Exception(f"no named {name} action.")

        commands = AutoList()
        for process in action_def.get("process", []):
            commands.add(await self.run_process(process, context))
        await self.load_player_to_context(origin_context)
        return commands

    async def transform_effect(self, name, args, context):
        commands = AutoList()
        if name == "playable.apply":
            commands.add(
                PlayableApplyCommand(PlayableApplyCommandArg(effect=args["effect"]))
            )
        elif name == "playable.next":
            commands.add(await self.playable_next(args, context))
        elif name == "playable.retry":
            commands.add(await self.playable_retry(args, context))
        elif name == "show_alert":
            text = self.eval_value(args["text"], context)
            title = self.eval_value(args.get("title", ""), context)
            tags = self.eval_value(args.get("tags", []), context)
            commands.add(
                ShowAlertCommand(ShowAlertCommandArg(text=text, title=title, tags=tags))
            )
        elif name == "open_modal":
            open_modal = args["modal"]
            commands.add(await self.get_show_modal_command(open_modal, context))
        elif name == "show_motion":
            commands.add(
                ShowMotionCommand(
                    args=ShowMotionCommandArg(
                        name=args["name"], args=args.get("args", {})
                    )
                )
            )
        elif name == "route_to":
            commands.add(await self.get_page(args["route"], context))
        return commands

    async def handle_events(self, actions, context):
        commands = AutoList()
        if "changes" not in context:
            context.changes = munchify([])
        for action in actions:
            condition = action.get("condition")
            if condition and not self.eval_condition(condition, context):
                continue

            if "chance" in action:
                if action["chance"] < random.random():
                    continue

            if action["type"] == "show_modal":
                modal_def = action["modal"]
                commands.add(
                    await self.get_show_modal_command(copy.copy(modal_def), context)
                )
            elif action["type"] == "call_action":
                commands.add(
                    await self.run_action(
                        action["name"], action.get("args", {}), context
                    )
                )
            elif action["type"] == "show_motion":
                name = action.get("name")
                args = action.get("args", {})
                if not name:
                    continue
                commands.add(
                    ShowMotionCommand(args=ShowMotionCommandArg(name=name, args=args))
                )
            elif action["type"] == "relocate":
                location = action["location"]
                commands.add(await self.get_page(location, context))
            else:
                raise Exception(f'unsupported action {action["type"]}')
        return commands

    async def playable_completed(self, args: PlayableCompletedArg, context):
        page_def, route_args = self.get_page_def(context.session.route)
        origin_context = context
        context = copy.copy(origin_context)
        await self.process_page_first_pass(page_def, context)
        orig_playable = {}
        if context.playable:
            orig_playable = context.playable.to_dict()
        orig_playable.update(
            {
                "succeed": args.succeed,
                "archievement": factory.dump(args.archievement),
                "itemlist": factory.dump(args.items),
            }
        )
        context.playable = munchify(orig_playable)
        commands = AutoList()

        playable_def = self.get_playable_define(page_def)
        if "is_succeed" in playable_def:
            is_succeed = self.eval_value(playable_def["is_succeed"], context)
            args.succeed = is_succeed

        if "locals" in playable_def:
            context.locals = munchify({})
            await self.transform_locals(playable_def["locals"], context)

        if "collection" in playable_def:
            state = await self.storage_svc.get_playable_state(
                playable_def["collection"], args.level.level_id
            )
            if state and "succeed" in state and state["succeed"] == True:
                context.playable.first_time_succeed = False
            else:
                context.playable.first_time_succeed = True
            await self.storage_svc.set_playable_state(
                playable_def["collection"], args.level.level_id, args.succeed
            )
        elif "challenge" in playable_def:
            name = playable_def["challenge"]["name"]
            challenge_def = await self.get_playable_challenge_define(name)
            challenge = ChallengeService(self, challenge_def=challenge_def)
            await challenge.playable_completed(args)

        if args.succeed:
            if "succeed" in playable_def:
                commands.add(await self.handle_events(playable_def["succeed"], context))
        else:
            if "failed" in playable_def:
                commands.add(await self.handle_events(playable_def["failed"], context))

        if len(commands) < 1:
            commands.add(await self.get_show_page_command(page_def, context))

        return commands

    async def playable_next(self, args, context):
        page_route = context.session.route
        page_def, route_args = self.get_page_def(page_route)
        playable_def = self.get_playable_define(page_def)

        commands = AutoList()
        if "next" in playable_def:
            commands.add(await self.handle_events(playable_def["next"], context))
        commands.add(await self.get_show_page_command(page_def, context))
        return commands

    async def playable_retry(self, args, context):
        page_route = context.session.route
        page_def, route_args = self.get_page_def(page_route)

        command = await self.get_show_page_command(page_def, context)
        return command

    async def item_use(self, args, context):
        page_route = context.session.route
        item_name = args["item_name"]
        item_def = await self.get_item_define(item_name)
        itembox = await self.storage_svc.load_itembox()
        items = itembox.detail.get("items", [])
        filtered = list(filter(lambda x: x["name"] == item_name, items))
        if len(filtered) <= 0 or filtered[0]["count"] < 1:
            return ShowAlertCommand(
                args=ShowAlertCommandArg(
                    text=f"物品 {item_def['display_name']} 已经用完了！", tags=["error"]
                )
            )
        filtered[0]["count"] -= 1
        await self.storage_svc.save_itembox(itembox)
        command = AutoList()
        command.add(
            PlayableApplyCommand(
                args=PlayableApplyCommandArg(effect=item_def["effect_name"])
            )
        )
        command.add(await self.get_page_update(page_route, context))
        return command

    async def item_buy(self, args, context):
        page_route = context.session.route
        item_name = args["item_name"]
        item_def = await self.get_item_define(item_name)
        price = item_def["price"]
        player = await self.storage_svc.load_player()
        currency = player.currency
        currency_def = self.get_currency_define()
        currency_name = currency_def["name"]

        if currency.get(currency_name, 0) < price:
            return ShowAlertCommand(
                args=ShowAlertCommandArg(
                    text=f"{currency_def['display_name']}不够了！", tags=["error"]
                )
            )

        command = AutoList()
        itembox = await self.storage_svc.load_itembox()
        items = itembox.detail.get("items", [])
        filtered = list(filter(lambda x: x["name"] == item_name, items))
        if len(filtered) <= 0:
            item = {
                "type": "item",
                "name": item_def["name"],
                "display_name": item_def["display_name"],
                "count": 0,
            }
            items.append(item)
        else:
            item = filtered[0]

        item["count"] += 1
        player.currency[currency_name] -= price
        await self.storage_svc.save_itembox(itembox)
        await self.storage_svc.save_player(player)

        command.add(
            ShowAlertCommand(
                args=ShowAlertCommandArg(
                    text=f"{item_def['display_name']} 购买成功！", tags=["success"]
                )
            )
        )
        command.add(await self.get_page_update(page_route, context))
        return command

    async def ad_showed(self, args, context):
        page_route = context.session.route
        page_def, route_args = self.get_page_def(page_route)
        command = AutoList()
        return command

    async def call_action(self, name, args, context):
        commands = AutoList()
        commands.add(await self.run_action(name, args, context))
        page_route = context.session.route
        has_page_command = (
            len(
                list(filter(lambda x: x.name in ("show_page", "update_page"), commands))
            )
            > 0
        )
        if not has_page_command:
            commands.add(await self.get_page_update(page_route, context=context))
        return commands

    async def handle_reaction(self, reaction, context):
        r_type = reaction.get("type", "")
        if r_type == "route-to":
            route = reaction.get("route")
            if not route:
                await logger.warning("no route for route-to")
            return await self.get_page(route, context)
        return None

    async def handle_permission(self, permission, context):
        p_type = permission.get("type", "")
        if p_type == "condition-check":
            ok = self.eval_condition(permission.get("condition"), context)
            if not ok and "on_false" in permission:
                on_false = permission["on_false"]
                return await self.handle_reaction(on_false, context)
        return None

    async def leave_page(self, page_route, context):
        origin_context = context
        try:
            page_def, route_args = self.get_page_def(page_route)
        except:
            return None
        if route_args:
            context = copy.copy(origin_context)
            context.route_args = munchify(route_args)

        leave_hooks = list(filter(lambda x: x.name == "before_leave", page_def.hooks))
        if leave_hooks:
            commands = AutoList()
            svc = await self.storage_svc.load_page_state_service()
            hook = leave_hooks[0]
            if hook.limit:
                showed = await svc.get_set_view_hooked(
                    page_route, hook.name, hook.tag, hook.limit
                )
                hooked = not showed
            else:
                hooked = True
            if hooked:
                commands.add(await self.handle_events(hook.handlers, context))
                return commands
        return None

    async def get_page_interact_handler(self, page_route, name, event, context):
        def walk_elements(elements):
            for element in elements:
                el_name = element.get("name")
                if el_name and el_name == name:
                    handler = element.get("events", {}).get(event)
                    if handler:
                        return handler
            return None

        page_def, route_args = self.get_page_def(page_route)
        filtered = AutoList()
        for element in page_def.elements:
            filtered.add(
                await self.filter_interact_element(copy.copy(element), context)
            )

        return walk_elements(filtered)

    async def filter_interact_element(self, element, context):
        if not element:
            return element

        filtered = AutoList()
        if "condition" in element:
            cond_value = self.eval_condition(element["condition"], context)
            if cond_value == False:
                return None

        if "visible" in element:
            visible = self.eval_value(element["visible"], context)
            if not visible:
                return None

        if "name" in element and "events" in element:
            filtered.add(element)

        for key, value in element.items():
            if isinstance(value, dict):
                filtered.add(await self.filter_interact_element(value, context))
            elif isinstance(value, (list, tuple)):
                for el in value:
                    if isinstance(el, (dict)):
                        filtered.add(await self.filter_interact_element(el, context))

        # if 'elements' in element:
        #     for sub_element in element['elements']:
        #         filtered.add(await self.filter_interact_element(sub_element, context))

        return filtered

    async def handle_page_interact_handlers(self, handlers, context):
        commands = AutoList()
        for handler in handlers:
            commands.add(await self.handle_page_interact_handler(handler, context))
        return commands

    async def handle_page_interact_handler(self, handler, context):
        handler_type = handler.get("type")
        if handler_type == "invoke-service":
            return await self.handle_invoke_service(handler, context)
        elif handler_type == "invoke-action":
            return await self.handle_invoke_action(handler, context)
        elif handler_type == "route-to":
            return await self.handle_route_to(handler, context)
        elif handler_type == "refresh":
            return await self.handle_refresh(handler, context)
        elif handler_type == "show-modal":
            return await self.handle_show_modal(handler, context)
        elif handler_type == "invalidate-locals":
            await logger.warning(f"TODO: handle invalidate-locals")
        elif handler_type == "create-object":
            return await self.handle_create_object(handler, context)
        elif handler_type == "update-object":
            return await self.handle_update_object(handler, context)
        elif handler_type == "delete-object":
            return await self.handle_delete_object(handler, context)
        else:
            await logger.warning(f"no handler for handler {handler_type}")

    async def handle_invoke_service(self, handler, context):
        name = handler.get("name")
        handler_args = handler.get("args")
        args = copy.copy(context.locals or {})
        args["__info__"] = {
            "app_id": self.app_id,
            "session": self.session.get_data_dict(),
            "user": self.user.get_data_dict() if self.user else {},
        }
        responses = await HolaServiceRegister.call(name, args)
        commands = AutoList()
        for ret in responses:
            ret_type = ret.get("type")
            if ret_type == "service_command":
                if ret["name"] == "reload_session":
                    commands.add(
                        await self.handle_service_command_reload_session(args, context)
                    )
                    new_context = await self._create_context(
                        context.client, context.locals
                    )
                    await self.load_variables_to_context(context=new_context)
                    await self.load_player_to_context(context=new_context)
                    context.clear()
                    context.update(new_context)
                else:
                    commands.add(
                        await self.handle_service_command(
                            ret["name"], ret.get("args", {}), context
                        )
                    )
            elif ret_type == "command":
                commands.add(ret)
            else:
                await logger.warning(f"unknown service response, {ret}")
        return commands

    async def handle_invoke_action(self, handler, context):
        name = handler.get('name')
        action_def = self.action_def.get(name)
        if not action_def:
            raise Exception(f'action with name {name} not found.')

        handler_args = self.handle_any_args(handler.get("args", {}), context)
        context = with_context(context, locals=handler_args)

        action_el = await self.transform_element(action_def, context)

        for el in action_el.get('elements', []):
            await self.handle_data_transform(el, context)

    async def handle_data_transform(self, element, context):
        el_type = element['type']
        if el_type == 'data-process':
            await self.handle_data_process(element, context)
        else:
            await logger.warning(f'no handler for data transform {el_type}')

    async def handle_data_process(self, element, context):
        el_type = element['type']
        for el in element.get('elements', []):
            el_type = el.get('type')
            if el_type == "create-object":
                return await self.handle_create_object(el, context)
            elif el_type == "update-object":
                return await self.handle_update_object(el, context)
            elif el_type == "delete-object":
                return await self.handle_delete_object(el, context)
            else:
                raise Exception(f'not supported data operation {el_type} in DataProcess')

    async def handle_refresh(self, handler, context):
        args = self.handle_any_args(handler.get("args", {}), context)
        context = with_context(context, locals=args)
        return await self.get_page(context.client.route, context)


    def handle_any_args(self, args_def, context):
        if 'type' in args_def and args_def['type'] == 'locals':
            return self.handle_locals(args_def, context)
        else:
            return self.eval_value(args_def, context)


    def handle_locals(self, locals_def, context):
        if locals_def.get('type') == 'locals':
            _locals = context.locals.to_dict()
            return _locals
        else:
            return locals_def

    async def handle_show_modal(self, handler, context):
        if "name" in handler:
            name = handler["name"]
            _modal = self.get_modal_def(name)
            if not _modal:
                await logger.error(f"modal with name {name} not defined.")
        elif "elements" in handler and handler["elements"]:
            _modal = handler["elements"][0]
        else:
            raise Exception(f"unknown to handle show modal handler.")

        if 'args' in handler and handler['args']:
            args = self.handle_any_args(handler['args'], context)
            context = with_context(context, locals=args)

        return await self.get_show_modal_command(_modal, context)

    async def get_object_updated_value(self, obj_def, value, context):
        ret = {}
        for prop in obj_def["elements"]:
            name = prop["name"]
            if name in value:
                ret[name] = value[name]
                continue
            else:
                if "default" in prop:
                    default_value = self.eval_value(prop["default"], context)
                    ret[name] = default_value
                elif "default" in prop.get('data_type', {}):
                    default_value = self.eval_value(prop["data_type"]["default"], context)
                    ret[name] = default_value

        return ret

    async def handle_create_object(self, handler, context):
        _locals = context.locals
        obj_name = handler.get("name")
        if obj_name.startswith("object."):
            obj_name = obj_name[len("object.") :]
            obj_def = self.get_object_by_name(obj_name)
            if not obj_def:
                raise Exception(f'No object definition form name {obj_name}.')
            obj_value = await self.get_object_updated_value(
                obj_def, _locals, context
            )
        else:
            obj_value = _locals
        svc = HolaDataObjectService(self.app_id, obj_name, self)
        await svc.create(**obj_value)

    async def handle_update_object(self, handler, context):
        _locals = context.locals
        obj_name = handler.get("name")
        if obj_name.startswith("object."):
            obj_name = obj_name[len("object.") :]

        if 'object_id' in handler and 'value' in handler:
            obj_value = {}
            obj_value.update(handler['value'])
            obj_value['_id'] = handler['object_id']
        elif 'locals' in handler and handler['locals']:
            obj_value = handler['locals']
        else:
            obj_value = _locals

        svc = HolaDataObjectService(self.app_id, obj_name, self)
        await svc.update(**obj_value)

    async def handle_delete_object(self, handler, context):
        _locals = context.locals
        obj_name = handler.get("name")
        obj_id = self.eval_value(handler.get('object_id'), context)
        if not obj_id:
            obj_id = _locals.get('_id')
        if not obj_id:
            raise Exception(f'delete can not get target object_id.')
        if obj_name.startswith("object."):
            obj_name = obj_name[len("object.") :]
        if "confirm" in handler:
            new_handler = copy.copy(handler)
            new_handler.pop("confirm")
            new_handler["name"] = obj_name
            new_handler["object_id"] = obj_id
            return HolaDialogService.build_confirm_dialog(
                handler["confirm"], new_handler
            )
        else:
            del_args = {
                "_id": obj_id
            }
            svc = HolaDataObjectService(self.app_id, obj_name, self)
            await svc.delete(**del_args)

    async def handle_service_command(self, name, args, context):
        if name == "call_succeed":
            return await self.handle_service_command_call_succeed(args, context)
        elif name == "call_failed":
            return await self.handle_service_command_call_failed(args, context)
        else:
            await logger.warning(
                "no handler for service command {name}, with args: {args}"
            )

    async def handle_service_command_reload_session(self, args, context):
        session_token = self.session.session_token
        session = await SessionService.load(
            app_id=self.app_id, session_token=session_token
        )
        self.session = session
        self.user_id = session.user_id
        if self.user_id:
            self.user = await UserService.load(app_id=self.app_id, user_id=self.user_id)

    async def handle_service_command_call_succeed(self, args, context):
        pass

    async def handle_service_command_call_failed(self, args, context):
        pass

    async def get_close_dialog_command(self, dialog_id, context):
        return CloseModalCommand(args=CloseModalCommandArg(modal_id=dialog_id))

    async def get_page(self, page_route, context):
        origin_context = context
        context = copy.copy(origin_context)
        page_def, route_args = self.get_page_def(page_route)
        if route_args:
            context.route_args = munchify(route_args)

        for key, value in page_def.locals.items():
            if key not in context.locals:
                context.locals[key] = value

        if page_def.permissions:
            for permission in page_def.permissions:
                _commands = await self.handle_permission(permission, context)
                if _commands:
                    return _commands

        svc = await self.storage_svc.load_page_state_service()

        commands = AutoList()

        if page_def.hooks:
            before_commands = AutoList()
            before_hooks = list(
                filter(lambda x: x.name.startswith("before_"), page_def.hooks)
            )
            normal_hooks = list(
                filter(
                    lambda x: (not x.name.startswith("after_"))
                    and (not x.name.startswith("before_")),
                    page_def.hooks,
                )
            )

            for hook in before_hooks:
                if hook.name == "before_first_enter":
                    tag = f"{hook.tag}_b"
                    showed = await svc.get_view_showed(page_route, tag)
                    if not showed:
                        before_commands.add(
                            await self.handle_events(hook.handlers, context)
                        )
                        await svc.set_view_showed(page_route, tag)
                elif hook.name == "before_enter":
                    if hook.condition:
                        condition_true = self.eval_condition(hook.condition, context)
                        if not condition_true:
                            continue
                    if hook.limit:
                        hook_showed = await svc.get_set_view_hooked(
                            page_route, hook.name, hook.tag, hook.limit
                        )
                        if not hook_showed:
                            before_commands.add(
                                await self.handle_events(hook.handlers, context)
                            )
                    else:
                        before_commands.add(
                            await self.handle_events(hook.handlers, context)
                        )

            if before_commands:
                commands.add(
                    await self.get_show_page_command(
                        page_def, context, include_elements=False
                    )
                )
                commands.add(before_commands)
                return commands

            for hook in normal_hooks:
                if hook.name == "first_enter":
                    tag = f"{hook.tag}"
                    showed = await svc.get_view_showed(page_route, tag)
                    if not showed:
                        commands.add(await self.handle_events(hook.handlers, context))
                        await svc.set_view_showed(page_route, tag)

        commands.add(await self.get_show_page_command(page_def, context))

        if page_def.hooks:
            after_hooks = list(
                filter(lambda x: x.name.startswith("after_"), page_def.hooks)
            )
            for hook in after_hooks:
                if hook.name == "after_enter":
                    if hook.limit:
                        showed = await svc.get_set_view_hooked(
                            page_route, hook.name, hook.tag, hook.limit
                        )
                        if not showed:
                            commands.add(
                                await self.handle_events(hook.handlers, context)
                            )
                    else:
                        commands.add(await self.handle_events(hook.handlers, context))

        return commands

    async def get_page_update(self, page_route, context):
        origin_context = context
        context = copy.copy(origin_context)
        page_def, route_args = self.get_page_def(page_route)
        if route_args:
            context.route_args = munchify(route_args)

        commands = AutoList()

        elements = {}

        await self.process_page_first_pass(page_def, context)

        for idx, element in enumerate(page_def.elements):
            element_type = element["type"]
            if element_type != "playable-view":
                elements[str(idx)] = await self.transform_element(
                    copy.copy(element), context
                )

        page_route = page_def.route
        if context.get("route_args"):
            page_route = page_route.format(**context.route_args)

        changed_page = UpdatePageInterface(
            name=page_def.name, route=page_route, changed_elements=elements
        )

        commands.add(
            UpdatePageCommand(args=UpdatePageCommandArg(changed_page=changed_page))
        )

        return commands

    async def get_init_ad(self, context):
        config_list = []
        for init_config in self.ad_init_def:
            if "condition" in init_config:
                if self.eval_condition(init_config["condition"], context):
                    config_list.extend(init_config.get("config", []))
            else:
                config_list.extend(init_config.get("config", []))
        if not config_list:
            return None
        return InitAdCommand(args={"configs": config_list})

    def create_set_session_command(self, user, session):
        return SetSessionCommand(args=SetSessionCommandArg(session=session, user=user))

    async def login(self, args):
        commands = AutoList()
        if "anonymous" not in args:
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text="only anonymous login supported.", title="", tags=["warn"]
                    )
                )
            )
            return commands
        # user, session = await AccountService.create(self.app_id)
        # if user and session:
        #     commands.add(SetSessionCommand(args=SetSessionCommandArg(
        #         session = session.get_data_dict(),
        #         user = user.get_data_dict()
        #     )))
        # else:
        #     commands.add(ShowAlertCommand(
        #         ShowAlertCommandArg(text='登录过程不成功，请稍后尝试~~', title='登录')
        #     ))
        return commands

    async def auth_weixin(self, code, context):
        commands = AutoList()
        # if self.session.weixin_login:
        #     commands.add(ShowAlertCommand(
        #         ShowAlertCommandArg(text='已经微信登录成功了~~', title='微信登录')
        #     ))
        #     return commands
        ret = await SocialAccountService.login_weixin(self.app_id, self.user_id, code)
        if ret["ok"]:
            if "session" in ret.get("data", {}):
                commands.add(
                    self.create_set_session_command(
                        ret["data"]["user"], ret["data"]["session"]
                    )
                )
        else:
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text="登录过程不成功，请稍后尝试~~", title="微信登录", tags=["error"]
                    )
                )
            )
        return commands

    async def handle_request(self, request_cmd):
        ret_commands = AutoList()
        ret_commands.add(self._commands)
        if request_cmd:
            args = request_cmd.args
            context = await self._create_context(
                factory.dump(request_cmd.context), args.get("locals", {})
            )
            await self.load_variables_to_context(context=context)
            await self.load_player_to_context(context=context)
            if context.client.as_device == True:
                thingsvc = await HolaThingService.create(self.app_id, self.config_def, context.client.device or {})
                home_url = thingsvc.get_home_url()
                context.home_url = home_url
                bind_to = await thingsvc.get_bind_to_obj() or {}
                context.bind_to = munchify(bind_to)
            else:
                context.home_url = '/'
                context.bind_to = munchify({})
            if request_cmd.command == "session_start":
                ret_commands.add(await self.handle_session_start(args, context=context))
            elif request_cmd.command == "page_interact":
                ret_commands.add(await self.handle_page_interact(args, context=context))
            elif request_cmd.command == "page_refresh":
                ret_commands.add(await self.handle_page_refresh(args, context=context))
            elif request_cmd.command == "dialog_interact":
                ret_commands.add(
                    await self.handle_dialog_interact(args, context=context)
                )
            elif request_cmd.command == "call_action":
                ret_commands.add(await self.handle_call_action(args, context=context))
            elif request_cmd.command == "route_to":
                ret_commands.add(await self.handle_route_to(args, context=context))
            elif request_cmd.command == "client_event":
                ret_commands.add(await self.handle_client_event(args, context=context))
            # the following commands are deprecated
            elif request_cmd.command == "login":
                ret_commands.add(await self.login(args))
            elif request_cmd.command == "auth_weixin":
                code = args.get("code")
                ret_commands.add(await self.auth_weixin(code, context=context))
            elif request_cmd.command == "playable_completed":
                args = factory.load(args, PlayableCompletedArg)
                ret_commands.add(await self.playable_completed(args, context=context))
            elif request_cmd.command == "playable_next":
                ret_commands.add(await self.playable_next(args, context=context))
            elif request_cmd.command == "playable_retry":
                ret_commands.add(await self.playable_retry(args, context=context))
            elif request_cmd.command == "item_use":
                ret_commands.add(await self.item_use(args, context=context))
            elif request_cmd.command == "item_buy":
                ret_commands.add(await self.item_buy(args, context=context))
            elif request_cmd.command == "ad_showed":
                ret_commands.add(await self.ad_showed(args, context=context))
            else:
                await logger.error(
                    f"no handler for request command {request_cmd.command}"
                )
        else:
            page_context = ClientRequestContext(
                route="/", platform="web", vendor="unknown", version="0.1.0"
            )
            context = await self._create_context(page_context, args.get("locals", {}))
            ret_commands.add(await self.get_page("/", context=context))
        if request_cmd and request_cmd.command and len(ret_commands) == 0:
            raise Exception(
                f"no return commands for request command {request_cmd.command}"
            )
        return ret_commands

    async def handle_session_start(self, args, context):
        commands = AutoList()
        commands.add(await self.get_init_ad(context=context))
        commands.add(await self.get_page(context.home_url or "/", context=context))
        return commands

    async def handle_call_action(self, args, context):
        name = args.get("name")
        action_args = args.get("args", {})
        return await self.call_action(name, action_args, context=context)

    async def handle_route_to(self, args, context):
        commands = await self.leave_page(context.client.route, context=context)
        if commands:
            return commands
        new_context = with_context(context, locals={})
        page_url = args.get('route', '/')
        if page_url == '/' and context.home_url:
            page_url = context.home_url
        return await self.get_page(page_url, context=new_context)

    async def handle_page_interact(self, args, context):
        commands = AutoList()
        name = args.get("name")
        _event = args.get("event")
        _handler = args.get("handler")
        _locals = args.get("locals", {})
        origin_context = context
        context = copy.copy(origin_context)
        context.locals = munchify(_locals)

        if name and _event:
            handler = await self.get_page_interact_handler(
                context.client.route, name, _event, context
            )
            if not handler:
                raise Exception(f"no handler for {name}:{_event}")
            if isinstance(handler, (list, tuple)):
                handlers = handler
            else:
                handlers = [handler]
            commands.add(await self.handle_page_interact_handlers(handlers, context))
        elif _handler:
            st = StampToken()
            handlers = st.load(_handler)
            if not isinstance(handlers, (list, tuple)):
                handlers = [handlers]
            commands.add(await self.handle_page_interact_handlers(handlers, context))
        else:
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text=f"No handler specified.", title="", tags=["warn"]
                    )
                )
            )
        if not commands:
            if 'page_locals' in context.locals:
                _locals = context.locals['page_locals']
                context = with_context(context, locals=_locals)
            commands.add(await self.get_page(context.client.route, context))

        return commands

    async def handle_page_refresh(self, args, context):
        commands = AutoList()
        route = context.client.route
        if 'page_locals' in context.locals:
            _locals = context.locals['page_locals']
            context = with_context(context, locals=_locals)
        commands.add(await self.get_page(route, context=context))
        return commands

    async def handle_dialog_interact(self, args, context):
        commands = AutoList()
        dialog_id = args.get("dialog_id")
        name = args.get("name")
        _event = args.get("event")
        _handler = args.get("handler")
        _locals = args.get("locals", {})
        origin_context = context
        context = copy.copy(origin_context)
        context.locals = munchify(_locals)

        if name and _event:
            handlers = await self.get_dialog_interact_handlers(name, _event, context)
            if not handlers:
                raise Exception(f"no handler for {name}:{_event}")
            commands.add(await self.handle_page_interact_handlers(handlers, context))
        elif _handler:
            st = StampToken()
            handlers = st.load(_handler)
            if not isinstance(handlers, (list, tuple)):
                handlers = [handlers]
            commands.add(await self.handle_page_interact_handlers(handlers, context))
        else:
            commands.add(
                ShowAlertCommand(
                    ShowAlertCommandArg(
                        text=f"No name or handler set to confirm button.",
                        title="",
                        tags=["error"],
                    )
                )
            )

        context.locals = munchify(_locals.get("page_locals", {}))
        if not commands:
            commands.add(await self.get_close_dialog_command(dialog_id, context))
            commands.add(await self.get_page(context.client.route, context))
        return commands

    async def get_dialog_interact_handlers(self, name, event, context):
        modal = self.get_modal_def(name)
        if event not in modal:
            return None
        click_handler = modal.get(event, {}).get("click", None)
        if not click_handler:
            return None
        if not isinstance(click_handler, (list, tuple)):
            click_handler = [click_handler]
        handlers = [await self.transform_element(el, context) for el in click_handler]
        return handlers

    async def handle_client_event(self, args, context):
        commands = AutoList()
        name = args.get("name")
        if name == "ad_showed":
            commands.add(await self.ad_showed(args, context=context))
        return commands
