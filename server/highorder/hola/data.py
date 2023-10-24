from dataclasses import dataclass, field
from typing import Any, Optional, List, TypeVar, Callable, Type, cast
from enum import auto
from datetime import datetime

@dataclass
class ComponentDefine:
    type: str
    name: str
    component: dict


@dataclass
class HookDefine:
    name: str
    tag: str
    limit: Optional[dict] = field(default_factory=dict)
    handlers: Optional[List[dict]] = field(default_factory=list)
    condition: Optional[str] = field(default_factory=str)


@dataclass
class PageDefine:
    type: str
    route: str
    name: Optional[str] = field(default_factory=str)
    valid: Optional[dict] = field(default_factory=dict)
    permissions: Optional[List[dict]] = field(default_factory=list)
    locals: Optional[dict] = field(default_factory=dict)
    events: Optional[dict] = field(default_factory=dict)
    hooks: Optional[List[HookDefine]] = field(default_factory=list)
    elements: Optional[List[dict]] = field(default_factory=list)


@dataclass
class PlayableCollectionConfig:
    name: str
    type: str
    configs_link: Optional[str] = None
    configs: Optional[List[dict]] = None
    iter_type: Optional[str] = None

@dataclass
class TypedObjectRef:
    name: str
    type: str

@dataclass
class LimitObject:
    daily: Optional[int] = None
    hourly: Optional[int] = None
    weekly: Optional[int] = None

    @property
    def none(self):
        return self.daily == None and self.hourly == None  and self.weekly == None

    @property
    def value(self):
        return self.daily or self.hourly or self.weekly

    def get_instant_key(self, time=None):
        if time == None:
            time = datetime.now()
        if self.daily:
            return time.strftime("%Y_%m_%d")
        elif self.hourly:
            return time.strftime("%Y_%m_%d_%H")
        elif self.weekly:
            return time.strftime("%Y_w%W")
        return time.strftime("%Y_%m_%d_%H_%M_%S")

    def get_expire(self):
        if self.daily:
            return 86500
        elif self.hourly:
            return 3700
        elif self.weekly:
            return 605000
        return 17300

@dataclass
class SeletedCollectionConfig:
    method: str
    collection: TypedObjectRef

@dataclass
class PlayableLevelsConfig:
    count: Optional[int] = None
    select: Optional[SeletedCollectionConfig] = None

@dataclass
class PlayableChallengeConfig:
    name: str
    type: str
    levels: PlayableLevelsConfig
    limit: Optional[LimitObject] = None

@dataclass
class PlayableConfig:
    collections: List[PlayableCollectionConfig] = field(default_factory=list)
    challenges: Optional[List[PlayableChallengeConfig]] = None


@dataclass
class ItemDefine:
    type: str
    name: str
    icon: str
    display_name: str
    description: str = ''
    hint: str = ''
    price: int = 0
    effect_name: str = ''

@dataclass
class HolaAdvertisementDefine:
    init: List[dict] = field(default_factory=list)
    show: List[dict] = field(default_factory=list)

@dataclass
class HolaInterfaceDefine:
    interfaces: List[dict] = field(default_factory=list)
    objects: List[dict] = field(default_factory=list)
    actions: List[dict] = field(default_factory=list)
    playable: Optional[PlayableConfig] = field(default_factory=PlayableConfig)
    advertisement: Optional[HolaAdvertisementDefine] = field(default_factory=HolaAdvertisementDefine)


@dataclass
class ShowPageCommandArg:
    page: Any


@dataclass
class ShowPageCommand:
    args: ShowPageCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'show_page'

@dataclass
class SetSessionCommandArg:
    session: Optional[dict] = None
    user: Optional[dict] = None

@dataclass
class SetSessionCommand:
    args: SetSessionCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'set_session'

@dataclass
class ClearSessionCommand:
    args: dict = field(default_factory=dict)
    type: str = 'command'
    name: str = 'clear_session'

@dataclass
class UpdatePageInterface:
    name: str
    route: str
    changed_elements: Optional[dict] = field(default_factory=dict)

@dataclass
class UpdatePageCommandArg:
    changed_page: Any


