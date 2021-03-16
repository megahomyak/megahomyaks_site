import datetime
from typing import OrderedDict

from dataclasses_ import ArticleInfo


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


def make_main_page(articles_info: OrderedDict[str, ArticleInfo]) -> str:
    return make_prettier(
        (
            '<p align="center"><img src="site_title.png" width="98%" '
            'style="image-rendering: pixelated; padding: 1%;" />'
            '<h1>Articles:</h1>'
            '<ul>' +
            "".join(
                f'<li><a href="{article_filename}">'
                f'{article_info.title}</a></li>'
                for article_filename, article_info in articles_info.items()
            ) +
            '</ul>'
        ),
        title="megahomyak’s site",
        make_github_style_headers=False
    )


def get_date_with_dots(date: datetime.date) -> str:
    return date.strftime("%d.%m.%Y")


def add_ending_signature(
        html: str, creation_time: float, modification_time: float,
        nickname: str = "megahomyak") -> str:
    creation_date = datetime.datetime.fromtimestamp(creation_time).date()
    modification_date = datetime.datetime.fromtimestamp(
        modification_time
    ).date()
    modification_date_text = (
        f" (last modification done in {get_date_with_dots(modification_date)})"
    ) if creation_date != modification_date else ""
    return (
        f'{html}<i><p style="text-align: right;">- {nickname}, '
        f'{get_date_with_dots(creation_date)}{modification_date_text}</p></i>'
    )
