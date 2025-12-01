from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import router

app = FastAPI(title="Agent Sangam Web App")

# Mount static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include modular routes
app.include_router(router)
