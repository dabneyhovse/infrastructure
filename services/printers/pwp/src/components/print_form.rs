use maud::{Markup, html};

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
