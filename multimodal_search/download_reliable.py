import urllib.request, os, json

images = [
    {"url": "https://images.pexels.com/photos/45201/kitty-cat-baby-animal-45201.jpeg", "caption": "a cute white cat sitting"},
    {"url": "https://images.pexels.com/photos/1108099/pexels-photo-1108099.jpeg", "caption": "two golden retriever puppies playing"},
    {"url": "https://images.pexels.com/photos/1661179/pexels-photo-1661179.jpeg", "caption": "a green parrot on a branch"},
    {"url": "https://images.pexels.com/photos/462118/pexels-photo-462118.jpeg", "caption": "a beautiful tropical beach with palm trees"},
    {"url": "https://images.pexels.com/photos/326055/pexels-photo-326055.jpeg", "caption": "a blue butterfly on a flower"},
    {"url": "https://images.pexels.com/photos/33109/fall-autumn-red-season.jpg", "caption": "red autumn leaves in a forest"},
    {"url": "https://images.pexels.com/photos/1402717/pexels-photo-1402717.jpeg", "caption": "a white sports car driving on a highway"},
    {"url": "https://images.pexels.com/photos/376464/pexels-photo-376464.jpeg", "caption": "a stack of pancakes with blueberries"},
    {"url": "https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg", "caption": "a delicious burger with french fries"},
    {"url": "https://images.pexels.com/photos/3408744/pexels-photo-3408744.jpeg", "caption": "mountains covered in snow at sunset"},
    {"url": "https://images.pexels.com/photos/258109/pexels-photo-258109.jpeg", "caption": "a large elephant in the savanna"},
    {"url": "https://images.pexels.com/photos/1624496/pexels-photo-1624496.jpeg", "caption": "the planet earth from space"},
    {"url": "https://images.pexels.com/photos/1036623/pexels-photo-1036623.jpeg", "caption": "a modern office building with glass windows"},
    {"url": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg", "caption": "people high-fiving in a business meeting"},
    {"url": "https://images.pexels.com/photos/326503/pexels-photo-326503.jpeg", "caption": "a laptop on a wooden desk with a cup of coffee"},
    {"url": "https://images.pexels.com/photos/1761279/pexels-photo-1761279.jpeg", "caption": "a glowing city skyline at night"},
    {"url": "https://images.pexels.com/photos/1149137/pexels-photo-1149137.jpeg", "caption": "a yellow sports car parked on the street"},
    {"url": "https://images.pexels.com/photos/1054218/pexels-photo-1054218.jpeg", "caption": "a foggy forest with tall pine trees"},
    {"url": "https://images.pexels.com/photos/356079/pexels-photo-356079.jpeg", "caption": "a modern computer motherboard with chips"}
]

os.makedirs(os.path.join("data", "images"), exist_ok=True)
dataset = []

print("Downloading high-quality dataset...")

for i, item in enumerate(images):
    path = os.path.join("data", "images", f"smart_{i}.jpg")
    try:
        print(f"Downloading [{i+1}/{len(images)}]: {item['caption']}...")
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(item["url"], path)
        dataset.append({
            "image_path": f"data/images/smart_{i}.jpg",
            "caption": item["caption"]
        })
    except Exception as e:
        print(f"Failed to download image {i}: {e}")
        continue

with open(os.path.join("data", "dataset.json"), "w") as f:
    json.dump(dataset, f, indent=4)

print(f"Smart Dataset Ready! {len(dataset)} images.")
