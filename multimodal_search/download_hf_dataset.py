from datasets import load_dataset
import os
import json
from PIL import Image
import io

# Setup paths
data_dir = os.path.join("data", "images")
os.makedirs(data_dir, exist_ok=True)
dataset_list = []

print("Loading professional AI dataset (COCO sample)...")
try:
    # Use a well-known, fast-streaming dataset
    ds = load_dataset("HuggingFaceM4/COCO", split="train", streaming=True)
except Exception as e:
    print(f"Error loading COCO: {e}")
    # Fallback to another small dataset if COCO is down
    print("Trying fallback dataset (Pokemon for variety)...")
    ds = load_dataset("lambdalabs/pokemon-blip-captions", split="train", streaming=True)

count = 0
for item in ds:
    try:
        if 'image' in item:
            image = item['image']
            # COCO format vs Pokemon format
            if 'sentences' in item: # COCO
                caption = item['sentences']['raw'][0]
            elif 'text' in item: # Pokemon
                caption = item['text']
            else:
                caption = "a professional photograph"
                
            name = f"smart_{count}.jpg"
            path = os.path.join(data_dir, name)
            
            # Save image
            if not isinstance(image, Image.Image):
                 image = Image.open(io.BytesIO(image))
            
            # Convert to RGB if needed (for PNGs/RGBA)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            image.save(path)
            
            dataset_list.append({
                "image_path": f"data/images/{name}",
                "caption": caption
            })
            
            print(f"[{count+1}/50] Saved: {caption[:50]}...")
            count += 1
            
            if count >= 50:
                break
    except Exception as e:
        print(f"Skip item: {e}")
        continue

# Save dataset.json
output_json = os.path.join("data", "dataset.json")
with open(output_json, "w") as f:
    json.dump(dataset_list, f, indent=4)

print(f"Finished! {len(dataset_list)} images saved.")
