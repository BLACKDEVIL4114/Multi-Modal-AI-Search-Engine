import os
import numpy as np
import torch
import faiss

# Fix for OpenMP runtime conflict on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# --- GLOBAL MODEL CACHE ---
_MODEL = None
_PROCESSOR = None
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def get_model():
    global _MODEL, _PROCESSOR
    if _MODEL is None:
        print(f"Loading CLIP model and processor on {_DEVICE}...")
        _MODEL = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(_DEVICE)
        _PROCESSOR = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return _MODEL, _PROCESSOR

def search_by_text(query, top_k=3):
    """Search images using a text query."""
    try:
        model, processor = get_model()
        
        # Tokenize and generate text embedding
        inputs = processor(text=[query], return_tensors="pt", padding=True).to(_DEVICE)
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        
        # Move back to CPU for numpy conversion
        text_embedding = text_features.cpu().numpy().astype('float32')
        norm = np.linalg.norm(text_embedding)
        if norm > 0:
            text_embedding = text_embedding / norm
            
        # Load indexed data
        index_path = os.path.join("embeddings", "vector.index")
        paths_path = os.path.join("embeddings", "image_paths.npy")
        
        if not os.path.exists(index_path) or not os.path.exists(paths_path):
            print("Error: Index or paths file missing.")
            return []
            
        # 📂 LOAD PERSISTENT INDEX
        index = faiss.read_index(index_path)
        image_paths = np.load(paths_path)
        
        # Search
        scores, indices = index.search(text_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    "image_path": str(image_paths[idx]),
                    "score": round(float(scores[0][i]), 2)
                })
        
        return results

    except Exception as e:
        print(f"Error in text search: {e}")
        return []

def search_by_image(uploaded_image, top_k=3):
    """Search images using an uploaded image."""
    try:
        model, processor = get_model()
        
        # Convert to RGB
        image = uploaded_image.convert("RGB")
        
        # Generate image embedding
        inputs = processor(images=image, return_tensors="pt").to(_DEVICE)
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        # Move back to CPU for numpy conversion
        query_embedding = image_features.cpu().numpy().astype('float32')
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm
            
        # Load indexed data
        index_path = os.path.join("embeddings", "vector.index")
        paths_path = os.path.join("embeddings", "image_paths.npy")
        
        if not os.path.exists(index_path) or not os.path.exists(paths_path):
            print("Error: Index or paths file missing.")
            return []
            
        # 📂 LOAD PERSISTENT INDEX
        index = faiss.read_index(index_path)
        image_paths = np.load(paths_path)
        
        # Search
        scores, indices = index.search(query_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1:
                results.append({
                    "image_path": str(image_paths[idx]),
                    "score": round(float(scores[0][i]), 2)
                })
        
        return results

    except Exception as e:
        print(f"Error in image search: {e}")
        return []
