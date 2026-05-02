import json
import os
import numpy as np
import torch
import faiss
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

def build_index():
    # Paths configuration
    data_dir = os.path.join("data")
    dataset_path = os.path.join(data_dir, "dataset.json")
    embeddings_dir = os.path.join("embeddings")
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # 1. Load dataset.json
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found.")
        return
        
    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    # Load Model and Processor
    print("Loading CLIP model (openai/clip-vit-base-patch32)...")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    embeddings = []
    valid_paths = []

    # 2. Validate paths and 3. Extract embeddings
    print("Starting image indexing...")
    BATCH_SIZE = 32
    all_entries = [e for e in dataset if os.path.exists(e["path"])]
    
    for i in range(0, len(all_entries), BATCH_SIZE):
        batch = all_entries[i:i+BATCH_SIZE]
        images = []
        batch_paths = []
        for entry in batch:
            try:
                img = Image.open(entry["path"]).convert("RGB")
                images.append(img)
                batch_paths.append(entry["path"])
            except Exception as e:
                print(f"Error loading {entry['path']}: {e}")
                continue
        
        if not images:
            continue
            
        try:
            inputs = processor(images=images, return_tensors="pt", padding=True).to(device)
            with torch.no_grad():
                image_features = model.get_image_features(**inputs)
            
            batch_embeddings = image_features.cpu().numpy().astype('float32')
            for j, emb in enumerate(batch_embeddings):
                norm = np.linalg.norm(emb)
                if norm > 0:
                    emb = emb / norm
                embeddings.append(emb)
                valid_paths.append(batch_paths[j])
        except Exception as e:
            print(f"Batch error: {e}")
            continue
        
        print(f"Indexed {min(i+BATCH_SIZE, len(all_entries))}/{len(all_entries)} images...")

    if not embeddings:
        print("No images were indexed. Check your images directory.")
        return

    # 4. Stack all embeddings
    embeddings_array = np.vstack(embeddings).astype('float32')
    paths_array = np.array(valid_paths)

    # Ensure embeddings directory exists
    if not os.path.exists(embeddings_dir):
        os.makedirs(embeddings_dir)

    # 5. Save raw embeddings and paths
    np.save(os.path.join(embeddings_dir, "image_embeddings.npy"), embeddings_array)
    np.save(os.path.join(embeddings_dir, "image_paths.npy"), paths_array)

    # 6. Build and save FAISS index for high-speed retrieval
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings_array)
    faiss.write_index(index, os.path.join(embeddings_dir, "vector.index"))

    # 7. Final Output
    print(f"Succeeded: {len(valid_paths)} images indexed successfully.")
    print(f"Embeddings saved to {os.path.join(embeddings_dir, 'image_embeddings.npy')}")
    print(f"FAISS index saved to {os.path.join(embeddings_dir, 'vector.index')}")

if __name__ == "__main__":
    build_index()
