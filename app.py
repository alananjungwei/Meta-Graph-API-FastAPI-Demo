from fastapi import FastAPI

app = FastAPI(
    title="Meta Graph API FastAPI Demo",
    description="Learning Meta Graph API, FastAPI and Webhooks",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the Meta Graph API Demo!"
    }