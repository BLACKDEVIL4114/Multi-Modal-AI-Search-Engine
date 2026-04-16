import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from PIL import Image
import io

# Fix pathing so search module is discoverable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from search.search_core import search_by_text, search_by_image

app = FastAPI(
    title="KALI AI | Multimodal Search API",
    description="High-performance text-to-image and image-to-image search engine.",
    version="3.0.0"
)

class SearchResult(BaseModel):
    image_path: str
    score: float

class TextSearchQuery(BaseModel):
    text: str
    top_k: int = 5

@app.get("/")
async def root():
    return {"status": "online", "engine": "KALI AI v3.0", "acceleration": "CUDA" if os.environ.get("CUDA_VISIBLE_DEVICES") else "CPU"}

@app.post("/search/text", response_model=List[SearchResult])
async def text_search(query: TextSearchQuery):
    try:
        results = search_by_text(query.text, top_k=query.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/image", response_model=List[SearchResult])
async def image_search(file: UploadFile = File(...), top_k: int = 5):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        results = search_by_image(image, top_k=top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
