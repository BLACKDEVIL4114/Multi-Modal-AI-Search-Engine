import os
import requests
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from PIL import Image
import io

# ── Configuration ──────────────────────────────────
DATA_DIR = os.path.join("data", "images")
INDEX_PATH = os.path.join("embeddings", "faiss_index.bin")
METADATA_PATH = os.path.join("data", "dataset.json")
CATEGORIES = ["nature", "tech", "people", "abstract", "architecture", "travel"]
ASSETS_PER_CAT = 15

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("embeddings", exist_ok=True)

# ── Autonomous Ingestion ─────────────────────────
def download_image(args):
    idx, cat = args
    # Using Picsum for ultra-reliable asset mining
    url = f"https://picsum.photos/seed/{cat}_{idx}/800/600"
    path = os.path.join(DATA_DIR, f"{cat}_{idx}.jpg")
    try:
        response = requests.get(url, timeout=12)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return {"path": path, "label": cat}
    except:
        return None

print("MINING PROFESSIONAL ASSETS...")
tasks = [(i, cat) for cat in CATEGORIES for i in range(ASSETS_PER_CAT)]
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(download_image, tasks))

valid_results = [r for r in results if r]
print(f"Harvested {len(valid_results)} high-fidelity assets.")

# ── Core Fusion (Embedding & Indexing) ──────────
print("FUSING VECTOR MATRIX...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
metadata = []
embeddings = []

for item in valid_results:
    # Use text embeddings for the label as a proxy for image analysis in this stage
    emb = embedder.encode(item['label']) 
    embeddings.append(emb)
    metadata.append(item)

# Build FAISS Index
emb_matrix = np.array(embeddings).astype('float32')
dimension = emb_matrix.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(emb_matrix)

# Save Assets
faiss.write_index(index, INDEX_PATH)
with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f)

print(f"OPERATION COMPLETE. Vector Matrix Synced: {INDEX_PATH}")
