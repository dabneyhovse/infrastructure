mod components;
mod routes;

use axum::{Router, routing::{get, post}};
use std::env;
use tower_http::services::ServeDir;

#[tokio::main]
async fn main() {
    let cups_server = env::var("CUPS_SERVER").expect("CUPS_SERVER must be set");
    cups_rs::config::set_server(Some(&cups_server)).expect("CUPS_SERVER must be valid");

    let app = Router::new()
        .route("/", get(routes::home::route))
        .route("/printers", get(routes::printers::route))
        .route("/print", post(routes::print::route))
        .nest_service("/static", ServeDir::new("static"));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
