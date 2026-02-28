use axum::response::Html;

use crate::components::print_form;

pub async fn route() -> Html<String> {
    let markup = match cups_rs::get_all_destinations() {
        Ok(printers) if !printers.is_empty() => {
            let printers = printers
                .into_iter()
                .map(|printer| printer.name)
                .collect::<Vec<_>>();
            print_form::printer_select(&printers)
        }
        Ok(_) => print_form::error_alert("No printers found."),
        Err(error) => print_form::error_alert(&format!("Failed to load printers: {error}")),
    };

    Html(markup.into_string())
}
