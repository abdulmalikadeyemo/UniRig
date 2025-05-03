import os
from typing import List, Dict
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import uuid

from app.models import Job, ProcessingStatus
from app.utils import save_upload_file, active_jobs, active_connections
from app.processing import process_model, send_status_update
from app.config import OUTPUT_DIR

app = FastAPI(title="UniRig API")

# Mount static files (for WebSocket testing UI)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/rig")
async def rig_model(
    background_tasks: BackgroundTasks,
    model_file: UploadFile = File(...)
):
    """
    Upload a 3D model and start the rigging process.
    Returns a job ID that can be used to track progress via WebSocket.
    """
    # Check file type
    allowed_extensions = [".obj", ".fbx", ".glb", ".gltf", ".vrm"]
    file_ext = os.path.splitext(model_file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"}
        )
    
    # Save uploaded file
    filename, file_path = save_upload_file(model_file)
    
    # Create job
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        input_filename=filename
    )
    active_jobs[job_id] = job
    
    # Start processing in background
    background_tasks.add_task(process_model, job_id, file_path)
    
    # Return job details
    return {
        "job_id": job_id,
        "message": "Processing started",
        "websocket_url": f"/api/ws/{job_id}"
    }

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a processed file"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@app.websocket("/api/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket connection for real-time status updates"""
    await websocket.accept()
    
    # Register connection
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)
    
    try:
        # Send current status if job exists
        if job_id in active_jobs:
            job = active_jobs[job_id]
            await websocket.send_json({
                "job_id": job_id,
                "status": job.status,
                "message": job.message,
                "output_file": job.output_filename
            })
        
        # Keep connection open
        while True:
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        # Remove connection when client disconnects
        if job_id in active_connections:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]

@app.get("/")
async def get_index():
    """Serve a simple WebSocket test UI"""
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 