import os
import re
from typing import Dict, Union

from aiohttp import web
from markdown import markdown

# noinspection RegExpAnonymousGroup
header_regex = re.compile("# (.+)\n")

article_titles_with_links = []
files: Dict[str, Union[bytes, str]] = {}


# noinspection PyShadowingNames
def add_file_to_files(filename: str) -> None:
    with open(filename, "rb") as f:
        files[filename] = f.read()


def make_title_and_font(html: str, title: str, font: str = "sans-serif") -> str:
    return (
        f'<meta property="og:title" content="{title}" />'
        f'<body style="font-family: {font}">{html}</html>'
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
        files[filename] = make_title_and_font(markdown(article), article_title)
    else:
        add_file_to_files(os.path.join("articles", filename))

for filename in ("site_title.png", "favicon.ico"):
    add_file_to_files(filename)

main_page_html = make_title_and_font(
    (
        '<br /><p align="center"><img src="site_title.png" width="90%" '
        'style="image-rendering: pixelated;" />'
        '<h1>Articles:</h1>'
        '<ul>' +
        "".join(
            f'<li><a href="{article_link}">{article_title}</a></li>'
            for article_title, article_link in article_titles_with_links
        ) +
        '</ul>'
    ),
    "megahomyak’s site"
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
