import os
import re
from typing import List, Dict

import fastapi
import uvicorn
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from markdown import markdown

import page_makers
from dataclasses_ import ArticlePathInfo, ArticleInfo

app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

ARTICLES_FOLDER_NAME = "articles"
# noinspection RegExpAnonymousGroup
HEADER_REGEX = re.compile("#{1,5} (.+)\n")


# noinspection PyShadowingNames
def get_articles_paths_sorted():
    article_filenames = []
    for filename in os.listdir(ARTICLES_FOLDER_NAME):
        if os.path.splitext(filename)[1] == ".md":
            article_filenames.append(ArticlePathInfo(
                os.path.join(ARTICLES_FOLDER_NAME, filename), filename
            ))
    article_filenames.sort(
        key=lambda article_path_info: os.path.getctime(article_path_info.path)
    )
    return article_filenames


def get_article_title(article_text):
    title = HEADER_REGEX.match(article_text)
    if title:
        return title.group(1)
    else:
        raise ValueError("No title found in article!")


# noinspection PyShadowingNames
def get_articles_dict_and_articles_info(article_paths: List[ArticlePathInfo]):
    articles_dict: Dict[str, str] = {}  # Filenames -> Contents
    articles_info: List[ArticleInfo] = []  # Paths & Titles
    for path in article_paths:
        article_text = open(path.path, "r", encoding="utf-8").read()
        articles_info.append(
            ArticleInfo(path.path, get_article_title(article_text))
        )
        articles_dict[path.filename] = markdown(article_text)
    return articles_dict, articles_info


preloaded_files = {
    filename: open(filename, "rb").read()
    for filename in ("favicon.ico", "site_title.png")
}

articles, articles_info = get_articles_dict_and_articles_info(
    get_articles_paths_sorted()
)


@app.get("/")
async def get_main_page():
    return HTMLResponse(page_makers.make_main_page(articles_info))


@app.get("/{filename}")
async def get_preloaded_file(filename: str):
    file_contents = preloaded_files.get(filename)
    if file_contents:
        return Response(file_contents)
    else:
        return PlainTextResponse(
            f"File {filename} not found in preloaded files!"
        )


@app.get(f"/{ARTICLES_FOLDER_NAME}/{{article_filename}}")
async def get_article(article_filename: str):
    article = articles.get(article_filename)
    if article:
        return HTMLResponse(article)
    else:
        return PlainTextResponse(
            f'Article with filename "{article_filename}" not found!'
        )


@app.get("/files/{filename}")
async def get_file(filename: str):
    try:
        with open(os.path.join("files", filename), "rb") as f:
            return Response(f.read())
    except FileNotFoundError:
        return PlainTextResponse(f"File {filename} not found!")


uvicorn.run(app, log_level="warning")
