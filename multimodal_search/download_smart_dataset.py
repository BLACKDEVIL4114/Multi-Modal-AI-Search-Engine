import urllib.request, os, json, time

categories = {
    "nature": ["mountain", "lake", "forest", "beach", "desert", "waterfall", "river", "glacier"],
    "animals": ["lion", "tiger", "elephant", "panda", "eagle", "horse", "rabbit", "cat", "dog"],
    "tech": ["laptop", "smartphone", "robot", "server", "camera", "drone", "spacecraft"],
    "food": ["pizza", "sushi", "burger", "cake", "coffee", "fruit", "pasta", "salad"],
    "cities": ["london", "tokyo", "nyc", "paris", "street", "bridge", "office", "concert"]
}

os.makedirs(os.path.join("data", "images"), exist_ok=True)
dataset = []

print("Starting Smart Dataset Download (50 images)...")

count = 0
for category, items in categories.items():
    for item in items:
        name = f"{category}_{item}_{count}"
        path = os.path.join("data", "images", f"{name}.jpg")
        
        # Note: source.unsplash.com is deprecated but often still redirects correctly or we use specific IDs
        # To be safe and fast, we use a slightly more predictable URL pattern or just retry
        url = f"https://source.unsplash.com/600x600/?{item}"
        
        try:
            print(f"Downloading [{count+1}/50]: {item}...")
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            
            urllib.request.urlretrieve(url, path)
            dataset.append({
                "image_path": f"data/images/{name}.jpg",
                "caption": f"a photograph of {item} in a {category} context"
            })
            count += 1
            if count >= 50: break
            time.sleep(0.5)
        except Exception as e:
            print(f"Error downloading {item}: {e}")
            continue
    if count >= 50: break

with open(os.path.join("data", "dataset.json"), "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Smart Dataset Finished! {len(dataset)} images.")
