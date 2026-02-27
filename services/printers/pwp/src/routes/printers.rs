use axum::response::Html;

use crate::components::print_form;

pub async fn route() -> Html<String> {
    let markup = match cups_rs::get_all_destinations() {
        Ok(printers) if !printers.is_empty() => {
            let printers = printers.into_iter().map(|printer| printer.name).collect::<Vec<_>>();
            print_form::printer_fieldset(&printers)
        }
        Ok(_) => print_form::message("No printers found."),
        Err(error) => print_form::message(&error.to_string()),
    };

    Html(markup.into_string())
}
