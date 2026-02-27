use axum::response::Html;

use crate::components::{self, print_form};

pub async fn route() -> Html<String> {
    Html(components::page(print_form::home_page()).into_string())
}
