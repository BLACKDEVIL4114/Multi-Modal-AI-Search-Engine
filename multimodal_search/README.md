# Multi-modal AI Search Engine
A complete search engine that allows finding similar images from a dataset using either text queries or image uploads.

## Features
- **Search by Text**: Enter descriptions like "a cat on the floor" to find matching images.
- **Search by Image**: Upload an image to find visually similar ones in the dataset.
- **Similarity Scoring**: Each result displays a similarity match percentage (e.g., Match: 91%).
- **Automated Indexing**: Pipeline script to pre-calculate and store embeddings for fast retrieval.
- **Interactive UI**: Clean Streamlit interface with loading spinners and error handling.
- **Robustness**: Validates file paths, handles bad uploads, and ensures the index is built before searching.

## Tech Stack
| Category | Library/Technology |
| :--- | :--- |
| Core Language | Python |
| Dataset Handling | `json`, `os` |
| Image Processing | `Pillow` |
| Math & Storage | `NumPy` |
| Deep Learning | `PyTorch`, `transformers` (CLIP) |
| Vector Search | `faiss-cpu` |
| UI Framework | `Streamlit` |

## Folder Structure
```text
multimodal_search/
├── data/
│   ├── images/         # Place your .jpg files here
│   └── dataset.json    # Map images to descriptions
├── embeddings/
│   ├── image_embeddings.npy
│   └── image_paths.npy
├── pipeline/
│   └── build_index.py
├── search/
│   └── search_core.py
├── app/
│   └── streamlit_app.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### Step 1 - Project Setup
Clone or download this project to your local machine.

### Step 2 - Install Dependencies
Ensure you have Python 3.8+ installed. Run the following command:
```bash
pip install -r requirements.txt
```

### Step 3 - Add Data
1. Place your images (`.jpg` or `.png`) inside the `data/images/` folder.
2. Update `data/dataset.json` with the corresponding file paths and captions.

### Step 4 - Generate Embeddings
Run the indexing script once to process images and store vectors in the `embeddings/` folder:
```bash
python pipeline/build_index.py
```

### Step 5 - Launch the App
Start the Streamlit interface:
```bash
streamlit run app/streamlit_app.py
```

## How to Use
1. **Search by Text**: Choose the "Search by Text" radio button, type a query, and click Search.
2. **Search by Image**: Choose the "Search by Image" radio button, upload a file (jpg/png), see the preview, and click Search.
3. **View Results**: The top 3 most similar images will be displayed in columns with their match percentage.

## Notes
- This project uses the **CLIP (Contrastive Language-Image Pre-Training)** model (`openai/clip-vit-base-patch32`) from HuggingFace.
- FAISS is used for high-performance vector similarity search.
- Embeddings are normalized to ensure Cosine Similarity is performed using Inner Product (`IndexFlatIP`).
