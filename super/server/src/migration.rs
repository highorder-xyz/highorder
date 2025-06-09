use sea_orm_migration::prelude::*;

pub struct Migration;

impl MigrationTrait for Migration {
    fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Create the users table
        manager
            .create_table(
                Table::create()
                    .table(Users::Table)
                    .if_not_exists()
                    .col(
                        ColumnDef::new(Users::Id)
                            .integer()
                            .not_null()
                            .auto_increment()
                            .primary_key(),
                    )
                    .col(ColumnDef::new(Users::Username).string().not_null().unique_key())
                    .col(ColumnDef::new(Users::Email).string().not_null().unique_key())
                    .col(ColumnDef::new(Users::Bio).text())
                    .col(
                        ColumnDef::new(Users::CreatedAt)
                            .timestamp_with_time_zone()
                            .not_null()
                            .default(Expr::current_timestamp()),
                    )
                    .col(
                        ColumnDef::new(Users::UpdatedAt)
                            .timestamp_with_time_zone()
                            .not_null()
                            .default(Expr::current_timestamp()),
                    )
                    .to_owned(),
            )
            .await
    }

    fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        // Drop the users table
        manager
            .drop_table(Table::drop().table(Users::Table).to_owned())
            .await
    }
}

// Define the users table columns
#[derive(Iden)]
enum Users {
    Table,
    Id,
    Username,
    Email,
    Bio,
    CreatedAt,
    UpdatedAt,
}
