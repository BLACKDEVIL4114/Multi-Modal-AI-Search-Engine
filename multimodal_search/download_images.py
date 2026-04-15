import urllib.request, os

# Create directory if it doesn't exist
os.makedirs(os.path.join("data", "images"), exist_ok=True)

images = {
    "cat":      "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400",
    "dog":      "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=400",
    "car":      "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400",
    "sunset":   "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=400",
    "mountain": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400",
    "beach":    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400",
    "pizza":    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400",
    "burger":   "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    "bicycle":  "https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400",
    "forest":   "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400",
}

print("Starting image downloads...")
for name, url in images.items():
    path = os.path.join("data", "images", f"{name}.jpg")
    try:
        # Use a User-Agent to avoid being blocked by some servers
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        urllib.request.urlretrieve(url, path)
        print(f"Downloaded {name}.jpg")
    except Exception as e:
        print(f"Failed to download {name}.jpg: {e}")
