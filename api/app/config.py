import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
UNIRIG_DIR = Path(__file__).resolve().parent.parent.parent

# Storage directories
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TMP_DIR = BASE_DIR / "tmp"

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# Script paths
SKELETON_SCRIPT = UNIRIG_DIR / "launch/inference/generate_skeleton.sh"
SKINNING_SCRIPT = UNIRIG_DIR / "launch/inference/generate_skin.sh"
MERGE_SCRIPT = UNIRIG_DIR / "launch/inference/merge.sh" 