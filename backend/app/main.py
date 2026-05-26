from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from .api.routes import router
from .api.websocket import manager
from .core.watcher import LiveWatcher
from .core.orchestrator import Orchestrator

app = FastAPI(title="PheonixVirtualization API")

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
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "PheonixVirtualization API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
