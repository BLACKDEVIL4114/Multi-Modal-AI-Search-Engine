import streamlit as st
import os
from PIL import Image
import sys

# Fix pathing so search module and data are discoverable
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.append(root_path)

from search.search_core import search_by_text, search_by_image
from utils.docx_prompt_editor import edit_docx_bytes, extract_docx_text_from_bytes

# 1. Page configuration
st.set_page_config(page_title="Multimodal Search + DOCX Editor", page_icon="🔍", layout="wide")


def render_docx_editor():
    st.title("📄 DOCX Prompt Editor")
    st.markdown("Upload a Word document, tell the editor what you want changed, and download the edited file.")

    col_left, col_right = st.columns([1, 1])
    with col_left:
        uploaded_docx = st.file_uploader("Upload a DOCX file", type=["docx"])
        prompt = st.text_area(
            "Edit prompt",
            placeholder='Example: replace "draft" with "final", add heading "Summary", and make the tone more professional.',
            height=180,
        )
        author = st.text_input("Editor name", value="AI Assistant")

    with col_right:
        st.info("Tips")
        st.write("- Use quoted text for precise replacements.")
        st.write("- Examples: `replace \"old\" with \"new\"`, `add heading \"Next Steps\"`.")
        st.write("- If the prompt is broad, the editor will try an LLM rewrite when credentials are configured.")

    if uploaded_docx is not None:
        file_bytes = uploaded_docx.getvalue()
        with st.expander("Preview extracted text", expanded=False):
            try:
                st.text(extract_docx_text_from_bytes(file_bytes))
            except Exception as exc:
                st.warning(f"Could not extract text preview: {exc}")

    if st.button("Edit DOCX", use_container_width=True):
        if uploaded_docx is None:
            st.error("Please upload a DOCX file first.")
            return
        if not prompt.strip():
            st.error("Please describe the edits you want.")
            return

        with st.spinner("Applying edits..."):
            try:
                edited_bytes, result = edit_docx_bytes(
                    uploaded_docx.getvalue(),
                    prompt=prompt,
                    author=author.strip() or "AI Assistant",
                )
                if result.strategy == "clarification":
                    st.warning(result.summary)
                else:
                    st.success(result.summary)
                st.caption(f"Strategy: {result.strategy}")
                st.download_button(
                    "Download edited DOCX",
                    data=edited_bytes,
                    file_name=os.path.splitext(uploaded_docx.name)[0] + "_edited.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
                with st.expander("Applied instructions", expanded=False):
                    if result.instructions:
                        st.json(result.instructions)
                    else:
                        st.write("No structured instructions were returned. The editor used a rewrite or fallback strategy.")
            except Exception as exc:
                st.error(f"Could not edit the document: {exc}")

def main():
    workspace = st.sidebar.radio(
        "Workspace",
        ["Image Search", "DOCX Editor"],
        index=0,
    )

    if workspace == "DOCX Editor":
        render_docx_editor()
        return

    st.title("🔍 Multimodal Image Search Engine")
    st.markdown("Search for images using text descriptions or other images.")

    # --- SIDEBAR SETTINGS ---
    with st.sidebar:
        st.header("⚙️ Search Settings")
        top_k = st.slider("Number of results (Top-K)", min_value=1, max_value=20, value=5)
        st.divider()
        st.info("Performance: Using GPU acceleration if available.")

    # 2. Check if index exists
    index_path = os.path.join(root_path, "embeddings", "vector.index")
    if not os.path.exists(index_path):
        st.error(f"Please run `pipeline/build_index.py` first. Index not found at {index_path}")
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
        
        if (search_btn or query) and query:
            with st.spinner("Searching..."):
                results = search_by_text(query, top_k=top_k)

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
                        results = search_by_image(img, top_k=top_k)
            except Exception as e:
                st.error(f"Could not open image: {e}")

    # 6. Display results
    if results:
        st.subheader(f"Results (Showing top {len(results)})")
        cols = st.columns(3)
        for i, res in enumerate(results):
            with cols[i % 3]:
                # Fix path for image loading (join with root if it's relative)
                img_display_path = res["image_path"]
                if not os.path.isabs(img_display_path):
                    img_display_path = os.path.join(root_path, img_display_path)

                if os.path.exists(img_display_path):
                    try:
                        display_img = Image.open(img_display_path)
                        st.image(display_img, use_column_width=True)
                        st.write(f"**Match: {int(res['score'] * 100)}%**")
                        st.caption(f"Path: {os.path.basename(img_display_path)}")
                    except:
                        st.error("Error loading image file.")
                else:
                    st.warning(f"File not found: {img_display_path}")
    elif "search_btn" in locals() and search_btn:
        # 7. No results found
        st.info("No results found. Try a different query.")

if __name__ == "__main__":
    main()
