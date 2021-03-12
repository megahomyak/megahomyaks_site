import os
import re
from typing import Dict, Union

from aiohttp import web
from markdown import markdown

# noinspection RegExpAnonymousGroup
header_regex = re.compile("#{1,5} (.+)\n")

article_titles_with_links = []
files: Dict[str, Union[bytes, str]] = {}


# noinspection PyShadowingNames
def add_file_to_files(filename: str) -> None:
    with open(filename, "rb") as f:
        files[filename] = f.read()


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


for filename in sorted(
    os.listdir("articles"),
    key=lambda path: os.path.getctime(
        os.path.abspath(os.path.join("articles", path))
    )
):
    if os.path.splitext(filename)[1] == ".md":
        with open(
            os.path.join("articles", filename), "r", encoding="utf-8"
        ) as f:
            article = f.read()
        article_title = header_regex.match(article)
        if not article_title:
            raise ValueError("Article should start with header!")
        article_title = article_title.group(1)
        article_titles_with_links.append((article_title, filename))
        files[filename] = make_prettier(markdown(article), title=article_title)
    else:
        add_file_to_files(os.path.join("articles", filename))

for filename in ("site_title.png", "favicon.ico"):
    add_file_to_files(filename)

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
            files.get(
                filename,
                f"Article named '{filename}' isn't found!"  # Default
            )
        )
    else:
        file = files.get(filename)
        if file:
            return web.Response(body=file)
        else:
            return make_html_response("File named '{filename}' isn't found!")


app.add_routes(routes)

web.run_app(app)
