use axum::{http::HeaderMap, response::{IntoResponse, Response}, Json, Extension};
use hmac::{Hmac, Mac};
use serde_json::{json, Value};
use sha2::Sha256;

use crate::{error, loader, AppState};

fn header_str<'a>(headers: &'a HeaderMap, key: &str) -> Option<&'a str> {
    headers.get(key).and_then(|v| v.to_str().ok())
}

fn calc_sign_hex(secret: &str, app_id: &str, timestamp: &str, body: &[u8]) -> String {
    let mut mac = Hmac::<Sha256>::new_from_slice(secret.as_bytes()).expect("HMAC can take key of any size");
    let mut msg = Vec::with_capacity(app_id.len() + timestamp.len() + body.len());
    msg.extend_from_slice(app_id.as_bytes());
    msg.extend_from_slice(timestamp.as_bytes());
    msg.extend_from_slice(body);
    mac.update(&msg);
    let res = mac.finalize().into_bytes();
    hex::encode(res)
}

async fn validate_main(headers: &HeaderMap, body: &[u8], state: &AppState) -> Result<(String, Option<String>), Response> {
    let app_id = header_str(headers, "X-HighOrder-Application-Id").ok_or_else(|| error::client_invalid("sign not correct."))?;
    let sign = header_str(headers, "X-HighOrder-Sign").ok_or_else(|| error::client_invalid("sign not correct."))?;
    let parts: Vec<&str> = sign.splitn(3, ',').collect();
    if parts.len() != 3 { return Err(error::client_invalid("sign not correct.")); }
    let hex_sign = parts[0];
    let timestamp = parts[1];
    let client_key = parts[2];

    let summary = loader::load_app_summary(app_id, &state.data_dir)
        .await
        .map_err(|_| error::client_invalid("sign not correct."))?;
    let summary = summary.ok_or_else(|| error::client_invalid("sign not correct."))?;
    let client_secret = summary.client_keys.iter().find(|k| k.client_key == client_key).map(|k| k.client_secret.clone())
        .ok_or_else(|| error::client_invalid("sign not correct."))?;

    let calc = calc_sign_hex(&client_secret, app_id, timestamp, body);
    if calc != hex_sign { return Err(error::client_invalid("sign not correct.")); }

    let session_token = header_str(headers, "X-HighOrder-Session-Token").map(|s| s.to_string());
    Ok((app_id.to_string(), session_token))
}

async fn validate_setup(headers: &HeaderMap, body: &[u8], state: &AppState) -> Result<String, Response> {
    // Reuse the same signature validation as main; returns app_id on success.
    let (app_id, _session_token) = validate_main(headers, body, state).await?;
    Ok(app_id)
}

pub async fn hola_main(Extension(state): Extension<AppState>, headers: HeaderMap, body: axum::body::Bytes) -> Response {
    let body_bytes = body.to_vec();
    let (_app_id, _session_token) = match validate_main(&headers, &body_bytes, &state).await {
        Ok(v) => v,
        Err(err) => return err,
    };

    let _data: Value = match serde_json::from_slice(&body_bytes) {
        Ok(v) => v,
        Err(_) => json!({}),
    };

    // TODO: integrate HolaService pipeline. For now, return empty commands list.
    let resp = json!({
        "ok": true,
        "data": { "commands": [] }
    });
    Json(resp).into_response()
}

pub async fn hola_setup(Extension(state): Extension<AppState>, headers: HeaderMap, body: axum::body::Bytes) -> Response {
    let body_bytes = body.to_vec();
    if let Err(err) = validate_setup(&headers, &body_bytes, &state).await { return err; }
    let _data: Value = serde_json::from_slice(&body_bytes).unwrap_or_else(|_| json!({}));
    let resp = json!({ "ok": true, "data": {} });
    Json(resp).into_response()
}

pub async fn hola_lite(Extension(_state): Extension<AppState>, headers: HeaderMap, body: axum::body::Bytes) -> Response {
    let _app_id = match header_str(&headers, "X-HighOrder-Application-Id") {
        Some(v) => v.to_string(),
        None => return error::client_invalid("missing app id"),
    };
    let _session_token = header_str(&headers, "X-HighOrder-Session-Token").map(|s| s.to_string());
    let _data: Value = serde_json::from_slice(&body).unwrap_or_else(|_| json!({}));
    let resp = json!({ "ok": true, "data": { "commands": [] } });
    Json(resp).into_response()
}
