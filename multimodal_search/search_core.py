import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

MODEL_NAME = "openai/clip-vit-base-patch32"

def load_model_and_processor():
    """
    Load CLIP model and processor.
    Called once and cached by Streamlit's @st.cache_resource.
    """
    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()
    return model, processor


def search_by_text(query: str, model, processor) -> np.ndarray:
    """
    Encode a text query into a normalized embedding vector.
    """
    inputs = processor(text=[query], return_tensors="pt", padding=True)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)
    embedding = embedding.cpu().numpy().astype("float32")
    embedding = embedding / np.linalg.norm(embedding)
    return embedding


def search_by_image(image: Image.Image, model, processor) -> np.ndarray:
    """
    Encode an image into a normalized embedding vector.
    """
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    embedding = embedding.cpu().numpy().astype("float32")
    embedding = embedding / np.linalg.norm(embedding)
    return embedding
