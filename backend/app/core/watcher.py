import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .orchestrator import Orchestrator
from ..api.websocket import manager
import asyncio

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, orchestrator: Orchestrator, loop: asyncio.AbstractEventLoop):
        self.orchestrator = orchestrator
        self.loop = loop
        self.last_run = 0
        self.debounce_seconds = 1

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Debounce and filter extensions
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in {'.py', '.js', '.ts', '.tsx'}:
            return
            
        current_time = time.time()
        if current_time - self.last_run < self.debounce_seconds:
            return
            
        self.last_run = current_time
        print(f"File modified: {event.src_path}. Re-analyzing...")
        
        # We need to run the analysis and broadcast the update
        # Since this is called from the watchdog thread, we use run_coroutine_threadsafe
        asyncio.run_coroutine_threadsafe(self._reanalyze_and_broadcast(), self.loop)

    async def _reanalyze_and_broadcast(self):
        try:
            # For MVP, we run a full analyze, but we've already optimized orchestrator 
            # with multiprocessing, so it's relatively fast.
            # Future improvement: partial re-parse.
            graph = self.orchestrator.analyze()
            await manager.broadcast({
                "type": "GRAPH_UPDATE",
                "data": graph.model_dump()
            })
        except Exception as e:
            print(f"Error during live update: {e}")

class LiveWatcher:
    def __init__(self, project_root: str, orchestrator: Orchestrator):
        self.project_root = project_root
        self.orchestrator = orchestrator
        self.observer = Observer()

    def start(self, loop: asyncio.AbstractEventLoop):
        handler = ChangeHandler(self.orchestrator, loop)
        self.observer.schedule(handler, self.project_root, recursive=True)
        self.observer.start()
        print(f"Live watcher started for: {self.project_root}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
