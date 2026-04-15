from PIL import Image, ImageDraw
import os

def create_sample_images():
    output_dir = os.path.join("data", "images")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    samples = [
        ("cat.jpg", (255, 200, 200), "CAT"),
        ("dog.jpg", (200, 255, 200), "DOG"),
        ("car.jpg", (200, 200, 255), "CAR"),
        ("sunset.jpg", (255, 255, 200), "SUNSET"),
        ("mountain.jpg", (200, 255, 255), "MOUNTAIN")
    ]
    
    for filename, color, text in samples:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            img = Image.new('RGB', (400, 400), color=color)
            d = ImageDraw.Draw(img)
            d.text((150, 180), text, fill=(0, 0, 0))
            img.save(path)
            print(f"Created sample image: {path}")

if __name__ == "__main__":
    create_sample_images()
