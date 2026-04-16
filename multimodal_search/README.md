# Multi-modal AI Search Engine
A complete search engine that allows finding similar images from a dataset using either text queries or image uploads.

## Features
- **Search by Text**: Enter descriptions like "a cat on the floor" to find matching images.
- **Search by Image**: Upload an image to find visually similar ones in the dataset.
- **REST API**: FastAPI layer for integration with external apps (POST /search/text, POST /search/image).
- **Docker Ready**: One-click deployment using Docker and Docker Compose.
- **High-Power Retrieval**: Uses FAISS with persistent `.index` files for industrial-scale speed.
- **GPU Acceleration**: Auto-detects CUDA for lightning-fast embedding generation.
- **Interactive UI**: Clean Streamlit interface with sidebar controls for result counts (Top-K).

## Tech Stack
| Category | Library/Technology |
| :--- | :--- |
| API Framework | `FastAPI`, `Uvicorn` |
| UI Framework | `Streamlit` |
| Containerization| `Docker`, `Docker Compose` |
| Deep Learning | `PyTorch`, `transformers` (CLIP) |
| Vector Search | `FAISS` |

## Folder Structure
```text
multimodal_search/
├── api/
│   └── main.py          # FastAPI Backend
├── app/
│   └── streamlit_app.py # Streamlit Frontend
├── pipeline/
│   └── build_index.py   # Embedding Generator
├── search/
│   └── search_core.py   # Core Logic
├── Dockerfile           # System Image
└── docker-compose.yml   # Multi-service Orchestration
```

## Setup Instructions

### Option 1: Using Docker (Recommended)
Launch the entire stack (API + UI) with one command:
```bash
docker-compose up --build
```
- UI: http://localhost:8501
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Option 2: Local Setup
1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```
2. **Generate Index**:
```bash
python pipeline/build_index.py
```
3. **Run Services**:
- **UI**: `streamlit run app/streamlit_app.py`
- **API**: `python api/main.py`

## API Usage Guide
- **Text Search**: `POST /search/text`
  - Body: `{"text": "a orange cat", "top_k": 5}`
- **Image Search**: `POST /search/image?top_k=5`
  - Body: `multipart/form-data` (file)
