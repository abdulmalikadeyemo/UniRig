import asyncio
from pathlib import Path
import os
import uuid
from typing import Dict, List, Optional

from fastapi import WebSocket
from app.config import SKELETON_SCRIPT, SKINNING_SCRIPT, MERGE_SCRIPT, OUTPUT_DIR, TMP_DIR
from app.models import Job, ProcessingStatus, StatusUpdate
from app.utils import run_command, active_jobs, active_connections, cleanup_tmp_files, convert_to_glb

async def send_status_update(job_id: str, status: ProcessingStatus, message: str, output_file: Optional[str] = None):
    """Send status update to connected clients"""
    update = StatusUpdate(
        job_id=job_id,
        status=status,
        message=message,
        output_file=output_file
    )
    
    # Update job status
    if job_id in active_jobs:
        active_jobs[job_id].status = status
        active_jobs[job_id].message = message
        if output_file:
            if status == ProcessingStatus.SKELETON_COMPLETED:
                active_jobs[job_id].skeleton_filename = output_file
            elif status == ProcessingStatus.SKINNING_COMPLETED:
                active_jobs[job_id].skinned_filename = output_file
            elif status == ProcessingStatus.COMPLETED:
                active_jobs[job_id].output_filename = output_file
    
    # Send update to all connected clients
    if job_id in active_connections:
        for connection in active_connections[job_id]:
            try:
                await connection.send_json(update.dict())
            except Exception:
                # Connection might be closed
                pass

async def process_model(job_id: str, input_path: Path):
    """Process a 3D model through the full pipeline"""
    try:
        # Create temporary directory for this job
        job_tmp_dir = TMP_DIR / job_id
        os.makedirs(job_tmp_dir, exist_ok=True)
        
        # 1. Skeleton Prediction
        await send_status_update(job_id, ProcessingStatus.SKELETON_STARTED, "Generating skeleton...")
        
        skeleton_output = OUTPUT_DIR / f"{job_id}_skeleton.fbx"
        skeleton_cmd = [
            "bash", str(SKELETON_SCRIPT),
            "--input", str(input_path),
            "--output", str(skeleton_output)
        ]
        
        success, output = run_command(skeleton_cmd)
        if not success:
            await send_status_update(job_id, ProcessingStatus.FAILED, f"Skeleton generation failed: {output}")
            return
        
        await send_status_update(
            job_id, 
            ProcessingStatus.SKELETON_COMPLETED, 
            "Skeleton generated successfully",
            f"{job_id}_skeleton.fbx"
        )
        
        # 2. Skinning Prediction
        await send_status_update(job_id, ProcessingStatus.SKINNING_STARTED, "Generating skinning weights...")
        
        skinned_output = OUTPUT_DIR / f"{job_id}_skinned.fbx"
        skinning_cmd = [
            "bash", str(SKINNING_SCRIPT),
            "--input", str(skeleton_output),
            "--output", str(skinned_output)
        ]
        
        success, output = run_command(skinning_cmd)
        if not success:
            await send_status_update(job_id, ProcessingStatus.FAILED, f"Skinning generation failed: {output}")
            return
            
        await send_status_update(
            job_id, 
            ProcessingStatus.SKINNING_COMPLETED, 
            "Skinning weights generated successfully",
            f"{job_id}_skinned.fbx"
        )
        
        # 3. Merge Operation
        await send_status_update(job_id, ProcessingStatus.MERGE_STARTED, "Merging results...")
        
        output_ext = input_path.suffix
        final_output = OUTPUT_DIR / f"{job_id}_rigged{output_ext}"
        merge_cmd = [
            "bash", str(MERGE_SCRIPT),
            "--source", str(skinned_output),
            "--target", str(input_path),
            "--output", str(final_output)
        ]
        
        success, output = run_command(merge_cmd)
        if not success:
            await send_status_update(job_id, ProcessingStatus.FAILED, f"Merge operation failed: {output}")
            return
        
        # 4. Create web-friendly GLB version if needed
        web_output = final_output
        web_output_filename = f"{job_id}_rigged{output_ext}"
        
        # If not already GLB, convert to GLB format for web viewer
        if output_ext.lower() != '.glb':
            await send_status_update(job_id, ProcessingStatus.MERGE_STARTED, "Creating web-friendly version...")
            web_output = convert_to_glb(final_output)
            # If conversion was successful, update the output filename
            if web_output != final_output:
                web_output_filename = web_output.name
        
        await send_status_update(
            job_id, 
            ProcessingStatus.COMPLETED, 
            "Model rigged successfully",
            web_output_filename
        )
        
        # Clean up temporary files
        cleanup_tmp_files(job_id)
        
    except Exception as e:
        await send_status_update(job_id, ProcessingStatus.FAILED, f"Processing failed: {str(e)}") 