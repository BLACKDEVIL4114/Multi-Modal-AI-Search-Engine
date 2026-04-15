import os
import requests
import json
import faiss
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer

# ── Configuration ──────────────────────────────────
DATA_DIR = os.path.join("data", "industrial_images")
CHECKPOINT_PATH = "training_checkpoint.json"
INDEX_PATH = os.path.join("embeddings", "industrial_index.bin")
METADATA_PATH = os.path.join("data", "industrial_metadata.json")

TOTAL_TARGET = 1000  # Large scale target
BATCH_SIZE = 10
CATEGORIES = ["nature", "city", "space", "cyberpunk", "ocean", "desert"]

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("embeddings", exist_ok=True)

# ── Progress Tracker (Checkpoint Persistence) ──
def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r") as f:
                return json.load(f)
        except: pass
    return {"last_idx": 0, "processed_paths": []}

def save_checkpoint(last_idx, processed_paths):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump({"last_idx": last_idx, "processed_paths": processed_paths}, f)

# ── Resumable Ingestion ─────────────────────────
def download_batch(start_idx, count):
    batch_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(start_idx, start_idx + count):
            cat = CATEGORIES[i % len(CATEGORIES)]
            url = f"https://picsum.photos/seed/{cat}_{i}/800/600"
            path = os.path.join(DATA_DIR, f"asset_{i}.jpg")
            futures.append(executor.submit(requests.get, url, timeout=12))
        
        for i, future in enumerate(futures):
            try:
                res = future.result()
                if res.status_code == 200:
                    path = os.path.join(DATA_DIR, f"asset_{start_idx + i}.jpg")
                    with open(path, "wb") as f:
                        f.write(res.content)
                    batch_results.append({"path": path, "label": CATEGORIES[(start_idx + i) % len(CATEGORIES)]})
            except: continue
    return batch_results

# ── Industrial Training Loop ─────────────────────
def industrial_forge():
    print("--- INDUSTRIAL FORGE: RESUMABLE PIPELINE ACTIVE ---")
    progress = load_checkpoint()
    start_idx = progress["last_idx"]
    processed = progress["processed_paths"]
    
    if start_idx >= TOTAL_TARGET:
        print("Pipeline already complete. No new work detected.")
        return

    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Load existing Index if resuming
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
    else:
        index = None

    try:
        for i in range(start_idx, TOTAL_TARGET, BATCH_SIZE):
            current_batch_size = min(BATCH_SIZE, TOTAL_TARGET - i)
            print(f"Processing Batch {i//BATCH_SIZE + 1} ({i}/{TOTAL_TARGET})...")
            
            assets = download_batch(i, current_batch_size)
            if not assets: continue
            
            # Embed & Index
            embs = embedder.encode([a['label'] for a in assets])
            matrix = np.array(embs).astype('float32')
            
            if index is None:
                index = faiss.IndexFlatL2(matrix.shape[1])
            index.add(matrix)
            
            # Update Progress
            processed.extend(assets)
            save_checkpoint(i + current_batch_size, processed)
            faiss.write_index(index, INDEX_PATH)
            
            print(f"Checkpoint Locked: {i + current_batch_size} assets synced.")
            
    except KeyboardInterrupt:
        print("\n[PAUSE DETECTED] Process suspended. State saved for resumption.")
    except Exception as e:
        print(f"\n[ERROR] Pipeline interrupted: {e}")
        print("State preserved. You can resume at any time.")

if __name__ == "__main__":
    industrial_forge()
