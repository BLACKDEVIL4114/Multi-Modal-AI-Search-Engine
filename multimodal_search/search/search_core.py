import os
import numpy as np
import torch
import faiss

# Fix for OpenMP runtime conflict on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from PIL import Image
from transformers import CLIPProcessor, CLIPModel

def search_by_text(query, top_k=3):
    """Search images using a text query."""
    try:
        # Load Model and Processor inside the function
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Tokenize and generate text embedding
        inputs = processor(text=[query], return_tensors="pt", padding=True)
        with torch.no_grad():
            text_features = model.get_text_features(**inputs)
        
        # Convert to numpy and normalize
        text_embedding = text_features.numpy().astype('float32')
        norm = np.linalg.norm(text_embedding)
        if norm > 0:
            text_embedding = text_embedding / norm
            
        # Load indexed data
        emb_path = os.path.join("embeddings", "image_embeddings.npy")
        paths_path = os.path.join("embeddings", "image_paths.npy")
        
        if not os.path.exists(emb_path) or not os.path.exists(paths_path):
            return []
            
        image_embeddings = np.load(emb_path).astype('float32')
        image_paths = np.load(paths_path)
        
        # Build FAISS Index (IndexFlatIP for inner product / cosine similarity on normalized vectors)
        dimension = image_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(image_embeddings)
        
        # Search
        scores, indices = index.search(text_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1: # FAISS returns -1 if not enough matches
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
        # Convert to RGB
        image = uploaded_image.convert("RGB")
        
        # Load Model and Processor inside the function
        model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Generate image embedding
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        
        # Convert to numpy and normalize
        query_embedding = image_features.numpy().astype('float32')
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm
            
        # Load indexed data
        emb_path = os.path.join("embeddings", "image_embeddings.npy")
        paths_path = os.path.join("embeddings", "image_paths.npy")
        
        if not os.path.exists(emb_path) or not os.path.exists(paths_path):
            return []
            
        image_embeddings = np.load(emb_path).astype('float32')
        image_paths = np.load(paths_path)
        
        # Build FAISS Index
        dimension = image_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(image_embeddings)
        
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
