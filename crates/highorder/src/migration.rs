use sea_orm_migration::prelude::*;
use async_trait::async_trait;

pub struct Migration;

macro_rules! json_col {
    ($is:expr, $col:expr) => {{
        let mut c = ColumnDef::new($col);
        if $is { c.text(); } else { c.json_binary(); }
        c
    }};
}

macro_rules! ts_col {
    ($is:expr, $col:expr) => {{
        let mut c = ColumnDef::new($col);
        if $is { c.date_time(); } else { c.timestamp_with_time_zone(); }
        c
    }};
}

macro_rules! str_col {
    ($is:expr, $col:expr, $len:expr) => {{
        let mut c = ColumnDef::new($col);
        if $is { c.string(); } else { c.string_len($len); }
        c
    }};
}

impl MigrationName for Migration {
    fn name(&self) -> &str {
        "m0001_init"
    }
}

#[async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let is_sqlite = manager.get_database_backend() == sea_orm::DatabaseBackend::Sqlite;
        // user
        manager
            .create_table(
                Table::create()
                    .table(User::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, User::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, User::UserId, 256).not_null())
                    .col(str_col!(is_sqlite, User::UserName, 256).not_null())
                    .col(ColumnDef::new(User::Deactive).boolean().not_null().default(false))
                    .col(ColumnDef::new(User::IsFrozen).boolean().not_null().default(false))
                    .col(json_col!(is_sqlite, User::Sessions).not_null())
                    .col(ts_col!(is_sqlite, User::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, User::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(User::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(User::AppId)
                            .col(User::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // user unique index (app_id, user_name)
        manager
            .create_index(
                Index::create()
                    .name("uq_user_app_username")
                    .table(User::Table)
                    .col(User::AppId)
                    .col(User::UserName)
                    .unique()
                    .to_owned(),
            )
            .await?;

        // user_auth
        manager
            .create_table(
                Table::create()
                    .table(UserAuth::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, UserAuth::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, UserAuth::Email, 128).not_null())
                    .col(str_col!(is_sqlite, UserAuth::UserId, 256).not_null())
                    .col(str_col!(is_sqlite, UserAuth::Salt, 32).not_null())
                    .col(str_col!(is_sqlite, UserAuth::PasswordHash, 2048).null())
                    .col(ts_col!(is_sqlite, UserAuth::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, UserAuth::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(UserAuth::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(UserAuth::AppId)
                            .col(UserAuth::Email),
                    )
                    .to_owned(),
            )
            .await?;

        // user_auth index (app_id, user_id)
        manager
            .create_index(
                Index::create()
                    .name("idx_user_auth_app_user")
                    .table(UserAuth::Table)
                    .col(UserAuth::AppId)
                    .col(UserAuth::UserId)
                    .to_owned(),
            )
            .await?;

        // social_account
        manager
            .create_table(
                Table::create()
                    .table(SocialAccount::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, SocialAccount::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::SocialId, 512).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::UserId, 256).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::Platform, 64).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::PlatformApp, 256).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::OpenId, 256).not_null())
                    .col(str_col!(is_sqlite, SocialAccount::UnionId, 256).not_null())
                    .col(json_col!(is_sqlite, SocialAccount::AuthInfo).not_null())
                    .col(ColumnDef::new(SocialAccount::LinkStatus).boolean().not_null().default(false))
                    .col(ts_col!(is_sqlite, SocialAccount::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, SocialAccount::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(SocialAccount::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(SocialAccount::AppId)
                            .col(SocialAccount::SocialId),
                    )
                    .to_owned(),
            )
            .await?;

        // social_account index (app_id, user_id)
        manager
            .create_index(
                Index::create()
                    .name("idx_social_account_app_user")
                    .table(SocialAccount::Table)
                    .col(SocialAccount::AppId)
                    .col(SocialAccount::UserId)
                    .to_owned(),
            )
            .await?;

        // session
        manager
            .create_table(
                Table::create()
                    .table(Session::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, Session::SessionToken, 256).not_null())
                    .col(str_col!(is_sqlite, Session::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, Session::UserId, 256).null())
                    .col(ts_col!(is_sqlite, Session::ExpireTime).null())
                    .col(str_col!(is_sqlite, Session::SessionType, 32).not_null())
                    .col(json_col!(is_sqlite, Session::SessionData).not_null())
                    .col(json_col!(is_sqlite, Session::DeviceInfo).not_null())
                    .col(str_col!(is_sqlite, Session::CountryCode, 32).null())
                    .col(str_col!(is_sqlite, Session::Ip, 128).null())
                    .col(ColumnDef::new(Session::IsValid).boolean().default(true))
                    .col(ts_col!(is_sqlite, Session::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, Session::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(Session::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(Session::AppId)
                            .col(Session::SessionToken),
                    )
                    .to_owned(),
            )
            .await?;

        // instant_kv_pack
        manager
            .create_table(
                Table::create()
                    .table(InstantKvPack::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, InstantKvPack::Prefix, 128).not_null())
                    .col(str_col!(is_sqlite, InstantKvPack::Name, 256).not_null())
                    .col(json_col!(is_sqlite, InstantKvPack::Data).not_null())
                    .col(ts_col!(is_sqlite, InstantKvPack::ExpireAt).null())
                    .col(ts_col!(is_sqlite, InstantKvPack::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, InstantKvPack::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKvPack::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(InstantKvPack::Prefix)
                            .col(InstantKvPack::Name),
                    )
                    .to_owned(),
            )
            .await?;

        // instant_kv (row per field)
        manager
            .create_table(
                Table::create()
                    .table(InstantKv::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, InstantKv::Prefix, 128).not_null())
                    .col(str_col!(is_sqlite, InstantKv::Name, 256).not_null())
                    .col(str_col!(is_sqlite, InstantKv::Field, 256).not_null())
                    .col(ColumnDef::new(InstantKv::Value).text().not_null())
                    .col(ts_col!(is_sqlite, InstantKv::ExpireAt).null())
                    .col(ts_col!(is_sqlite, InstantKv::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, InstantKv::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKv::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(InstantKv::Prefix)
                            .col(InstantKv::Name)
                            .col(InstantKv::Field),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_object
        manager
            .create_table(
                Table::create()
                    .table(HolaObject::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaObject::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaObject::ObjectName, 512).not_null())
                    .col(str_col!(is_sqlite, HolaObject::ObjectId, 512).not_null())
                    .col(json_col!(is_sqlite, HolaObject::Value).not_null())
                    .col(ts_col!(is_sqlite, HolaObject::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaObject::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaObject::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaObject::AppId)
                            .col(HolaObject::ObjectId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_object index (app_id, object_name)
        manager
            .create_index(
                Index::create()
                    .name("idx_hola_object_app_name")
                    .table(HolaObject::Table)
                    .col(HolaObject::AppId)
                    .col(HolaObject::ObjectName)
                    .to_owned(),
            )
            .await?;

        // hola_resource
        manager
            .create_table(
                Table::create()
                    .table(HolaResource::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaResource::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaResource::ResName, 512).not_null())
                    .col(str_col!(is_sqlite, HolaResource::ResKey, 512).not_null())
                    .col(json_col!(is_sqlite, HolaResource::Allocation).not_null())
                    .col(ts_col!(is_sqlite, HolaResource::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaResource::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaResource::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaResource::AppId)
                            .col(HolaResource::ResName)
                            .col(HolaResource::ResKey),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_variable
        manager
            .create_table(
                Table::create()
                    .table(HolaVariable::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaVariable::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaVariable::UserId, 256).not_null())
                    .col(json_col!(is_sqlite, HolaVariable::Variable).not_null())
                    .col(ts_col!(is_sqlite, HolaVariable::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaVariable::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaVariable::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaVariable::AppId)
                            .col(HolaVariable::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_session_variable
        manager
            .create_table(
                Table::create()
                    .table(HolaSessionVariable::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaSessionVariable::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaSessionVariable::SessionToken, 256).not_null())
                    .col(json_col!(is_sqlite, HolaSessionVariable::Variable).not_null())
                    .col(ts_col!(is_sqlite, HolaSessionVariable::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaSessionVariable::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionVariable::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaSessionVariable::AppId)
                            .col(HolaSessionVariable::SessionToken),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_page_state
        manager
            .create_table(
                Table::create()
                    .table(HolaPageState::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaPageState::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaPageState::UserId, 256).not_null())
                    .col(json_col!(is_sqlite, HolaPageState::PageState).not_null())
                    .col(ts_col!(is_sqlite, HolaPageState::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaPageState::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPageState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaPageState::AppId)
                            .col(HolaPageState::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_session_page_state
        manager
            .create_table(
                Table::create()
                    .table(HolaSessionPageState::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaSessionPageState::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPageState::SessionToken, 256).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPageState::PageState).not_null())
                    .col(ts_col!(is_sqlite, HolaSessionPageState::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaSessionPageState::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPageState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaSessionPageState::AppId)
                            .col(HolaSessionPageState::SessionToken),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_playable_state
        manager
            .create_table(
                Table::create()
                    .table(HolaPlayableState::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaPlayableState::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaPlayableState::UserId, 256).not_null())
                    .col(json_col!(is_sqlite, HolaPlayableState::PlayableState).not_null())
                    .col(ts_col!(is_sqlite, HolaPlayableState::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaPlayableState::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayableState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaPlayableState::AppId)
                            .col(HolaPlayableState::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_session_playable_state
        manager
            .create_table(
                Table::create()
                    .table(HolaSessionPlayableState::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaSessionPlayableState::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPlayableState::SessionToken, 256).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayableState::PlayableState).not_null())
                    .col(ts_col!(is_sqlite, HolaSessionPlayableState::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaSessionPlayableState::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayableState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaSessionPlayableState::AppId)
                            .col(HolaSessionPlayableState::SessionToken),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_player
        manager
            .create_table(
                Table::create()
                    .table(HolaPlayer::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaPlayer::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaPlayer::UserId, 256).not_null())
                    .col(str_col!(is_sqlite, HolaPlayer::Name, 256).not_null())
                    .col(json_col!(is_sqlite, HolaPlayer::State).not_null())
                    .col(json_col!(is_sqlite, HolaPlayer::Profile).not_null())
                    .col(json_col!(is_sqlite, HolaPlayer::Attribute).not_null())
                    .col(json_col!(is_sqlite, HolaPlayer::Currency).not_null())
                    .col(ts_col!(is_sqlite, HolaPlayer::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaPlayer::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayer::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaPlayer::AppId)
                            .col(HolaPlayer::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_session_player
        manager
            .create_table(
                Table::create()
                    .table(HolaSessionPlayer::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaSessionPlayer::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPlayer::SessionToken, 256).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPlayer::Name, 256).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayer::State).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayer::Profile).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayer::Attribute).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayer::Currency).not_null())
                    .col(ts_col!(is_sqlite, HolaSessionPlayer::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaSessionPlayer::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayer::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaSessionPlayer::AppId)
                            .col(HolaSessionPlayer::SessionToken),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_player_itembox
        manager
            .create_table(
                Table::create()
                    .table(HolaPlayerItembox::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaPlayerItembox::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaPlayerItembox::UserId, 256).not_null())
                    .col(str_col!(is_sqlite, HolaPlayerItembox::Name, 256).not_null())
                    .col(json_col!(is_sqlite, HolaPlayerItembox::Attrs).not_null())
                    .col(json_col!(is_sqlite, HolaPlayerItembox::Detail).not_null())
                    .col(ts_col!(is_sqlite, HolaPlayerItembox::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaPlayerItembox::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayerItembox::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaPlayerItembox::AppId)
                            .col(HolaPlayerItembox::UserId)
                            .col(HolaPlayerItembox::Name),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_session_player_itembox
        manager
            .create_table(
                Table::create()
                    .table(HolaSessionPlayerItembox::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaSessionPlayerItembox::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPlayerItembox::SessionToken, 256).not_null())
                    .col(str_col!(is_sqlite, HolaSessionPlayerItembox::Name, 256).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayerItembox::Attrs).not_null())
                    .col(json_col!(is_sqlite, HolaSessionPlayerItembox::Detail).not_null())
                    .col(ts_col!(is_sqlite, HolaSessionPlayerItembox::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaSessionPlayerItembox::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayerItembox::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaSessionPlayerItembox::AppId)
                            .col(HolaSessionPlayerItembox::SessionToken)
                            .col(HolaSessionPlayerItembox::Name),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_thing
        manager
            .create_table(
                Table::create()
                    .table(HolaThing::Table)
                    .if_not_exists()
                    .col(str_col!(is_sqlite, HolaThing::AppId, 128).not_null())
                    .col(str_col!(is_sqlite, HolaThing::ThingId, 256).not_null())
                    .col(str_col!(is_sqlite, HolaThing::DeviceId, 256).not_null())
                    .col(str_col!(is_sqlite, HolaThing::DeviceType, 128).not_null())
                    .col(json_col!(is_sqlite, HolaThing::DeviceInfo).not_null())
                    .col(json_col!(is_sqlite, HolaThing::BindTo).not_null())
                    .col(str_col!(is_sqlite, HolaThing::HomeUrl, 1024).null())
                    .col(json_col!(is_sqlite, HolaThing::Related).not_null())
                    .col(ts_col!(is_sqlite, HolaThing::Created).not_null().default(Expr::current_timestamp()))
                    .col(ts_col!(is_sqlite, HolaThing::Updated).not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaThing::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .col(HolaThing::AppId)
                            .col(HolaThing::ThingId),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_thing index (app_id, device_id)
        manager
            .create_index(
                Index::create()
                    .name("idx_hola_thing_app_device")
                    .table(HolaThing::Table)
                    .col(HolaThing::AppId)
                    .col(HolaThing::DeviceId)
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(HolaThing::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaSessionPlayerItembox::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaPlayerItembox::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaSessionPlayer::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaPlayer::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaSessionPlayableState::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaPlayableState::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaSessionPageState::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaPageState::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaSessionVariable::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaVariable::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaResource::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(HolaObject::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(InstantKv::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(InstantKvPack::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(Session::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(SocialAccount::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(UserAuth::Table).to_owned())
            .await?;
        manager
            .drop_table(Table::drop().table(User::Table).to_owned())
            .await?;
        Ok(())
    }
}

#[derive(Iden)]
enum User {
    Table,
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

#[derive(Iden)]
enum UserAuth {
    Table,
    AppId,
    Email,
    UserId,
    Salt,
    PasswordHash,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum SocialAccount {
    Table,
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

#[derive(Iden)]
enum Session {
    Table,
    SessionToken,
    AppId,
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

#[derive(Iden)]
enum InstantKvPack {
    Table,
    Prefix,
    Name,
    Data,
    ExpireAt,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum InstantKv {
    Table,
    Prefix,
    Name,
    Field,
    Value,
    ExpireAt,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaObject {
    Table,
    AppId,
    ObjectName,
    ObjectId,
    Value,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaResource {
    Table,
    AppId,
    ResName,
    ResKey,
    Allocation,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaVariable {
    Table,
    AppId,
    UserId,
    Variable,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaSessionVariable {
    Table,
    AppId,
    SessionToken,
    Variable,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaPageState {
    Table,
    AppId,
    UserId,
    PageState,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaSessionPageState {
    Table,
    AppId,
    SessionToken,
    PageState,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaPlayableState {
    Table,
    AppId,
    UserId,
    PlayableState,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaSessionPlayableState {
    Table,
    AppId,
    SessionToken,
    PlayableState,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaPlayer {
    Table,
    AppId,
    UserId,
    Name,
    State,
    Profile,
    Attribute,
    Currency,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaSessionPlayer {
    Table,
    AppId,
    SessionToken,
    Name,
    State,
    Profile,
    Attribute,
    Currency,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaPlayerItembox {
    Table,
    AppId,
    UserId,
    Name,
    Attrs,
    Detail,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaSessionPlayerItembox {
    Table,
    AppId,
    SessionToken,
    Name,
    Attrs,
    Detail,
    Created,
    Updated,
    DataVer,
}

#[derive(Iden)]
enum HolaThing {
    Table,
    AppId,
    ThingId,
    DeviceId,
    DeviceType,
    DeviceInfo,
    BindTo,
    HomeUrl,
    Related,
    Created,
    Updated,
    DataVer,
}
