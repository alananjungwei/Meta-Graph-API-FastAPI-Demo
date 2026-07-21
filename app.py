from fastapi import FastAPI

from routes.graph import router as graph_router

from routes.facebook import router as facebook_router

from routes import messenger

app = FastAPI(
    title="Meta Graph API FastAPI Demo",
    description="Learning Meta Graph API, FastAPI and Webhooks",
    version="0.1.0",
)

app.include_router(graph_router)
app.include_router(facebook_router)
app.include_router(messenger.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Meta Graph API Demo!"
    }