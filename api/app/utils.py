import os
import shutil
import subprocess
from pathlib import Path
import uuid
from typing import Dict, List, Optional, Tuple
from fastapi import UploadFile, WebSocket

from app.config import UPLOAD_DIR, OUTPUT_DIR, TMP_DIR

# Dictionary to store active jobs
active_jobs: Dict[str, dict] = {}
# Dictionary to store WebSocket connections
active_connections: Dict[str, List] = {}

def save_upload_file(upload_file: UploadFile) -> Tuple[str, Path]:
    """Save an uploaded file to the uploads directory"""
    filename = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    
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

def convert_to_glb(input_file: Path) -> Path:
    """
    Convert a 3D model to GLB format for web viewing
    Returns the path to the GLB file
    """
    original_ext = input_file.suffix.lower()
    
    # If already GLB, return as is
    if original_ext == '.glb':
        return input_file
        
    # Output GLB file path
    glb_output = input_file.with_suffix('.glb')
    
    # For FBX files, use Blender to convert
    if original_ext in ['.fbx', '.obj', '.gltf']:
        # Create a temporary Blender Python script for conversion
        script_path = TMP_DIR / f"{uuid.uuid4()}_convert.py"
        with open(script_path, 'w') as f:
            f.write(f"""
import bpy
import os

# Clear default scene
bpy.ops.wm.read_homefile(use_empty=True)

# Import the model
if '{original_ext}' == '.fbx':
    bpy.ops.import_scene.fbx(filepath='{input_file}')
elif '{original_ext}' == '.obj':
    bpy.ops.import_scene.obj(filepath='{input_file}')
elif '{original_ext}' == '.gltf':
    bpy.ops.import_scene.gltf(filepath='{input_file}')

# Export as GLB
bpy.ops.export_scene.gltf(
    filepath='{glb_output}',
    export_format='GLB',
    export_animations=True,
    export_skins=True
)
""")
        
        # Run Blender headless to convert
        blender_cmd = [
            "blender", "--background", "--python", str(script_path)
        ]
        success, output = run_command(blender_cmd)
        
        # Clean up script
        os.remove(script_path)
        
        if success and glb_output.exists():
            return glb_output
    
    # If conversion failed or unsupported format, return original
    return input_file 