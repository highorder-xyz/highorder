use sea_orm::entity::prelude::*;

// user
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "user")]
pub struct ModelUser {
    #[sea_orm(primary_key, auto_increment = false)]
    pub app_id: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub user_id: String,
    pub user_name: String,
    pub deactive: bool,
    pub is_frozen: bool,
    pub sessions: serde_json::Value,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationUser {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeyUser {
    #[sea_orm(primary_key, auto_increment = false)]
    AppId,
    #[sea_orm(primary_key, auto_increment = false)]
    UserId,
}

pub type EntityUser = EntityUserAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntityUserAlias;

impl EntityTrait for EntityUserAlias {
    type Model = ModelUser;
    type Column = ColumnUser;
    type PrimaryKey = PrimaryKeyUser;
    type Relation = RelationUser;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnUser {
    AppId,
    UserId,
    UserName,
    Deactive,
    IsFrozen,
    Sessions,
    Created,
    Updated,
    DataVer,
}

// user_auth
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "user_auth")]
pub struct ModelUserAuth {
    #[sea_orm(primary_key, auto_increment = false)]
    pub app_id: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub email: String,
    pub user_id: String,
    pub salt: String,
    pub password_hash: Option<String>,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationUserAuth {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeyUserAuth {
    #[sea_orm(primary_key, auto_increment = false)]
    AppId,
    #[sea_orm(primary_key, auto_increment = false)]
    Email,
}

pub type EntityUserAuth = EntityUserAuthAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntityUserAuthAlias;

impl EntityTrait for EntityUserAuthAlias {
    type Model = ModelUserAuth;
    type Column = ColumnUserAuth;
    type PrimaryKey = PrimaryKeyUserAuth;
    type Relation = RelationUserAuth;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnUserAuth {
    AppId,
    Email,
    UserId,
    Salt,
    PasswordHash,
    Created,
    Updated,
    DataVer,
}

// social_account
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "social_account")]
pub struct ModelSocialAccount {
    #[sea_orm(primary_key, auto_increment = false)]
    pub app_id: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub social_id: String,
    pub user_id: String,
    pub platform: String,
    pub platform_app: String,
    pub open_id: String,
    pub union_id: String,
    pub auth_info: serde_json::Value,
    pub link_status: bool,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationSocialAccount {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeySocialAccount {
    #[sea_orm(primary_key, auto_increment = false)]
    AppId,
    #[sea_orm(primary_key, auto_increment = false)]
    SocialId,
}

pub type EntitySocialAccount = EntitySocialAccountAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntitySocialAccountAlias;

impl EntityTrait for EntitySocialAccountAlias {
    type Model = ModelSocialAccount;
    type Column = ColumnSocialAccount;
    type PrimaryKey = PrimaryKeySocialAccount;
    type Relation = RelationSocialAccount;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnSocialAccount {
    AppId,
    SocialId,
    UserId,
    Platform,
    PlatformApp,
    OpenId,
    UnionId,
    AuthInfo,
    LinkStatus,
    Created,
    Updated,
    DataVer,
}

// session
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "session")]
pub struct ModelSession {
    #[sea_orm(primary_key, auto_increment = false)]
    pub app_id: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub session_token: String,
    pub user_id: Option<String>,
    pub expire_time: Option<DateTimeWithTimeZone>,
    pub session_type: String,
    pub session_data: serde_json::Value,
    pub device_info: serde_json::Value,
    pub country_code: Option<String>,
    pub ip: Option<String>,
    pub is_valid: Option<bool>,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationSession {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeySession {
    #[sea_orm(primary_key, auto_increment = false)]
    AppId,
    #[sea_orm(primary_key, auto_increment = false)]
    SessionToken,
}

pub type EntitySession = EntitySessionAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntitySessionAlias;

impl EntityTrait for EntitySessionAlias {
    type Model = ModelSession;
    type Column = ColumnSession;
    type PrimaryKey = PrimaryKeySession;
    type Relation = RelationSession;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnSession {
    AppId,
    SessionToken,
    UserId,
    ExpireTime,
    SessionType,
    SessionData,
    DeviceInfo,
    CountryCode,
    Ip,
    IsValid,
    Created,
    Updated,
    DataVer,
}

// instant_kv_pack
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "instant_kv_pack")]
pub struct ModelInstantKvPack {
    #[sea_orm(primary_key, auto_increment = false)]
    pub prefix: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub name: String,
    pub data: serde_json::Value,
    pub expire_at: Option<DateTimeWithTimeZone>,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationInstantKvPack {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeyInstantKvPack {
    #[sea_orm(primary_key, auto_increment = false)]
    Prefix,
    #[sea_orm(primary_key, auto_increment = false)]
    Name,
}

pub type EntityInstantKvPack = EntityInstantKvPackAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntityInstantKvPackAlias;

impl EntityTrait for EntityInstantKvPackAlias {
    type Model = ModelInstantKvPack;
    type Column = ColumnInstantKvPack;
    type PrimaryKey = PrimaryKeyInstantKvPack;
    type Relation = RelationInstantKvPack;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnInstantKvPack {
    Prefix,
    Name,
    Data,
    ExpireAt,
    Created,
    Updated,
    DataVer,
}

// instant_kv
#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "instant_kv")]
pub struct ModelInstantKv {
    #[sea_orm(primary_key, auto_increment = false)]
    pub prefix: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub name: String,
    #[sea_orm(primary_key, auto_increment = false)]
    pub field: String,
    pub value: String,
    pub expire_at: Option<DateTimeWithTimeZone>,
    pub created: DateTimeWithTimeZone,
    pub updated: DateTimeWithTimeZone,
    pub data_ver: i64,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum RelationInstantKv {}

#[derive(Copy, Clone, Debug, EnumIter, DerivePrimaryKey)]
pub enum PrimaryKeyInstantKv {
    #[sea_orm(primary_key, auto_increment = false)]
    Prefix,
    #[sea_orm(primary_key, auto_increment = false)]
    Name,
    #[sea_orm(primary_key, auto_increment = false)]
    Field,
}

pub type EntityInstantKv = EntityInstantKvAlias;

#[derive(Copy, Clone, Default, Debug, DeriveEntity)]
pub struct EntityInstantKvAlias;

impl EntityTrait for EntityInstantKvAlias {
    type Model = ModelInstantKv;
    type Column = ColumnInstantKv;
    type PrimaryKey = PrimaryKeyInstantKv;
    type Relation = RelationInstantKv;
    type Related = (); fn related<R: EntityTrait>() -> RelationDef { panic!("not used") }
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveColumn)]
pub enum ColumnInstantKv {
    Prefix,
    Name,
    Field,
    Value,
    ExpireAt,
    Created,
    Updated,
    DataVer,
}
