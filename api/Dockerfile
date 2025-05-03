FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    CONDA_AUTO_UPDATE_CONDA=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    git \
    build-essential \
    python3-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-py311_23.9.0-0-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Add conda to PATH
ENV PATH=/opt/conda/bin:$PATH

# Copy only the requirements file first to leverage Docker cache
WORKDIR /app
COPY api/requirements.txt /app/api/requirements.txt
COPY requirements.txt /app/requirements.txt

# Create and activate conda environment
RUN conda create -n unirig python=3.11 -y
SHELL ["/bin/bash", "-c"]

# Install UniRig dependencies
RUN source /opt/conda/bin/activate unirig && \
    pip install -r /app/requirements.txt && \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118 && \
    pip install spconv-cu118 && \
    pip install torch_scatter torch_cluster -f https://data.pyg.org/whl/torch-2.3.0+cu118.html --no-cache-dir && \
    pip install numpy==1.26.4 && \
    pip install -r /app/api/requirements.txt

# Copy the entire repository
COPY . /app

# Create necessary directories for API
RUN mkdir -p /app/api/uploads /app/api/outputs /app/api/tmp

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
source /opt/conda/bin/activate unirig\n\
cd /app/api\n\
exec python run.py "$@"\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set the working directory to the API folder
WORKDIR /app/api

# Expose the API port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command (can be overridden)
CMD ["--host", "0.0.0.0", "--port", "8000"] 