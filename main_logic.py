import fastapi
import uvicorn

app = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/")
async def get_main_page():
    return fastapi.Response()


uvicorn.run(app, log_level="warning")
