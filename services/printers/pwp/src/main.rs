mod components;

use axum::{Router, response::Html, routing::get};
use tower_http::services::ServeDir;

async fn home() -> Html<String> {
    Html(components::page("hello world").into_string())
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(home))
        .nest_service("/static", ServeDir::new("static"));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:80").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
