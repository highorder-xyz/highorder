use sea_orm::{Database, DatabaseConnection, DbErr, ConnectOptions};
use sea_orm_migration::prelude::*;
use postgresql_embedded::{PostgreSQL as EmbeddedPostgres, Settings as EmbeddedSettings};
use std::process::Command;
use tokio::time::{sleep, Duration};
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
    if database_url.starts_with("sqlite://") {
        tracing::info!("Preparing SQLite database file: {}", database_url);
    }
    prepare_sqlite_if_needed(&database_url).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
    // Create connection (limit to single connection for sqlite memory)
    let mut opt = ConnectOptions::new(database_url.clone());
    if database_url.to_lowercase().contains(":memory:") {
        opt.max_connections(1);
    }
    Database::connect(opt).await
}

async fn start_embedded_postgres(settings: &Settings) -> anyhow::Result<(EmbeddedPostgres, String)> {
    let mut data_dir = std::path::PathBuf::from(settings.localdb_data_dir());
    tracing::info!("Starting embedded Postgres: data_dir={}", data_dir.to_string_lossy());

    // If the configured data_dir exists and is non-empty but not an initialized cluster (no PG_VERSION),
    // fallback to a subdirectory (e.g. data_dir/db) to satisfy initdb requirement.
    if data_dir.exists() {
        let pg_version = data_dir.join("PG_VERSION");
        if !pg_version.exists() {
            if let Ok(mut rd) = std::fs::read_dir(&data_dir) {
                if rd.next().is_some() {
                    data_dir = data_dir.join("db");
                }
            }
        }
    }

    let mut es = EmbeddedSettings::default();
    es.data_dir = data_dir.clone();
    es.host = "127.0.0.1".to_string();
    es.port = settings.localdb_port(); // 0 => random available port
    es.username = "postgres".to_string();
    es.password = "postgres".to_string();
    es.temporary = false; // preserve data directory across stops
    // tighten server configuration to avoid env interference
    es.configuration.insert(
        "listen_addresses".to_string(),
        "127.0.0.1".to_string(),
    );
    // Do not override unix_socket_directories; rely on system default (/tmp)
    // leave installation_dir/version defaults (downloads cached under $HOME/.theseus/postgresql)

    let mut pg = EmbeddedPostgres::new(es);
    // Force C locale to avoid zh_CN text search configuration issue during initdb
    std::env::set_var("LC_ALL", "C");
    std::env::set_var("LANG", "C");
    pg.setup().await?;

    // Try start with small backoff and cleanup on failure
    let mut started = false;
    let mut last_err: Option<anyhow::Error> = None;
    for _ in 0..3 {
        match pg.start().await {
            Ok(_) => { started = true; break; }
            Err(e) => {
                let mut err_msg = format!("{}", e);
                let start_log = data_dir.join("start.log");
                if let Ok(s) = std::fs::read_to_string(&start_log) {
                    let snippet = if s.len() > 4000 { &s[s.len()-4000..] } else { &s };
                    err_msg = format!("{}\nstart.log:\n{}", err_msg, snippet);
                }
                last_err = Some(anyhow::anyhow!(err_msg));
                sleep(Duration::from_millis(300)).await;
                continue;
            }
        }
    }
    if !started {
        return Err(last_err.unwrap_or_else(|| anyhow::anyhow!("failed to start embedded postgres")));
    }
    let s_now = pg.settings().clone();
    tracing::info!("Embedded Postgres started on {}:{}", s_now.host, s_now.port);

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
        let mut opt = ConnectOptions::new(u.clone());
        if u.to_lowercase().contains(":memory:") {
            opt.max_connections(1);
        }
        return Database::connect(opt).await;
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
    match settings.storage().as_str() {
        "localdb" => {
            // Embedded Postgres
            let data_dir = std::path::PathBuf::from(settings.localdb_data_dir());
            if let Err(e) = ensure_postgres_not_running(&data_dir).await {
                tracing::warn!("ensure_postgres_not_running warning: {}", e);
            }
            let (pg, dsn) = start_embedded_postgres(settings)
                .await
                .map_err(|e| DbErr::Custom(format!("embedded pg error: {}", e)))?;
            let conn = Database::connect(dsn).await?;
            run_migrations(&conn).await?;
            println!("Database initialized with migrations applied");
            Ok((conn, Some(pg)))
        }
        "memory" => {
            // SQLite in-memory, single connection
            let dsn = "sqlite::memory:".to_string();
            let mut opt = ConnectOptions::new(dsn);
            opt.max_connections(1);
            let conn = Database::connect(opt).await?;
            run_migrations(&conn).await?;
            println!("Database initialized with migrations applied");
            Ok((conn, None))
        }
        "litedb" => {
            // SQLite file
            let dsn = settings.db_url();
            prepare_sqlite_if_needed(&dsn).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
            let conn = Database::connect(dsn).await?;
            run_migrations(&conn).await?;
            println!("Database initialized with migrations applied");
            Ok((conn, None))
        }
        "db" => {
            // External database (expected Postgres)
            let dsn = settings.db_url();
            let conn = Database::connect(dsn).await?;
            run_migrations(&conn).await?;
            println!("Database initialized with migrations applied");
            Ok((conn, None))
        }
        other => {
            // Fallback: derive from db_url like before
            tracing::warn!("Unknown storage '{}', falling back to db_url handling", other);
            let dsn = settings.db_url();
            prepare_sqlite_if_needed(&dsn).map_err(|e| DbErr::Custom(format!("sqlite prepare error: {}", e)))?;
            let mut opt = ConnectOptions::new(dsn.clone());
            if dsn.to_lowercase().contains(":memory:") { opt.max_connections(1); }
            let conn = Database::connect(opt).await?;
            run_migrations(&conn).await?;
            println!("Database initialized with migrations applied");
            Ok((conn, None))
        }
    }
}

/// Run database migrations
async fn run_migrations(conn: &DatabaseConnection) -> Result<(), DbErr> {
    let schema_manager = SchemaManager::new(conn);
    
    // Apply the migration
    Migration.up(&schema_manager).await?;
    println!("Migration applied successfully");
    
    Ok(())
}

async fn ensure_postgres_not_running(data_dir: &std::path::Path) -> anyhow::Result<()> {
    // Try graceful stop via pg_ctl (ignoring errors)
    let mut es = EmbeddedSettings::default();
    es.data_dir = data_dir.to_path_buf();
    let mut pg = EmbeddedPostgres::new(es);
    let _ = pg.stop().await;

    // If postmaster.pid exists, try to SIGTERM then SIGKILL the PID
    let pid_path = data_dir.join("postmaster.pid");
    if pid_path.exists() {
        if let Ok(content) = std::fs::read_to_string(&pid_path) {
            if let Some(first) = content.lines().next() {
                if let Ok(pid) = first.trim().parse::<i32>() {
                    tracing::warn!("Killing residual postgres pid {} for data_dir {}", pid, data_dir.to_string_lossy());
                    let _ = Command::new("kill").arg("-TERM").arg(pid.to_string()).status();
                    sleep(Duration::from_millis(500)).await;
                    if pid_path.exists() {
                        let _ = Command::new("kill").arg("-KILL").arg(pid.to_string()).status();
                        sleep(Duration::from_millis(200)).await;
                    }
                }
            }
        }
    }
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
