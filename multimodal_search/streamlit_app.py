import streamlit as st
import numpy as np
from PIL import Image
import faiss
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search.search_core import load_model_and_processor, search_by_text, search_by_image

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Modal AI Search",
    page_icon="🔍",
    layout="wide"
)

# ─── FIX 1: Cache model so it only loads ONCE, not on every reload ─────────────
@st.cache_resource(show_spinner="Loading AI model... (first time only)")
def get_model():
    return load_model_and_processor()

# ─── FIX 1: Cache embeddings/index too ────────────────────────────────────────
@st.cache_resource(show_spinner="Loading search index...")
def get_index():
    embeddings_path = "embeddings/image_embeddings.npy"
    paths_path = "embeddings/image_paths.npy"

    if not os.path.exists(embeddings_path) or not os.path.exists(paths_path):
        return None, None

    embeddings = np.load(embeddings_path)
    image_paths = np.load(paths_path, allow_pickle=True)

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return index, image_paths

# ─── Load (cached after first run) ────────────────────────────────────────────
model, processor = get_model()
index, image_paths = get_index()

# ─── UI ───────────────────────────────────────────────────────────────────────
st.title("🔍 Multi-Modal AI Search Engine")
st.markdown("Find similar images using **text** or **image** queries.")

if index is None:
    st.error("⚠️ Embeddings not found. Run `python pipeline/build_index.py` first.")
    st.stop()

# ─── Search Mode ──────────────────────────────────────────────────────────────
mode = st.radio("Search by:", ["Text", "Image"], horizontal=True)

query_embedding = None

if mode == "Text":
    query = st.text_input("Enter your search query:", placeholder="e.g. a cat sitting on a chair")
    if st.button("🔍 Search", type="primary") and query.strip():
        with st.spinner("Searching..."):
            query_embedding = search_by_text(query, model, processor)

elif mode == "Image":
    uploaded = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Your uploaded image", width=300)
        if st.button("🔍 Find Similar", type="primary"):
            with st.spinner("Searching..."):
                query_embedding = search_by_image(img, model, processor)

# ─── Show Results ─────────────────────────────────────────────────────────────
if query_embedding is not None:
    query_embedding = query_embedding / np.linalg.norm(query_embedding)
    scores, indices = index.search(query_embedding.reshape(1, -1), k=3)

    st.markdown("---")
    st.subheader("Top Results")
    cols = st.columns(3)

    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        path = image_paths[idx]
        if os.path.exists(path):
            with cols[i]:
                st.image(path, use_column_width=True)
                st.metric("Match", f"{score * 100:.1f}%")
        else:
            cols[i].warning(f"Image not found:\n{path}")
