from pony.orm import db_session

from models import Article


def make_prettier(
        html: str, title: str, font: str = "sans-serif",
        make_github_style_headers: bool = True) -> str:
    return (
        (
            (
                '<style>h1:after, h2:after {content: ""; display: block; '
                'position: relative; top: .33em; '
                'border-bottom: 1px solid hsla(0,0%,50%,.33);}</style>'
            ) if make_github_style_headers else ""
        ) +
        f'<title>{title}</title>'
        f'<body style="font-family: {font}">{html}</body>'
    )


def make_main_page() -> str:
    with db_session:
        return make_prettier(
            (
                '<p align="center"><img src="site_title.png" width="98%" '
                'style="image-rendering: pixelated; padding: 1%;" />'
                '<h1>Articles:</h1>'
                '<ul>' +
                "".join(
                    f'<li><a href="articles/{article.id}">'
                    f'{article.title}</a></li>'
                    for article in Article.select()
                ) +
                '</ul>'
            ),
            title="megahomyak’s site",
            make_github_style_headers=False
        )
