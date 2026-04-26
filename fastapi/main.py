from fastapi import FastAPI
import asyncio
from dotenv import load_dotenv
import os

from app.models import HealthCheckRequest, BackupRequest
from app.netmiko_service import health_check, backup_config

load_dotenv()

app = FastAPI(title=os.getenv("APP_NAME", "Network Automation API"))


@app.get("/")
def home():
    return {"message": "Network Automation API is running"}


@app.post("/health-check")
async def health_check_api(request: HealthCheckRequest):
    tasks = [
        asyncio.to_thread(health_check, device.model_dump())
        for device in request.devices
    ]

    results = await asyncio.gather(*tasks)

    return {"results": results}


@app.post("/backup")
async def backup_api(request: BackupRequest):
    tasks = [
        asyncio.to_thread(backup_config, device.model_dump())
        for device in request.devices
    ]

    results = await asyncio.gather(*tasks)

    return {"results": results}
