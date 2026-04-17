import streamlit as st
import os
import json
import base64
import requests
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

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
def call_gemini(prompt, api_key, image_bytes=None):
    if not api_key: return "⚠️ Please provide a Gemini API Key."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    parts = [{"text": prompt}]
    if image_bytes:
        encoded = base64.b64encode(image_bytes).decode('utf-8')
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": encoded
            }
        })
        
    body = {"contents": [{"parts": parts}]}
    try:
        resp = requests.post(url, headers=headers, json=body)
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {str(e)}"

def call_groq(prompt, api_key):
    if not api_key: return "⚠️ Please provide a Groq API Key."
    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_completion_tokens=4096,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>✦ KALI AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; opacity:0.7;'>intelligence Studio v3.5</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show ONLY the Intelligence Engine selector as requested
    model_choice = st.selectbox("Intelligence Engine", ["Gemini 2.0 (Fastest)", "Groq Llama 3.3 (Pro)", "Gemma 2 (HuggingFace)"])
    
    # Background Keys (Hidden from UI)
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    st.markdown("---")
    st.markdown("### 📁 Multimodal Input")
    uploaded_file = st.file_uploader("Drop Image, PDF, or Code here", type=["png", "jpg", "jpeg", "pdf", "docx", "txt", "py", "xlsx"])
    
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("<div class='sidebar-card'><b>Pro Tip:</b> Use Llama 3.3 for complex coding help and Gemini for image/visual discovery.</div>", unsafe_allow_html=True)

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
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(f"<div class='user-msg'>{prompt}</div>", unsafe_allow_html=True)
        img_bytes = None
        if uploaded_file and uploaded_file.type.startswith("image/"):
            st.image(uploaded_file, width=300)
            img_bytes = uploaded_file.getvalue()
            st.session_state.messages[-1]["image"] = img_bytes

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ""
            if "Gemini" in model_choice:
                response = call_gemini(prompt, gemini_key, img_bytes)
            elif "Groq" in model_choice:
                full_prompt = prompt
                if uploaded_file:
                    full_prompt = f"Note: User uploaded {uploaded_file.name}. \n\n" + prompt
                response = call_groq(full_prompt, groq_key)
            else:
                response = "HuggingFace Gemma integration is being initialized. Use Gemini or Groq."
            
            st.markdown(f"<div class='ai-msg'>{response}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- LANDING STATE ---
if not st.session_state.messages:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='color:#FF4B4B !important;'>💻 Code Help</h3>
        Ask for Python scripts, React components, or debugging help.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='color:#1A73E8 !important;'>📄 Doc Analysis</h3>
        Upload a PDF or DOCX to summarize or extract data.
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='color:#00D1FF !important;'>🎨 Visual AI</h3>
        Upload an image and ask "What is this?" or "Convert to HTML".
        </div>
        """, unsafe_allow_html=True)
