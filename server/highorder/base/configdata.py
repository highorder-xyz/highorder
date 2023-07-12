

from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import os

@dataclass
class ApplicationClientKey:
    app_id: str
    client_key: str
    client_secret: str
    valid: bool

@dataclass
class ApplicationSummary:
    app_id: str
    app_name: str
    client_keys: List[ApplicationClientKey] = field(default_factory=list)

@dataclass
class ApplicationAccount:
    allow_anonymous: bool = field(default=False)