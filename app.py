from fastapi import FastAPI
from routes.graph import router as graph_router
from routes.facebook import router as facebook_router
from routes import messenger
from services.database_service import initialize_database
from routes.analytics import router as analytics_router

app = FastAPI(
    title="Meta Graph API FastAPI Demo",
    description="Learning Meta Graph API, FastAPI and Webhooks",
    version="0.1.0",
)

initialize_database()

app.include_router(graph_router)
app.include_router(facebook_router)
app.include_router(messenger.router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Meta Graph API Demo!"
    }