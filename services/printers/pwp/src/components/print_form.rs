use maud::{Markup, PreEscaped, html};

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

                    input id="file" type="file" name="file" required onchange="previewFile(this)" {}

                    div id="file-preview" {}

                    div
                        id="printer-field"
                        hx-get="/printers"
                        hx-trigger="load"
                        hx-target="this"
                        hx-swap="innerHTML"
                    {
                        p { "Loading printers..." }
                    }

                    button type="submit" { "Print" }
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

pub fn printer_fieldset(printers: &[String]) -> Markup {
    html! {
        label for="printer" { "Printer" }
        select id="printer" name="printer" required {
            @for printer in printers {
                option value=(printer) { (printer) }
            }
        }
    }
}

pub fn message(text: &str) -> Markup {
    html! {
        output { (text) }
    }
}
