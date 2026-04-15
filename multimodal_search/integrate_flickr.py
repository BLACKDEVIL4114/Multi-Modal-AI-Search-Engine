import kagglehub
import os
import json

def integrate():
    print("Downloading Flickr30k from Kaggle (this may take a few mins)...")
    try:
        path = kagglehub.dataset_download("hsankesara/flickr-image-dataset")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return

    print(f"Dataset downloaded to: {path}")
    
    image_folder = os.path.join(path, "flickr30k_images", "flickr30k_images")
    csv_path = os.path.join(path, "results.csv")
    
    if not os.path.exists(csv_path):
        csv_path = os.path.join(path, "flickr30k_images", "results.csv")

    if not os.path.exists(csv_path):
        print(f"Error: Cannot find results.csv in {path}")
        return

    print("Parsing captions...")
    dataset = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:] 
            
            seen_images = set()
            for line in lines:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    img_name = parts[0].strip()
                    caption = parts[2].strip()
                    
                    full_img_path = os.path.join(image_folder, img_name)
                    
                    if img_name not in seen_images and os.path.exists(full_img_path):
                        dataset.append({
                            "image_path": full_img_path, 
                            "caption": caption
                        })
                        seen_images.add(img_name)
                        
                if len(seen_images) >= 500: break 
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return

    output_json = os.path.join("data", "dataset.json")
    with open(output_json, "w") as f:
        json.dump(dataset, f, indent=4)

    print(f"Integrated {len(dataset)} high-quality Flickr images into {output_json}.")

if __name__ == "__main__":
    integrate()
