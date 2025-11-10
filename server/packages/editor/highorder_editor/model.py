"""
HighOrder Editor Database Models
All models merged into a single file for easier management
"""

from peewee import *
import json
import string
import random
from datetime import datetime
from playhouse.sqlite_ext import JSONField

# Database configuration
db = SqliteDatabase('editor.db')


# ============================================================================
# Utilities
# ============================================================================

class IDGenerator(object):
    """Generate unique IDs for various entities"""
    shift_list = [35, 30, 25, 20, 15, 10, 5, 0]
    charset = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

    @classmethod
    def format_ts(cls):
        now_ts = int(datetime.now().timestamp())
        id_list = []
        for n in cls.shift_list:
            c = cls.charset[(now_ts >> n) & 31]
            id_list.append(c)
        assert len(id_list) == 8
        return ''.join(id_list)

    @classmethod
    def create_user_id(cls):
        generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        return 'UU{}'.format(generated)

    @classmethod
    def create_application_id(cls):
        generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(14))
        return 'AP{}'.format(generated)

    @classmethod
    def create_session_id(cls):
        generated = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        return 'SS{}'.format(generated)


# ============================================================================
# Base Model
# ============================================================================

class BaseModel(Model):
    """Base model with common fields"""
    created = DateTimeField(default=datetime.now)
    updated = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def save(self, *args, **kwargs):
        self.updated = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)


# ============================================================================
# User Models
# ============================================================================

class UserModel(BaseModel):
    """User account model"""
    user_id = CharField(max_length=128, primary_key=True, default=IDGenerator.create_user_id)
    email = CharField(max_length=256, unique=True)
    nickname = CharField(max_length=256)
    salt = CharField(max_length=128)
    password = CharField(max_length=256)
    sessions = JSONField(default=dict)

    class Meta:
        table_name = "user"


class SessionModel(BaseModel):
    """User session model"""
    session_id = CharField(max_length=128, primary_key=True)
    user_id = CharField(max_length=256, index=True)
    device = JSONField(default=dict)
    expired_at = DateTimeField()

    class Meta:
        table_name = "session"


# ============================================================================
# Application Models
# ============================================================================

class ApplicationModel(BaseModel):
    """Application model"""
    app_id = CharField(max_length=128, primary_key=True, default=IDGenerator.create_application_id)
    name = CharField(max_length=256, unique=True)
    detail = JSONField(default=dict)
    description = CharField(max_length=4096)
    creator = CharField(max_length=128)
    # State fields (merged from ApplicationStateModel)
    current_version = CharField(max_length=32, null=True)
    previous_version = CharField(max_length=32, null=True)
    latest_version = CharField(max_length=32, null=True)

    class Meta:
        table_name = "application"


class ApplicationClientKeyModel(BaseModel):
    """Application client key model"""
    app_id = CharField(max_length=128)
    clientkey_id = CharField(max_length=128)
    clientkey_secret = CharField(max_length=128)
    valid = BooleanField(default=True)

    class Meta:
        table_name = "application_clientkey"
        primary_key = CompositeKey('app_id', 'clientkey_id')


class ApplicationPublishModel(BaseModel):
    """Application publish model"""
    app_id = CharField(max_length=128)
    app_version = CharField(max_length=32)
    version_number = IntegerField()
    publish_date = DateTimeField()
    publish_type = CharField(max_length=128)
    description = CharField(max_length=4096)
    package_data = BlobField(null=True)  # Binary data for package

    class Meta:
        table_name = "application_publish"
        primary_key = CompositeKey('app_id', 'app_version')


class ApplicationHolaModel(BaseModel):
    """Application Hola model"""
    app_id = CharField(max_length=128, primary_key=True)
    hola = JSONField(default=dict)
    code = JSONField(default=dict)

    class Meta:
        table_name = "application_hola"


# Initialize database tables
def init_db():
    """Initialize database and create tables"""
    db.connect()
    db.create_tables([
        UserModel,
        SessionModel,
        ApplicationModel,
        ApplicationClientKeyModel,
        ApplicationPublishModel,
        ApplicationHolaModel,
    ])
    db.close()

