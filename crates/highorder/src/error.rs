use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use serde::Serialize;

#[derive(Serialize)]
struct ErrorBody<'a> {
    ok: bool,
    error_type: &'a str,
    error_msg: &'a str,
}

fn json_error(status: StatusCode, error_type: &str, error_msg: &str) -> Response {
    let body = ErrorBody { ok: false, error_type, error_msg };
    (status, Json(body)).into_response()
}

pub fn bad_request(error_type: &str, error_msg: &str) -> Response {
    json_error(StatusCode::BAD_REQUEST, error_type, error_msg)
}

pub fn server_error(error_type: &str, error_msg: &str) -> Response {
    json_error(StatusCode::INTERNAL_SERVER_ERROR, error_type, error_msg)
}

pub fn client_invalid(msg: &str) -> Response {
    bad_request("ClientInvalid", msg)
}

pub fn client_unauthorized(msg: &str) -> Response {
    (StatusCode::UNAUTHORIZED, Json(ErrorBody { ok: false, error_type: "AuthorizeRequired", error_msg: msg })).into_response()
}

pub fn client_forbidden(msg: &str) -> Response {
    (StatusCode::FORBIDDEN, Json(ErrorBody { ok: false, error_type: "Forbidden", error_msg: msg })).into_response()
}

pub fn session_invalid(msg: &str) -> Response {
    bad_request("SessionInvalid", if msg.is_empty() { "session invalid or expired" } else { msg })
}
