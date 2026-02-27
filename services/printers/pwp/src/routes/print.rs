use axum::response::Html;
use axum_typed_multipart::{FieldData, TryFromMultipart, TypedMultipart};
use tempfile::NamedTempFile;

use crate::components::print_form;

#[derive(TryFromMultipart)]
pub struct PrintForm {
    printer: String,
    file: FieldData<NamedTempFile>,
}

pub async fn route(TypedMultipart(form): TypedMultipart<PrintForm>) -> Html<String> {
    let destination = match cups_rs::get_destination(&form.printer) {
        Ok(destination) => destination,
        Err(error) => return Html(print_form::message(&error.to_string()).into_string()),
    };

    let title = form
        .file
        .metadata
        .file_name
        .clone()
        .unwrap_or_else(|| "Print job".to_owned());
    let content_type = form
        .file
        .metadata
        .content_type
        .map(|content_type| content_type.to_string())
        .unwrap_or_else(|| "application/octet-stream".to_owned());
    let path = form.file.contents.path().to_string_lossy().into_owned();

    let job = match cups_rs::create_job(&destination, &title) {
        Ok(job) => job,
        Err(error) => return Html(print_form::message(&error.to_string()).into_string()),
    };

    if let Err(error) = job.submit_file(&path, &content_type) {
        return Html(print_form::message(&error.to_string()).into_string());
    }

    if let Err(error) = job.close() {
        return Html(print_form::message(&error.to_string()).into_string());
    }

    Html(print_form::message("Print job submitted.").into_string())
}
