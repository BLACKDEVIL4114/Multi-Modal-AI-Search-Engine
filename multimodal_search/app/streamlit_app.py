import streamlit as st
import os
import json
import base64
import requests
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (Check root and app dir)
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv("../.env")

# --- DOCUMENT PARSER ---
def extract_text_from_file(file):
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file.type in ["text/plain", "text/x-python", "application/octet-stream"]:
            return file.getvalue().decode("utf-8")
        return ""
    except Exception as e:
        return f"Error reading file: {str(e)}"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Kali AI | Intelligence Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;600&display=swap');

    :root {
        --primary: #FF3B30;
        --bg-pure: #FFFFFF;
        --text-obsidian: #000000;
        --sidebar-bg: #F2F2F7;
    }

    .stApp {
        background-color: var(--bg-pure) !important;
        color: var(--text-obsidian) !important;
        font-family: 'Inter', sans-serif;
    }

    /* Brighter, Properly Visible Headings */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #000000 !important;
    }

    .main-title {
        color: #FF3B30 !important;
        -webkit-text-fill-color: #FF3B30 !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
    }

    /* FORCED BRIGHTNESS for Buttons */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
    }

    .stButton>button:hover {
        background-color: #FF3B30 !important;
        color: #FFFFFF !important;
    }
    
    /* RADiant CLEAR CHAT BUTTON FIX */
    div[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        background: linear-gradient(90deg, #FF3B30, #FF7A70) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        min-height: 50px !important;
    }

    /* Sidebar - Crisp Modern Look */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid rgba(0,0,0,0.05) !important;
    }

    /* Chat Bubbles - High Contrast Day Mode */
    .user-msg {
        background: #007AFF !important;
        color: #FFFFFF !important;
        padding: 1.2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        font-weight: 500;
    }

    .ai-msg {
        background: #F2F2F7 !important;
        color: #000000 !important;
        padding: 1.2rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        border: 1px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
    }

    /* Card Surfaces */
    .feature-card {
        background: #FFFFFF !important;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(0,0,0,0.1) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04) !important;
        transition: transform 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- AI ENGINES ---

def call_groq(prompt, api_key):
    if not api_key: return "⚠️ Please provide a Groq API Key."
    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # High-speed, high-quota engine
            messages=[
                {
                    "role": "system", 
                    "content": """You are the Absolute Intelligence Engine, an elite AI specialized in zero-error technical analysis and architecture. 
                    
                    INTERNAL AUDIT PROTOCOL:
                    - Before responding, internally verify the structural integrity of your analysis.
                    - REPETITION SHIELD: If the input document is highly repetitive or consists purely of template placeholders (like "NAME: NAME: NAME:"), do not repeat the noise. State clearly in the 'Overall Summary' that the document contains empty template repetition.
                    - Ensure every claim is backed by the document content or proven technical principles.
                    - Eliminate all conversational filler; provide only high-fidelity, data-driven content.

                    MODE SELECTION:
                    - ANALYSIS MODE: Triggered by documents/research. Follow the EXACT structure below.
                    - CHAT MODE: Triggered by greetings. Warm, premium, and brief.

                    IDEAL ANALYSIS STRUCTURE (STRICT):
                    1. **Overall Summary**: A concise 2-3 sentence overview.
                    2. 🧠 **Project Understanding**: Bulleted list of core project components.
                    3. 👉 **Tech stack**: Clean list of technologies used.
                    4. 📅 **Week-by-Week Breakdown**: 
                       - Grouped weeks (e.g., Weeks 1–2, 3–4).
                       - Tasks completed within those weeks.
                       - 📌 **Insight**: A brief technical commentary on that phase.
                    5. ✅ **Strengths of This Work**: Multi-bulleted list of positives.
                    6. ⚠️ **Weaknesses / Improvements Needed**: Honest list of errors or missing pieces.
                    7. 📊 **Final Evaluation (Honest)**: 
                       - Technical Level: ⭐ rating
                       - Completeness: ⭐ rating
                       - Professional Quality: ⭐ rating
                    8. 💡 **Suggestions to Make It Outstanding**: Actionable executive steps.
                    9. 🧾 **One-Line Conclusion**: Final definitive verdict.

                    Format with Bold Headers, Emojis, and extreme technical clarity.
                    Tone: Mathematical, Precise, and World-Class."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Balanced for both structure and loop prevention
            max_completion_tokens=4096,
            top_p=1.0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>✦ KALI AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; opacity:0.7;'>intelligence Studio v3.5</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show ONLY the working Intelligence Engines
    model_choice = "Groq Llama 3.3 (Pro)"
    st.info(f"🚀 Running on {model_choice}")
    
    # Background Keys (Only Groq needed now)
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    st.markdown("---")
    st.markdown("### 📁 Multimodal Input")
    uploaded_file = st.file_uploader("Drop Image, PDF, or Code here", type=["png", "jpg", "jpeg", "pdf", "docx", "txt", "py", "xlsx"])
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<div class='sidebar-card'><b>Pro Tip:</b> Use Llama 3.3 (Pro) for blazing fast coding help and reasoning.</div>", unsafe_allow_html=True)

# --- MAIN CHAT INTERFACE ---
st.markdown("<h1 class='main-title'>Intelligence Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.1rem; opacity:0.8;'>Ask questions, build code, and analyze documents in one place.</p>", unsafe_allow_html=True)

# Display Messages
for message in st.session_state.messages:
    cls = "user-msg" if message["role"] == "user" else "ai-msg"
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='{cls}'>{message['content']}</div>", unsafe_allow_html=True)
        if "image" in message:
            st.image(message["image"], width=300)

# Input Box
if prompt := st.chat_input("What are we building today?"):
    # CLEAN DISPLAY MESSAGE
    display_user_msg = prompt if prompt else f"📄 Analyzing: {uploaded_file.name}"
    st.session_state.messages.append({"role": "user", "content": display_user_msg})
    
    with st.chat_message("user"):
        st.markdown(f"<div class='user-msg'>{display_user_msg}</div>", unsafe_allow_html=True)
        if uploaded_file and uploaded_file.type.startswith("image/"):
            img_bytes = uploaded_file.getvalue()
            st.image(uploaded_file, width=300)
            st.session_state.messages[-1]["image"] = img_bytes

    # GENERATE AI RESPONSE (With Background Prompt)
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            full_prompt = prompt
            if uploaded_file:
                file_content = extract_text_from_file(uploaded_file)
                if file_content:
                    full_prompt = f"""
                    [ANALYZE MODE]
                    FILE: {uploaded_file.name}
                    CONTENT: {file_content[:18000]}
                    USER QUERY: {prompt if prompt else "Analyze this document thoroughly and provide a detailed breakdown."}
                    """
                else:
                    full_prompt = f"Extraction failed for {uploaded_file.name}. Respond to: {prompt}"
            
            response = call_groq(full_prompt, groq_key)
            st.markdown(f"<div class='ai-msg'>{response}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- LANDING STATE ---
if not st.session_state.messages:
    st.markdown("""
    <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; text-align: center;'>
        <div style='width: 80px; height: 80px; background: #000; border-radius: 24px; display: flex; align-items: center; justify-content: center; margin-bottom: 2rem; box-shadow: 0 20px 50px rgba(0,0,0,0.1);'>
            <span style='color: #FFF; font-size: 2rem;'>✦</span>
        </div>
        <h1 style='font-size: 3.5rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 0.5rem;'>Intelligence Studio</h1>
        <p style='font-size: 1.2rem; opacity: 0.5; font-weight: 400;'>Ready to analyze, code, and assist you today.</p>
    </div>
    """, unsafe_allow_html=True)

# --- END OF APP ---
