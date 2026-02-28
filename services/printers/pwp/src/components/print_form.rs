use maud::{Markup, html};

pub fn printer_select(printers: &[String]) -> Markup {
    html! {
        select id="printer" class="printer-control" name="printer" required {
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

pub fn error_alert(text: &str) -> Markup {
    html! {
        div role="alert" class="w-100 items-center printer-control" data-variant="error" {
            strong { "Error!" }
            " "
            (text)
        }
    }
}
