import os
import shutil
import subprocess
from pathlib import Path
import uuid
from typing import Dict, List, Optional, Tuple

from app.config import UPLOAD_DIR, OUTPUT_DIR, TMP_DIR

# Dictionary to store active jobs
active_jobs: Dict[str, dict] = {}
# Dictionary to store WebSocket connections
active_connections: Dict[str, List] = {}

def save_upload_file(upload_file) -> Tuple[str, Path]:
    """Save uploaded file and return filename and path"""
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return filename, file_path

def run_command(cmd: List[str]) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            text=True, 
            capture_output=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed: {e.stderr}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_output_path(filename: str) -> Path:
    """Get path for output file"""
    return OUTPUT_DIR / filename

def cleanup_tmp_files(job_id: str):
    """Clean up temporary files after processing"""
    tmp_job_dir = TMP_DIR / job_id
    if tmp_job_dir.exists():
        shutil.rmtree(tmp_job_dir) 