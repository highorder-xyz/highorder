use axum::{response::Html, routing::get, Router, Extension};
use std::net::SocketAddr;
use std::sync::Arc;

mod base;
mod db;
mod models;
mod migration;

#[tokio::main]
async fn main() {
    // Initialize database connection
    let db_conn = match db::init_db().await {
        Ok(conn) => {
            println!("Database connection established");
            conn
        },
        Err(e) => {
            eprintln!("Failed to connect to database: {}", e);
            std::process::exit(1);
        }
    };
    
    // Wrap the database connection in an Arc for thread-safe sharing
    let db_conn = Arc::new(db_conn);
    
    // Build our application with routes and database connection
    let app = Router::new()
        .route("/", get(handler))
        // Add the database connection to the application state
        .layer(Extension(db_conn));

    // Run the server
    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    println!("Server listening on {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

async fn handler() -> Html<&'static str> {
    Html("<h1>Hello, World!</h1>")
}