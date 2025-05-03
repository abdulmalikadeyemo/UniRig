# UniRig API

A FastAPI-based REST API for the UniRig 3D model rigging framework.

## Overview

This API provides a simple web interface to the UniRig system, allowing for:
- Uploading 3D models for automatic rigging
- Real-time status updates during processing
- Downloading rigged models

The API handles the complete pipeline from skeleton prediction to skinning weight prediction and final merging, all in a single endpoint with WebSocket updates.

## Installation

1. Make sure you have UniRig set up and working with its dependencies.

2. Install additional API dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running with Python

The simplest way to run the API server is using the Python script:

```bash
# Basic usage
python run.py

# With options
python run.py --host 127.0.0.1 --port 8000 --reload --debug
```

Command line options:
- `--host`: Hostname to bind to (default: 0.0.0.0)
- `--port`: Port to listen on (default: 8000)
- `--reload`: Enable auto-reload for development
- `--debug`: Enable debug mode

### Using Docker

For deployment, a Dockerfile is provided:

```bash
# Build the Docker image
docker build -t unirig-api -f api/Dockerfile .

# Run the container (with GPU support)
docker run --gpus all -p 8000:8000 unirig-api

# Or with custom parameters
docker run --gpus all -p 9000:9000 unirig-api --host 0.0.0.0 --port 9000
```

Make sure your Docker installation supports NVIDIA GPU passthrough.

## Client Usage

### Web Interface

Access the web interface at:
```
http://localhost:8000
```

### Programmatically

```python
import requests
import websocket
import json

# Upload a model
files = {'model_file': open('model.glb', 'rb')}
response = requests.post('http://localhost:8000/api/rig', files=files)
job_id = response.json()['job_id']

# Connect to WebSocket for updates
ws = websocket.WebSocketApp(
    f"ws://localhost:8000/api/ws/{job_id}",
    on_message=lambda ws, msg: print(json.loads(msg))
)
ws.run_forever()

# Download the result when complete
with open('rigged_model.glb', 'wb') as f:
    f.write(requests.get(f'http://localhost:8000/api/download/{output_file}').content)
```

## API Endpoints

### POST /api/rig
Upload a 3D model to start the rigging process.

**Request:**
- Form data with `model_file` (supported formats: .obj, .fbx, .glb, .gltf, .vrm)

**Response:**
```json
{
  "job_id": "uuid-string",
  "message": "Processing started",
  "websocket_url": "/api/ws/uuid-string"
}
```

### WebSocket /api/ws/{job_id}
Connect to this WebSocket to receive real-time updates on the processing status.

**Updates format:**
```json
{
  "job_id": "uuid-string",
  "status": "pending|skeleton_started|skeleton_completed|skinning_started|skinning_completed|merge_started|completed|failed",
  "message": "Status message",
  "output_file": "filename.ext"
}
```

### GET /api/download/{filename}
Download a processed file.

## Development

- The API is built with FastAPI
- WebSocket connections provide real-time status updates
- Background tasks are used for processing to avoid blocking the main thread 