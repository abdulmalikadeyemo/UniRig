from pydantic import BaseModel
from enum import Enum
import uuid
from typing import Optional

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    SKELETON_STARTED = "skeleton_started"
    SKELETON_COMPLETED = "skeleton_completed"
    SKINNING_STARTED = "skinning_started"
    SKINNING_COMPLETED = "skinning_completed"
    MERGE_STARTED = "merge_started"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(BaseModel):
    id: str = str(uuid.uuid4())
    status: ProcessingStatus = ProcessingStatus.PENDING
    message: str = "Job created"
    input_filename: str
    skeleton_filename: Optional[str] = None
    skinned_filename: Optional[str] = None
    output_filename: Optional[str] = None
    error: Optional[str] = None

class StatusUpdate(BaseModel):
    job_id: str
    status: ProcessingStatus
    message: str
    output_file: Optional[str] = None 