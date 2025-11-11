use sea_orm::{Database, DatabaseConnection, DbErr};
use sea_orm_migration::prelude::*;
use postgresql_embedded::{PostgreSQL as EmbeddedPostgres, Settings as EmbeddedSettings};
use std::fs::File;
use std::path::Path;

use crate::config::Settings;
// Import our migration module
use crate::migration::Migration;

/// Creates a database connection
pub async fn create_db_connection() -> Result<DatabaseConnection, DbErr> {
    // Load settings and resolve DB URL (defaults to SQLite if not provided)
    dotenv::dotenv().ok();
    let settings = Settings::load().unwrap_or_default();
    let database_url = settings.db_url();
    
    // Prepare sqlite file if needed
    prepare_sqlite_if_needed(&database_url).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
    // Create connection
    Database::connect(database_url).await
}

async fn start_embedded_postgres(settings: &Settings) -> anyhow::Result<(EmbeddedPostgres, String)> {
    let mut es = EmbeddedSettings::default();
    es.data_dir = std::path::PathBuf::from(settings.embedded_pg_data_dir());
    es.host = "127.0.0.1".to_string();
    es.port = settings.embedded_pg_port(); // 0 => random available port
    es.username = "postgres".to_string();
    es.password = "postgres".to_string();
    // leave installation_dir/version defaults (downloads cached under $HOME/.theseus/postgresql)

    let mut pg = EmbeddedPostgres::new(es);
    pg.setup().await?;
    pg.start().await?;

    // Ensure the target database exists
    let db_name = "highorder";
    if !pg.database_exists(db_name).await? {
        pg.create_database(db_name).await?;
    }

    // Build DSN from the (possibly updated) settings (port 0 becomes the chosen port)
    let s = pg.settings().clone();
    let dsn = format!(
        "postgres://{}:{}@{}:{}/{}",
        s.username, s.password, s.host, s.port, db_name
    );
    Ok((pg, dsn))
}

/// Creates a database connection with optional URL override
pub async fn create_db_connection_with_url(url: Option<String>) -> Result<DatabaseConnection, DbErr> {
    if let Some(u) = url {
        prepare_sqlite_if_needed(&u).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
        return Database::connect(u).await;
    }
    create_db_connection().await
}

/// Initializes the database, including running migrations
pub async fn init_db() -> Result<DatabaseConnection, DbErr> {
    let conn = create_db_connection().await?;
    
    // Run migrations
    run_migrations(&conn).await?;
    println!("Database initialized with migrations applied");
    
    Ok(conn)
}

/// Initializes the database with optional URL, including running migrations
pub async fn init_db_with_url(url: Option<String>) -> Result<DatabaseConnection, DbErr> {
    let conn = create_db_connection_with_url(url).await?;
    run_migrations(&conn).await?;
    println!("Database initialized with migrations applied");
    Ok(conn)
}

/// Initializes the database using loaded settings. If use_embedded_postgres is enabled,
/// starts an embedded PostgreSQL instance and connects to it; otherwise falls back to db_url logic.
pub async fn init_db_with_settings(settings: &Settings) -> Result<(DatabaseConnection, Option<EmbeddedPostgres>), DbErr> {
    if settings.use_embedded_postgres() {
        // Start embedded Postgres
        let (pg, dsn) = start_embedded_postgres(settings).await.map_err(|e| DbErr::Custom(format!("embedded pg error: {}", e)))?;
        let conn = Database::connect(dsn).await?;
        run_migrations(&conn).await?;
        println!("Database initialized with migrations applied");
        return Ok((conn, Some(pg)));
    }

    // Fallback to explicit db_url (or default SQLite)
    let dsn = settings.db_url();
    prepare_sqlite_if_needed(&dsn).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
    let conn = Database::connect(dsn).await?;
    run_migrations(&conn).await?;
    println!("Database initialized with migrations applied");
    Ok((conn, None))
}

/// Run database migrations
async fn run_migrations(conn: &DatabaseConnection) -> Result<(), DbErr> {
    let schema_manager = SchemaManager::new(conn);
    
    // Apply the migration
    Migration.up(&schema_manager).await?;
    println!("Migration applied successfully");
    
    Ok(())
}

fn prepare_sqlite_if_needed(url: &str) -> Result<(), std::io::Error> {
    if !url.starts_with("sqlite://") {
        return Ok(());
    }
    let path_part = &url["sqlite://".len()..];
    // memory DB, skip
    if path_part.starts_with(":memory:") {
        return Ok(());
    }
    // Strip query string
    let path_str = path_part.split('?').next().unwrap_or(path_part);
    let p = Path::new(path_str);
    if let Some(parent) = p.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent)?;
        }
    }
    if !p.exists() {
        File::create(p)?;
    }
    Ok(())
}
