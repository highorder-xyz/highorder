use sea_orm_migration::prelude::*;
use async_trait::async_trait;

pub struct Migration;

impl MigrationName for Migration {
    fn name(&self) -> &str {
        "m0001_init"
    }
}

#[async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // user
        manager
            .create_table(
                Table::create()
                    .table(User::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(User::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(User::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(User::UserName).string_len(256).not_null())
                    .col(ColumnDef::new(User::Deactive).boolean().not_null().default(false))
                    .col(ColumnDef::new(User::IsFrozen).boolean().not_null().default(false))
                    .col(ColumnDef::new(User::Sessions).json_binary().not_null())
                    .col(ColumnDef::new(User::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(User::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(User::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_user")
                            .col(User::AppId)
                            .col(User::UserId),
                    )
                    .index(
                        Index::create()
                            .name("uq_user_app_username")
                            .col(User::AppId)
                            .col(User::UserName)
                            .unique(),
                    )
                    .to_owned(),
            )
            .await?;

        // user_auth
        manager
            .create_table(
                Table::create()
                    .table(UserAuth::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(UserAuth::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(UserAuth::Email).string_len(128).not_null())
                    .col(ColumnDef::new(UserAuth::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(UserAuth::Salt).string_len(32).not_null())
                    .col(ColumnDef::new(UserAuth::PasswordHash).string_len(2048))
                    .col(ColumnDef::new(UserAuth::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(UserAuth::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(UserAuth::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_user_auth")
                            .col(UserAuth::AppId)
                            .col(UserAuth::Email),
                    )
                    .index(
                        Index::create()
                            .name("idx_user_auth_app_user")
                            .col(UserAuth::AppId)
                            .col(UserAuth::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // social_account
        manager
            .create_table(
                Table::create()
                    .table(SocialAccount::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(SocialAccount::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(SocialAccount::SocialId).string_len(512).not_null())
                    .col(ColumnDef::new(SocialAccount::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(SocialAccount::Platform).string_len(64).not_null())
                    .col(ColumnDef::new(SocialAccount::PlatformApp).string_len(256).not_null())
                    .col(ColumnDef::new(SocialAccount::OpenId).string_len(256).not_null())
                    .col(ColumnDef::new(SocialAccount::UnionId).string_len(256).not_null())
                    .col(ColumnDef::new(SocialAccount::AuthInfo).json_binary().not_null())
                    .col(ColumnDef::new(SocialAccount::LinkStatus).boolean().not_null().default(false))
                    .col(ColumnDef::new(SocialAccount::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(SocialAccount::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(SocialAccount::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_social_account")
                            .col(SocialAccount::AppId)
                            .col(SocialAccount::SocialId),
                    )
                    .index(
                        Index::create()
                            .name("idx_social_account_app_user")
                            .col(SocialAccount::AppId)
                            .col(SocialAccount::UserId),
                    )
                    .to_owned(),
            )
            .await?;

        // session
        manager
            .create_table(
                Table::create()
                    .table(Session::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(Session::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(Session::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(Session::UserId).string_len(256))
                    .col(ColumnDef::new(Session::ExpireTime).timestamp_with_time_zone())
                    .col(ColumnDef::new(Session::SessionType).string_len(32).not_null())
                    .col(ColumnDef::new(Session::SessionData).json_binary().not_null())
                    .col(ColumnDef::new(Session::DeviceInfo).json_binary().not_null())
                    .col(ColumnDef::new(Session::CountryCode).string_len(32))
                    .col(ColumnDef::new(Session::Ip).string_len(128))
                    .col(ColumnDef::new(Session::IsValid).boolean().default(true))
                    .col(ColumnDef::new(Session::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(Session::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(Session::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_session")
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
                    .col(ColumnDef::new(InstantKvPack::Prefix).string_len(128).not_null())
                    .col(ColumnDef::new(InstantKvPack::Name).string_len(256).not_null())
                    .col(ColumnDef::new(InstantKvPack::Data).json_binary().not_null())
                    .col(ColumnDef::new(InstantKvPack::ExpireAt).timestamp_with_time_zone())
                    .col(ColumnDef::new(InstantKvPack::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKvPack::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKvPack::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_instant_kv_pack")
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
                    .col(ColumnDef::new(InstantKv::Prefix).string_len(128).not_null())
                    .col(ColumnDef::new(InstantKv::Name).string_len(256).not_null())
                    .col(ColumnDef::new(InstantKv::Field).string_len(256).not_null())
                    .col(ColumnDef::new(InstantKv::Value).text().not_null())
                    .col(ColumnDef::new(InstantKv::ExpireAt).timestamp_with_time_zone())
                    .col(ColumnDef::new(InstantKv::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKv::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(InstantKv::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_instant_kv")
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
                    .col(ColumnDef::new(HolaObject::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaObject::ObjectName).string_len(512).not_null())
                    .col(ColumnDef::new(HolaObject::ObjectId).string_len(512).not_null())
                    .col(ColumnDef::new(HolaObject::Value).json_binary().not_null())
                    .col(ColumnDef::new(HolaObject::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaObject::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaObject::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_object")
                            .col(HolaObject::AppId)
                            .col(HolaObject::ObjectId),
                    )
                    .index(
                        Index::create()
                            .name("idx_hola_object_app_name")
                            .col(HolaObject::AppId)
                            .col(HolaObject::ObjectName),
                    )
                    .to_owned(),
            )
            .await?;

        // hola_resource
        manager
            .create_table(
                Table::create()
                    .table(HolaResource::Table)
                    .if_not_exists()
                    .col(ColumnDef::new(HolaResource::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaResource::ResName).string_len(512).not_null())
                    .col(ColumnDef::new(HolaResource::ResKey).string_len(512).not_null())
                    .col(ColumnDef::new(HolaResource::Allocation).json_binary().not_null())
                    .col(ColumnDef::new(HolaResource::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaResource::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaResource::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_resource")
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
                    .col(ColumnDef::new(HolaVariable::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaVariable::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaVariable::Variable).json_binary().not_null())
                    .col(ColumnDef::new(HolaVariable::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaVariable::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaVariable::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_variable")
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
                    .col(ColumnDef::new(HolaSessionVariable::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaSessionVariable::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionVariable::Variable).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionVariable::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionVariable::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionVariable::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_session_variable")
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
                    .col(ColumnDef::new(HolaPageState::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaPageState::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPageState::PageState).json_binary().not_null())
                    .col(ColumnDef::new(HolaPageState::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPageState::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPageState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_page_state")
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
                    .col(ColumnDef::new(HolaSessionPageState::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaSessionPageState::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPageState::PageState).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPageState::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPageState::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPageState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_session_page_state")
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
                    .col(ColumnDef::new(HolaPlayableState::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaPlayableState::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPlayableState::PlayableState).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayableState::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayableState::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayableState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_playable_state")
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
                    .col(ColumnDef::new(HolaSessionPlayableState::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaSessionPlayableState::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPlayableState::PlayableState).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayableState::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayableState::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayableState::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_session_playable_state")
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
                    .col(ColumnDef::new(HolaPlayer::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaPlayer::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPlayer::Name).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPlayer::State).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayer::Profile).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayer::Attribute).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayer::Currency).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayer::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayer::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayer::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_player")
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
                    .col(ColumnDef::new(HolaSessionPlayer::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::Name).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::State).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::Profile).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::Attribute).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::Currency).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayer::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayer::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayer::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_session_player")
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
                    .col(ColumnDef::new(HolaPlayerItembox::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaPlayerItembox::UserId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPlayerItembox::Name).string_len(256).not_null())
                    .col(ColumnDef::new(HolaPlayerItembox::Attrs).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayerItembox::Detail).json_binary().not_null())
                    .col(ColumnDef::new(HolaPlayerItembox::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayerItembox::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaPlayerItembox::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_player_itembox")
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
                    .col(ColumnDef::new(HolaSessionPlayerItembox::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaSessionPlayerItembox::SessionToken).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPlayerItembox::Name).string_len(256).not_null())
                    .col(ColumnDef::new(HolaSessionPlayerItembox::Attrs).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayerItembox::Detail).json_binary().not_null())
                    .col(ColumnDef::new(HolaSessionPlayerItembox::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayerItembox::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaSessionPlayerItembox::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_session_player_itembox")
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
                    .col(ColumnDef::new(HolaThing::AppId).string_len(128).not_null())
                    .col(ColumnDef::new(HolaThing::ThingId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaThing::DeviceId).string_len(256).not_null())
                    .col(ColumnDef::new(HolaThing::DeviceType).string_len(128).not_null())
                    .col(ColumnDef::new(HolaThing::DeviceInfo).json_binary().not_null())
                    .col(ColumnDef::new(HolaThing::BindTo).json_binary().not_null())
                    .col(ColumnDef::new(HolaThing::HomeUrl).string_len(1024))
                    .col(ColumnDef::new(HolaThing::Related).json_binary().not_null())
                    .col(ColumnDef::new(HolaThing::Created).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaThing::Updated).timestamp_with_time_zone().not_null().default(Expr::current_timestamp()))
                    .col(ColumnDef::new(HolaThing::DataVer).big_integer().not_null().default(0))
                    .primary_key(
                        Index::create()
                            .name("pk_hola_thing")
                            .col(HolaThing::AppId)
                            .col(HolaThing::ThingId),
                    )
                    .index(
                        Index::create()
                            .name("idx_hola_thing_app_device")
                            .col(HolaThing::AppId)
                            .col(HolaThing::DeviceId),
                    )
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