@dataclass
class UpdatePageCommand:
    args: UpdatePageCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'update_page'

@dataclass
class ModalConfirm:
    text: str = ''
    action: str = ''

@dataclass
class ModalCancel:
    text: str = ''
    action: str = ''


@dataclass
class PageInterface:
    name: str
    route: str
    elements: Optional[List[dict]] = field(default_factory=list)
    type: str = 'page'

@dataclass
class ShowNarrationCommandArg:
    narration: dict = field(default_factory=dict)


@dataclass
class ShowNarrationCommand:
    args: ShowNarrationCommandArg
    type: str = 'command'
    name: str = 'show_narration'


@dataclass
class ShowModalCommandArg:
    type: str = 'modal'
    title: str = ''
    content: str = ''
    content_html: str = ''
    title_action: Optional[dict] = field(default_factory=dict)
    elements: Optional[List[dict]] = field(default_factory=list)
    handlers: Optional[List[dict]] = field(default_factory=list)
    style: Optional[dict] = field(default_factory=dict)
    confirm: Optional[dict] = field(default_factory=dict)
    cancel: Optional[dict] = field(default_factory=dict)

@dataclass
class ShowModalCommand:
    args: Optional[ShowModalCommandArg] = field(default_factory=dict)
    type: str = 'command'
    name: str = 'show_modal'


@dataclass
class ShowMotionCommandArg:
    name: str
    args: dict = field(default_factory=dict)


@dataclass
class ShowMotionCommand:
    args: ShowMotionCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'show_motion'


@dataclass
class ExcuteActionCommandArg:
    action: str
    args: dict = field(default_factory=dict)


@dataclass
class ExcuteActionCommand:
    args: ExcuteActionCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'execute_action'


@dataclass
class ShowAlertCommandArg:
    text: str
    title: str = None


@dataclass
class ShowAlertCommand:
    args: ShowAlertCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'show_alert'


@dataclass
class PlayableApplyCommandArg:
    effect: str

@dataclass
class PlayableApplyCommand:
    args: PlayableApplyCommandArg = field(default_factory=dict)
    type: str = 'command'
    name: str = 'playable_apply'

@dataclass
class ShowAdCommandArg:
    ad_vendor: str
    ad_type: str
    ad_hint: List[str] = field(default_factory=list)

@dataclass
class ShowAdCommand:
    args: ShowAdCommandArg
    type: str = 'command'
    name: str = 'show_ad'

@dataclass
class InitAdCommand:
    args: dict = field(default_factory=dict)
    type: str = 'command'
    name: str = 'init_ad'


@dataclass
class SetPlayerArg(dict):
    attributes: dict = field(default_factory= dict)
    currencies: dict = field(default_factory= dict)
    items: List[dict] = field(default_factory=list)


@dataclass
class SetPlayer:
    args: SetPlayerArg
    type: str = 'command'
    name: str = 'set_player'


@dataclass
class UpdatePlayer:
    args: dict = field(default_factory=dict)
    type: str = 'command'
    name: str = 'update_player'


# Client Request Command
class ClientCommandName:
    navigate_to = 'navigate_to'
    narration_showed = 'narration_showed'
    playable_completed = 'playable_completed'
    ad_showed = 'ad_showed'


@dataclass
class ClientRequestContext:
    route: str
    platform: str
    os: str
    os_version: str
    is_virtual: bool
    vendor: str = field(default="")
    version: str = field(default="0.0.0")
    page_size: dict = field(default_factory=dict)
    screen_size: dict = field(default_factory=dict)


@dataclass
class ClientRequestCommand:
    command: str
    args: dict = field(default_factory=dict)
    context: ClientRequestContext = field(default_factory=dict)


@dataclass
class SetupRequestCommand:
    command: str
    args: dict = field(default_factory=dict)

@dataclass
class PlayableArchievement:
    rating: int
    features: dict = field(default_factory=dict)

@dataclass
class PlayableLevel:
    level_id: str

@dataclass
class PlayableCompletedArg:
    succeed: bool
    level: PlayableLevel
    archievement: PlayableArchievement = field(default_factory=dict)
    items: List[dict] = field(default_factory=list)
