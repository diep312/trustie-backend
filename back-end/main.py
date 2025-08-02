from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import shutil
import os
from typing import Any
from .routes import phone, alerts, screenshot, user, family, reports, tts

app = FastAPI(title="Backend API của Trustie", version="1.0.1")

# Include routers
app.include_router(phone.router)
app.include_router(alerts.router)
app.include_router(screenshot.router)
app.include_router(user.router)
app.include_router(family.router)
app.include_router(reports.router)
app.include_router(tts.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
