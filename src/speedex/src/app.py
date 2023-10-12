from os import getenv
from uvicorn import Config, Server
from asyncio import run
from fastapi import FastAPI, HTTPException
from tracker import Tracker, Package
from dataclasses import dataclass, field
from typing import List, Dict

app = FastAPI()
tracker = Tracker()

@dataclass
class ResponseError:
    code: int
    message: str

@dataclass
class Response:
    success: bool
    data: List[Dict[str, Package]]
    error: ResponseError

@app.on_event("startup")
async def startup_event():
    await tracker.startup()

@app.on_event("shutdown")
async def shutdown_event():
    await tracker.shutdown()

@app.get("/track-one/{id}")
async def track_one(id: str):
    try:
        data = await tracker.track_one(id)
        return Response(success=True, data=data, error=ResponseError(code=200, message=""))
    except HTTPException as e:
        return Response(success=False, data=None, error=ResponseError(code=e.status_code, message=e.detail))

@app.get("/track-many/{ids}")
async def track_many(ids: str):
    try:    
        data = await tracker.track_many(ids.split("&")[:5])
        return Response(success=True, data=data, error=ResponseError(code=200, message=""))
    except HTTPException as e:
        return Response(success=False, data=None, error=ResponseError(code=e.status_code, message=e.detail))

async def main():
    PORT = getenv("PORT", 8000)
    config = Config("app:app", host="0.0.0.0", port=int(PORT), log_level="info")
    server = Server(config)
    await server.serve()

if __name__ == "__main__":
    run(main())