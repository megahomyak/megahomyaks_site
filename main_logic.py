import os

import fastapi
import uvicorn
from fastapi.responses import HTMLResponse, Response, PlainTextResponse
from pony.orm import db_session, ObjectNotFound

import models
import page_makers

app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

preloaded_files = {
    filename: open(filename, "rb").read()
    for filename in ("favicon.ico", "site_title.png")
}


@app.get("/")
async def get_main_page():
    return HTMLResponse(page_makers.make_main_page())


@app.get("/{filename}")
async def get_preloaded_file(filename: str):
    file_contents = preloaded_files.get(filename)
    if file_contents:
        return Response(file_contents)
    else:
        return PlainTextResponse(
            f"File {filename} not found in preloaded files!"
        )


@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    try:
        article_id = int(article_id)
    except ValueError:
        return PlainTextResponse(
            f'Article ID ("{article_id}") is not an integer!'
        )
    else:
        with db_session:
            try:
                return HTMLResponse(models.Article[article_id].html)
            except ObjectNotFound:
                return PlainTextResponse(
                    f"Article with ID {article_id} not found!"
                )


@app.get("/files/{filename}")
async def get_file(filename: str):
    try:
        with open(os.path.join("files", filename), "rb") as f:
            return Response(f.read())
    except FileNotFoundError:
        return PlainTextResponse(f"File {filename} not found!")


uvicorn.run(app, log_level="warning")
