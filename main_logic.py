import collections
import os
import re
from typing import OrderedDict

import fastapi
import uvicorn
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from markdown import markdown

import page_makers
from dataclasses_ import ArticleInfo, FileInfo

app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

ARTICLES_FOLDER_NAME = "articles"
# noinspection RegExpAnonymousGroup
HEADER_REGEX = re.compile("#{1,5} (.+)\n")


# noinspection PyShadowingNames
def get_articles() -> OrderedDict[str, ArticleInfo]:
    article_files_info = []
    for filename in os.listdir(ARTICLES_FOLDER_NAME):
        if os.path.splitext(filename)[1] == ".md":
            path = os.path.join(ARTICLES_FOLDER_NAME, filename)
            file_info = os.stat(path)
            article_files_info.append(
                FileInfo(filename, path, file_info.st_ctime, file_info.st_mtime)
            )
    article_files_info.sort(key=lambda file_info: file_info.creation_time)
    # noinspection PyShadowingNames
    articles = collections.OrderedDict()
    for file_info in article_files_info:
        article_text = open(file_info.path, "r", encoding="utf-8").read()
        title = HEADER_REGEX.match(article_text)
        if title:
            title = title.group(1)
        else:
            raise ValueError(f"No title found in article {file_info.filename}!")
        articles[file_info.filename] = ArticleInfo(
            title,
            page_makers.add_ending_signature(
                page_makers.make_prettier(markdown(article_text), title),
                file_info.creation_time, file_info.modification_time
            )
        )
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
