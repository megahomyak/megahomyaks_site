import datetime
import os
import re
from typing import Dict, Union

from aiohttp import web
from markdown import markdown

# noinspection RegExpAnonymousGroup
header_regex = re.compile("#{1,5} (.+)\n")

article_titles_with_links = []
preloaded_files: Dict[str, Union[bytes, str]] = {}


def get_date_with_dots(date: datetime.date) -> str:
    return date.strftime("%d.%m.%Y")


def add_ending_signature(
        html: str, creation_time: int, modification_time: int,
        nickname: str = "megahomyak") -> str:
    creation_date = datetime.datetime.fromtimestamp(creation_time).date()
    modification_date = datetime.datetime.fromtimestamp(
        modification_time
    ).date()
    modification_date_text = (
        f" (last edit in {get_date_with_dots(modification_date)})"
    ) if creation_date != modification_date else ""
    return (
        f'{html}<i><p style="text-align: right;">- {nickname}, '
        f'{get_date_with_dots(creation_date)}{modification_date_text}</p></i>'
    )


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


article_folder_files_names = os.listdir("articles")
article_filenames = []
for filename in article_folder_files_names:
    if os.path.splitext(filename)[1] == ".md":
        article_filenames.append(filename)

# noinspection PyShadowingNames
article_filenames.sort(
    key=lambda filename: os.path.getctime(os.path.join("articles", filename))
)

for filename in article_filenames:
    path_to_file = os.path.join("articles", filename)
    with open(path_to_file, "r", encoding="utf-8") as f:
        article = f.read()
    article_title = header_regex.match(article)
    if not article_title:
        raise ValueError("Article should start with header!")
    article_title = article_title.group(1)
    article_titles_with_links.append((article_title, filename))
    preloaded_files[filename] = add_ending_signature(
        make_prettier(markdown(article), title=article_title),
        int(os.path.getctime(path_to_file)), int(os.path.getmtime(path_to_file))
    )

for filename in ("site_title.png", "favicon.ico"):
    with open(filename, "rb") as f:
        preloaded_files[filename] = f.read()

main_page_html = make_prettier(
    (
        '<p align="center"><img src="site_title.png" width="98%" '
        'style="image-rendering: pixelated; padding: 1%;" />'
        '<h1>Articles:</h1>'
        '<ul>' +
        "".join(
            f'<li><a href="{article_link}">{article_title}</a></li>'
            for article_title, article_link in article_titles_with_links
        ) +
        '</ul>'
    ),
    title="megahomyak’s site",
    make_github_style_headers=False
)

app = web.Application()

routes = web.RouteTableDef()


def make_html_response(text: str) -> web.Response:
    return web.Response(
        text=text,
        content_type='text/html'
    )


@routes.get("/")
async def respond_with_main_page(_: web.Request) -> web.Response:
    return make_html_response(main_page_html)


@routes.get("/{filename}")
async def respond_with_article(request: web.Request) -> web.Response:
    # noinspection PyShadowingNames
    filename = request.match_info["filename"]
    if os.path.splitext(filename)[1] == ".md":
        return make_html_response(
            preloaded_files.get(
                filename,
                f"Article named '{filename}' isn't found!"  # Default
            )
        )
    else:
        file = preloaded_files.get(filename)
        if file:
            return web.Response(body=file)
        else:
            try:
                # noinspection PyShadowingNames
                with open(os.path.join("articles", filename), "rb") as f:
                    return web.Response(body=f.read())
            except FileNotFoundError:
                return make_html_response(
                    f"File named '{filename}' isn't found!"
                )


app.add_routes(routes)

web.run_app(app)
