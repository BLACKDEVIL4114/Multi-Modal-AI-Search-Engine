# 🤖 ChatGPT Clone | Intelligence Studio v2.0

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit)
![Groq](https://img.shields.io/badge/Powered%20By-Groq-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Vision-Gemini%202.0-blue?style=for-the-badge)

An advanced, high-fidelity AI assistant designed for real-time intelligence gathering, surgical document processing, and multi-modal analysis. This platform combines the speed of Groq's Llama 3 models with the deep reasoning and grounding of Google Gemini.

## 🌟 Key Features

*   **🌐 Real-Time Web Intelligence**: Autonomous web scraping and search grounding using DuckDuckGo and custom scrapers to provide up-to-the-minute data.
*   **🧬 Surgical Document Editing**: Industry-first "Surgical Mode" that allows the AI to perform redline edits directly on `.docx` files, preserving formatting while tracking changes.
*   **📸 Vision & Multi-Modal**: Analyze images and complex visual data using integrated Vision models.
*   **🎙️ Voice Command System**: Integrated mic-recorder for hands-free intelligence queries.
*   **🔍 RAG (Retrieval-Augmented Generation)**: High-speed local knowledge indexing using FAISS for PDF and Word document ingestion.
*   **🎨 Glassmorphic UI**: A premium, modern dashboard designed with a midnight-slate aesthetic and fluid animations.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/BLACKDEVIL4114/Multi-Modal-AI-Search-Engine.git
cd Multi-Modal-AI-Search-Engine/chatgpt_clone
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the `chatgpt_clone` directory:
```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 4. Launch the Studio
```bash
streamlit run app.py --server.port 8503
```

## 🧠 Neural Architecture

The system utilizes a dual-engine routing matrix:
- **Primary Engine**: Llama-3.3-70b (via Groq) for lightning-fast reasoning.
- **Secondary/Vision Engine**: Gemini 2.0 Flash for multi-modal tasks and search grounding.
- **Vector Store**: FAISS for high-performance similarity search across uploaded assets.

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Custom CSS-overridden for premium UI)
- **AI Models**: Groq Llama 3.3, Google Gemini 2.0
- **Parsing**: `python-docx`, `PyPDF2`, `BeautifulSoup4`
- **Vector Ops**: `faiss-cpu`, `sentence-transformers`

---
Developed by [BLACKDEVIL4114](https://github.com/BLACKDEVIL4114)
