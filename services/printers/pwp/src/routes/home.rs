use axum::response::Html;
use maud::{Markup, PreEscaped, html};

use crate::components;

pub fn home_page() -> Markup {
    html! {
        main {
            form
                hx-post="/print"
                hx-target="#print-result"
                hx-swap="innerHTML"
                hx-encoding="multipart/form-data"
                enctype="multipart/form-data"
            {
                fieldset {
                    legend { "Print a file" }

                    label data-field {
                        input id="file" type="file" name="file" required onchange="previewFile(this)" {}
                    }

                    div id="file-preview" {}

                    fieldset class="group" {
                        div
                            id="printer-field"
                            class="w-100 flex items-center"
                            hx-get="/printers"
                            hx-trigger="load"
                            hx-target="this"
                            hx-swap="outerHTML"
                        {
                            div role="status" class="skeleton line printer-control" {}
                        }

                        button type="submit" class="printer-control" { "Print" }
                    }
                }
            }

            div id="print-result" {}
        }

        script {
            (PreEscaped(r#"
                let previewUrl;

                function previewFile(input) {
                    const preview = document.getElementById("file-preview");
                    const file = input && input.files && input.files[0];

                    preview.replaceChildren();

                    if (previewUrl) {
                        URL.revokeObjectURL(previewUrl);
                        previewUrl = null;
                    }

                    if (!file) {
                        return;
                    }

                    const object = document.createElement("object");
                    previewUrl = URL.createObjectURL(file);
                    object.data = previewUrl;
                    object.type = file.type;
                    object.width = "100%";
                    object.height = "500";
                    object.textContent = "Preview unavailable in this browser.";
                    preview.append(object);
                }

                function syncPreview() {
                    previewFile(document.getElementById("file"));
                }

                window.addEventListener("pageshow", syncPreview);
                syncPreview();
            "#))
        }
    }
}

pub async fn route() -> Html<String> {
    Html(components::page(home_page()).into_string())
}
