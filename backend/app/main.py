from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from collections import defaultdict
import asyncio
import os
import time
from .api.routes import router
from .api.websocket import manager
from .core.watcher import LiveWatcher
from .core.orchestrator import Orchestrator

app = FastAPI(title="PheonixVirtualization API")

# Simple rate limiter: 100 requests per minute per IP
rate_limit_records = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Clean old records (older than 60s)
    rate_limit_records[client_ip] = [t for t in rate_limit_records[client_ip] if now - t < 60]
    
    if len(rate_limit_records[client_ip]) >= 100:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too Many Requests: Rate limit exceeded"}
        )
    
    rate_limit_records[client_ip].append(now)
    return await call_next(request)

# Security: API Key requirement
API_KEY = os.getenv("PHEONIX_API_KEY", "dev-key-12345")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

# Global instances for the watcher
watcher = None

@app.on_event("startup")
async def startup_event():
    global watcher
    # For now, we watch the current project root or a path from env
    project_root = os.getenv("PROJECT_ROOT", os.getcwd())
    orchestrator = Orchestrator(project_root)
    
    # Run initial analysis
    orchestrator.analyze()
    
    # Start the filesystem watcher
    loop = asyncio.get_event_loop()
    watcher = LiveWatcher(project_root, orchestrator)
    watcher.start(loop)

@app.on_event("shutdown")
async def shutdown_event():
    if watcher:
        watcher.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # For WebSockets, we can check a token in query params or headers
    # manager.connect already handled basic connection
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Security: CORS Hardening
# In development, restrict to Vite's default port.
# In production, this should be set via environment variable.
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Protect all API routes with the API Key dependency
app.include_router(router, prefix="/api", dependencies=[Depends(verify_api_key)])

@app.get("/")
async def root():
    return {"message": "PheonixVirtualization API is running", "status": "secure"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
