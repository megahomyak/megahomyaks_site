import collections
import os
import re
from typing import OrderedDict

import fastapi
import uvicorn
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from markdown import markdown

import page_makers
from dataclasses_ import ArticleInfo

app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

ARTICLES_FOLDER_NAME = "articles"
# noinspection RegExpAnonymousGroup
HEADER_REGEX = re.compile("#{1,5} (.+)\n")


def get_articles() -> OrderedDict[str, ArticleInfo]:
    article_filenames_with_paths = [
        (filename, os.path.join(ARTICLES_FOLDER_NAME, filename))
        for filename in os.listdir(ARTICLES_FOLDER_NAME)
        if os.path.splitext(filename)[1] == ".md"
    ]
    article_filenames_with_paths.sort(
        key=lambda filename_with_path: os.path.getctime(
            filename_with_path[1]  # Path
        )
    )
    # noinspection PyShadowingNames
    articles = collections.OrderedDict()
    for filename, path in article_filenames_with_paths:
        article_text = open(path, "r", encoding="utf-8").read()
        title = HEADER_REGEX.match(article_text)
        if title:
            title = title.group(1)
        else:
            raise ValueError(f"No title found in article {filename}!")
        articles[filename] = ArticleInfo(title, markdown(article_text))
    return articles


preloaded_files = {
    filename: open(filename, "rb").read()
    for filename in ("favicon.ico", "site_title.png")
}

articles = get_articles()


@app.get("/")
async def get_main_page():
    return HTMLResponse(page_makers.make_main_page(articles))


@app.get("/{filename}")
async def get_file(filename: str):
    if os.path.splitext(filename)[1] == ".md":
        article = articles.get(filename)
        if article:
            return HTMLResponse(article.html)
        else:
            return PlainTextResponse(
                f'Article with filename "{filename}" not found!'
            )
    else:
        file_contents = preloaded_files.get(filename)
        if file_contents:
            return Response(file_contents)
        else:
            try:
                with open(
                    os.path.join(ARTICLES_FOLDER_NAME, filename), "rb"
                ) as f:
                    return Response(f.read())
            except FileNotFoundError:
                return PlainTextResponse(f"File {filename} not found!")


uvicorn.run(app, log_level="warning")
