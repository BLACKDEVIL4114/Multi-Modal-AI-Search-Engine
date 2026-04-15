import streamlit as st
import os
from PIL import Image
import sys

# Fix pathing so search module and data are discoverable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from search.search_core import search_by_text, search_by_image

# 1. Page configuration
st.set_page_config(page_title="Multimodal Image Search Engine", page_icon="🔍")

def main():
    st.title("🔍 Multimodal Image Search Engine")
    st.markdown("Search for images using text descriptions or other images.")

    # Check if index exists
    emb_path = os.path.join(root_path, "embeddings", "image_embeddings.npy")
    if not os.path.exists(emb_path):
        st.error(f"Please run `pipeline/build_index.py` first. Index not found at {emb_path}")
        return

    # 3. Search Mode Toggle
    search_mode = st.radio(
        "Select Search Mode:",
        ("Search by Text", "Search by Image"),
        horizontal=True
    )

    results = []

    # 4. IF Search by Text
    if search_mode == "Search by Text":
        query = st.text_input("Describe what you are looking for", placeholder="e.g. a cat on the floor")
        search_btn = st.button("Search")
        
        if search_btn and query:
            with st.spinner("Searching..."):
                results = search_by_text(query)

    # 5. IF Search by Image
    else:
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            try:
                # Show preview
                img = Image.open(uploaded_file)
                st.image(img, caption="Query Image", width=200)
                
                search_btn = st.button("Search")
                if search_btn:
                    with st.spinner("Searching..."):
                        results = search_by_image(img)
            except Exception as e:
                st.error(f"Could not open image: {e}")

    # 6. Display results
    if results:
        st.subheader("Results")
        cols = st.columns(3)
        for i, res in enumerate(results):
            with cols[i % 3]:
                if os.path.exists(res["image_path"]):
                    try:
                        display_img = Image.open(res["image_path"])
                        st.image(display_img, use_column_width=True)
                        st.write(f"**Match: {int(res['score'] * 100)}%**")
                    except:
                        st.error("Error loading image file.")
                else:
                    st.warning(f"File not found: {res['image_path']}")
    elif "search_btn" in locals() and search_btn:
        # 7. No results found
        st.info("No results found. Try a different query.")

if __name__ == "__main__":
    main()
