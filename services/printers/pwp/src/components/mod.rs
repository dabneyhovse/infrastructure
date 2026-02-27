use maud::{DOCTYPE, Markup, Render, html};

pub fn header() -> Markup {
    html! {
        .header {
            h1 {
                "pepsi's web print"
            }
        }
    }
}

pub fn page(body: impl Render) -> Markup {
    html! {
        (DOCTYPE)
        html {
            head {
                script src="/static/vendor/htmx.min.js" {}
                script src="/static/vendor/oat.min.js" {}
                link rel="stylesheet" href="/static/vendor/oat.min.css" {}
                link rel="stylesheet" href="/static/style.css" {}
            }
            body {
                (header())
                (body)
            }
        }
    }
}
