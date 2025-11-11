use axum::{
    extract::{Path, Query},
    http::{header, HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::get,
    Router,
};
use axum::Extension;
use serde::Deserialize;
use std::{net::SocketAddr, path::PathBuf, sync::Arc};
use tower_http::trace::TraceLayer;
use tokio::signal;

mod base;
mod db;
// mod models; // will be added when SeaORM entities are ready
mod migration;
mod config;
mod error;
mod loader;
mod hola;

use config::Settings;
use sea_orm::DatabaseConnection;

#[derive(Clone)]
pub struct AppState {
    pub db: Arc<DatabaseConnection>,
    pub settings: Settings,
    pub webapp_root: Option<PathBuf>,
    pub data_dir: PathBuf,
    pub content_url: Option<String>,
}

#[derive(Deserialize)]
struct IndexQuery {
    app_id: Option<String>,
    client_key: Option<String>,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    let settings = Settings::load().unwrap_or_default();
    tracing::info!(
        "Program start: debug={}, host={}, port={}, embedded_pg={}",
        settings.debug(),
        settings.host(),
        settings.port(),
        settings.use_embedded_postgres()
    );

    // Initialize database connection (use embedded Postgres when enabled; otherwise use db_url)
    let (db_conn, mut embedded_pg_guard) = match db::init_db_with_settings(&settings).await {
        Ok((conn, guard)) => {
            tracing::info!("Database connection established");
            (conn, guard)
        }
        Err(e) => {
            tracing::error!("Failed to connect to database: {}", e);
            std::process::exit(1);
        }
    };

    // Prepare paths
    let data_dir = settings
        .data_dir
        .clone()
        .map(PathBuf::from)
        .unwrap_or_else(|| std::env::current_dir().unwrap());
    let webapp_root = settings.webapp_root.clone().map(PathBuf::from);

    let state = AppState {
        db: Arc::new(db_conn),
        settings: settings.clone(),
        webapp_root,
        data_dir,
        content_url: settings.content_url.clone(),
    };

    // Build routes
    let mut app = Router::new()
        .route("/", get(index))
        .route("/favicon.ico", get(favicon))
        .layer(Extension(state.clone()))
        .layer(TraceLayer::new_for_http());

    // Assets under webapp_root/assets
    app = app.route("/assets/*path", get(assets));

    // Static content mapping when content_url is not specified
    if state.content_url.as_deref().unwrap_or("").is_empty() {
        app = app.route("/static/:app_folder_name/content/*path", get(static_content));
    }

    // service/hola endpoints
    app = app
        .route("/service/hola/main", axum::routing::post(hola::hola_main))
        .route("/service/hola/setup", axum::routing::post(hola::hola_setup))
        .route("/service/hola/lite", axum::routing::post(hola::hola_lite));

    // Run server
    let addr: SocketAddr = format!("{}:{}", state.settings.host(), state.settings.port())
        .parse()
        .expect("invalid host/port");
    tracing::info!("Server listening on {}", addr);
    let app = app.with_state(());
    let server = axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .with_graceful_shutdown(async move {
            let _ = signal::ctrl_c().await;
        });

    if let Err(e) = server.await {
        tracing::error!("server error: {}", e);
    }

    // On shutdown, if we started an embedded Postgres, stop it gracefully
    if let Some(pg) = embedded_pg_guard.take() {
        let _ = pg.stop().await;
    }
}

async fn index(Extension(state): Extension<AppState>, Query(q): Query<IndexQuery>) -> Response {
    if q.app_id.is_some() && q.client_key.is_some() {
        if let Some(root) = &state.webapp_root {
            let index_path = root.join("index.html");
            return serve_file(index_path).await;
        }
    }
    (StatusCode::OK, "highorder server ok").into_response()
}

async fn favicon(Extension(state): Extension<AppState>) -> Response {
    if let Some(root) = &state.webapp_root {
        let fpath = root.join("favicon.ico");
        if fpath.exists() {
            return serve_file(fpath).await;
        }
    }
    (StatusCode::NOT_FOUND, "").into_response()
}

#[derive(Deserialize)]
struct AssetPath {
    path: String,
}

async fn assets(Extension(state): Extension<AppState>, Path(AssetPath { path }): Path<AssetPath>) -> Response {
    if let Some(root) = &state.webapp_root {
        let fp = sanitize_join(root.join("assets"), &path);
        return serve_file(fp).await;
    }
    (StatusCode::NOT_FOUND, "").into_response()
}

#[derive(Deserialize)]
struct StaticPathParams {
    app_folder_name: String,
    path: String,
}

async fn static_content(Extension(state): Extension<AppState>, Path(StaticPathParams { app_folder_name, path }): Path<StaticPathParams>) -> Response {
    // Map to data_dir/live/{app_folder_name}/content/{path}
    let base = state.data_dir.join("live").join(app_folder_name).join("content");
    let fp = sanitize_join(base, &path);
    serve_file(fp).await
}

fn sanitize_join(base: PathBuf, rest: &str) -> PathBuf {
    // Basic path traversal protection
    let mut p = PathBuf::from(base);
    for seg in rest.split('/') {
        if seg.is_empty() || seg == "." || seg == ".." { continue; }
        p.push(seg);
    }
    p
}

async fn serve_file(path: PathBuf) -> Response {
    if !path.exists() || !path.is_file() {
        return (StatusCode::NOT_FOUND, "").into_response();
    }
    match tokio::fs::read(&path).await {
        Ok(bytes) => {
            let mime = mime_guess::from_path(&path).first_or_octet_stream();
            let mut headers = HeaderMap::new();
            headers.insert(header::CONTENT_TYPE, header::HeaderValue::from_str(mime.as_ref()).unwrap());
            (StatusCode::OK, headers, bytes).into_response()
        }
        Err(_) => (StatusCode::INTERNAL_SERVER_ERROR, "").into_response(),
    }
}