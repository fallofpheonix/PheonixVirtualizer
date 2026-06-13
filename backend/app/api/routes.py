from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import uuid
import os
from ..core.orchestrator import Orchestrator
from ..models.types import NormalizedGraph, NodeKind
from ..services.ai_reasoning import ai_reasoning_service

router = APIRouter()

# In-memory storage for jobs (for MVP, should be replaced by DB/Redis)
jobs: Dict[str, Dict[str, Any]] = {}

@router.post("/analyze")
async def analyze_repository(path: str, background_tasks: BackgroundTasks):
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="Path does not exist")
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "processing",
        "projectName": os.path.basename(path),
        "path": path,
        "graph": None,
        "errors": []
    }
    
    background_tasks.add_task(_run_analysis, job_id, path)
    
    return {"jobId": job_id, "status": "processing"}

async def _run_analysis(job_id: str, path: str):
    try:
        orchestrator = Orchestrator(path)
        graph = orchestrator.analyze()
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["graph"] = graph
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["errors"].append(str(e))

@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return {
        "jobId": job_id,
        "status": job["status"],
        "projectName": job["projectName"],
        "errors": job["errors"]
    }

@router.get("/job/{job_id}/macro")
async def get_macro_graph(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=404, detail="Graph not found or processing")

    full_graph: NormalizedGraph = jobs[job_id]["graph"]
    
    # Filter nodes to high-level only (LOD 0)
    allowed_kinds = {NodeKind.PROJECT, NodeKind.FOLDER, NodeKind.FILE}
    macro_nodes = [n for n in full_graph.nodes if n.kind in allowed_kinds]
    macro_node_ids = {n.id for n in macro_nodes}

    macro_edges = [
        e for e in full_graph.edges 
        if e.source in macro_node_ids and e.target in macro_node_ids
    ]

    return {
        "nodes": macro_nodes,
        "edges": macro_edges
    }

@router.get("/job/{job_id}/micro/{file_id}")
async def get_micro_graph(job_id: str, file_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=404, detail="Graph not found")

    full_graph: NormalizedGraph = jobs[job_id]["graph"]

    # Filter for nodes inside the specific file (LOD 1)
    micro_nodes = [n for n in full_graph.nodes if n.parentId == file_id]
    micro_node_ids = {n.id for n in micro_nodes}

    micro_edges = [
        e for e in full_graph.edges 
        if e.source in micro_node_ids or e.target in micro_node_ids
    ]

    return {
        "nodes": micro_nodes,
        "edges": micro_edges
    }

@router.post("/job/{job_id}/analyze-violation/{violation_id}")
async def analyze_violation_with_ai(job_id: str, violation_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=404, detail="Job not found or processing")

    full_graph: NormalizedGraph = jobs[job_id]["graph"]
    
    # Find the violation
    violation = next((v for v in full_graph.violations if v.id == violation_id), None)
    if not violation:
        # Fallback: check if the provided ID is actually a node ID involved in a violation
        violation = next((v for v in full_graph.violations if violation_id in v.sourceNodeIds), None)
    
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found for this identifier")

    # Find affected nodes
    affected_nodes = [n for n in full_graph.nodes if n.id in violation.sourceNodeIds]
    
    # Get project root from job if available, or fallback to current dir
    project_root = jobs[job_id].get("path", os.getcwd())
    
    analysis = await ai_reasoning_service.analyze_violation(violation, affected_nodes, project_root)
    
    return {"analysis": analysis}

@router.post("/job/{job_id}/snapshot")
async def create_snapshot(job_id: str):
    if job_id not in jobs or jobs[job_id]["status"] != "complete":
        raise HTTPException(status_code=404, detail="Job not found or processing")
    
    from ..core.database import Database
    db = Database()
    project_id = "default-project"
    graph = jobs[job_id]["graph"]
    
    snapshot_id = db.create_snapshot(project_id, graph)
    return {"snapshotId": snapshot_id, "status": "captured"}

@router.get("/job/{job_id}/trends")
async def get_trends(job_id: str):
    # Trends are project-wide, so we use the project_id
    from ..core.database import Database
    db = Database()
    project_id = "default-project"
    
    snapshots = db.get_snapshots(project_id)
    return {"snapshots": snapshots}
