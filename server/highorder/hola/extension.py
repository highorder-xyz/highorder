
import inspect
from dataclasses import dataclass, field, is_dataclass, asdict
from .data import (
    SetSessionCommand, SetSessionCommandArg,
    ShowModalCommand, ShowModalCommandArg,
    ShowAlertCommand, ShowAlertCommandArg,
)
from typing import Any, Optional, List, TypeVar, Callable, Type, cast
from highorder.base.utils import AutoList

@dataclass
class ReloadSessionContext:
    type: str = 'service_command'
    name: str = 'reload_session'

@dataclass
class ExtensionCallFailedArg:
    error_type: str
    error_msg: Optional[str] = ''
    error: Optional[dict] = field(default_factory=dict)

@dataclass
class ExtensionCallFailed:
    args: ExtensionCallFailedArg = field(default_factory=dict)
    type: str = 'service_command'
    name: str = 'call_failed'

@dataclass
class ExtensionCallSucceedArg:
    data: Optional[dict] = field(default_factory=dict)

@dataclass
class ExtensionCallSucceed:
    args: ExtensionCallSucceedArg = field(default_factory=dict)
    type: str = 'service_command'
    name: str = 'call_succeed'


class HolaServiceRegister:
    _services = {}

    @classmethod
    def register(cls, svc_class):
        name = svc_class.ext_name
        if name in cls._services:
            raise Exception(f'Service With Name {name} already registered. {svc_class}.')

        cls._services[name] = {
            'svc_class': svc_class,
            'registered': True
        }
        for attr in dir(svc_class):
            if attr.startswith("__"):
                continue
            attr_value = getattr(svc_class, attr)
            if inspect.ismethod(attr_value) and callable(attr_value):
                svc_name = f'{name}.{attr}'
                cls._services[svc_name] = attr_value

    @classmethod
    async def call(cls, name, args):
        if name not in cls._services:
            raise Exception(f'Service with name {name} not registered.')

        func = cls._services[name]
        if isinstance(func, dict) or not callable(func):
            raise Exception(f'Service name {name} must have func name, like "module.function" format.')

        if inspect.iscoroutinefunction(func) or inspect.iscoroutine(func):
            ret = await func(args)
        else:
            ret = func(args)

        response = AutoList()
        for r in ret:
            if is_dataclass(r):
                response.add(asdict(r))
            elif isinstance(r, dict):
                response.add(r)
            else:
                raise Exception('extension return wrong data type.')

        return response

