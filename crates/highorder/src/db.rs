use sea_orm::{Database, DatabaseConnection, DbErr};
use sea_orm_migration::prelude::*;
use std::env;

// Import our migration module
use crate::migration::Migration;

/// Creates a database connection
pub async fn create_db_connection() -> Result<DatabaseConnection, DbErr> {
    // Load environment variables from .env file if available
    dotenv::dotenv().ok();
    
    // Get database URL from environment or use a default for development
    let database_url = env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgres://postgres:postgres@127.0.0.1:5432/highorder".to_string());
    
    // Create connection
    Database::connect(database_url).await
}

/// Creates a database connection with optional URL override
pub async fn create_db_connection_with_url(url: Option<String>) -> Result<DatabaseConnection, DbErr> {
    if let Some(u) = url {
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

/// Run database migrations
async fn run_migrations(conn: &DatabaseConnection) -> Result<(), DbErr> {
    let schema_manager = SchemaManager::new(conn);
    
    // Apply the migration
    Migration.up(&schema_manager).await?;
    println!("Migration applied successfully");
    
    Ok(())
}
