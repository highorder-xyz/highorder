use crate::config::Settings;

use sqlx::SqlitePool;
use sqlx::sqlite::SqlitePoolOptions;

#[derive(Clone, Default)]
pub struct DbHandles {
    pub sqlite: Option<SqlitePool>,
}

/// Initializes the database using loaded settings. If use_embedded_postgres is enabled,
/// starts an embedded PostgreSQL instance and connects to it; otherwise falls back to db_url logic.
pub async fn init_db_with_settings(settings: &Settings) -> anyhow::Result<DbHandles> {
    dotenv::dotenv().ok();

    let db_url = settings.db_url();
    let sqlite = SqlitePoolOptions::new()
        .max_connections(1)
        .connect(&db_url)
        .await?;

    Ok(DbHandles { sqlite: Some(sqlite) })
}
