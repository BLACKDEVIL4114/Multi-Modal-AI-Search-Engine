# Use Python 3.9 as base (stable for torch/transformers)
FROM python:3.9-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for FAISS and Image processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirement file first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/images embeddings

# Expose ports for both APIs
# 8501: Streamlit
# 8000: FastAPI
EXPOSE 8501 8000

# Default command: Start the FastAPI backend
# Use -m to run as module if needed, otherwise direct path
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
