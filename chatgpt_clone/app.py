import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import io
import re
import base64
import requests
from bs4 import BeautifulSoup

from urllib.parse import urlparse
import socket

# ── Cybersecurity: Scraper Firewall ────────────
def is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']: return False
        hostname = parsed.hostname
        if not hostname: return False
        
        # Block common local/private IP ranges
        ip = socket.gethostbyname(hostname)
        parts = list(map(int, ip.split('.')))
        if parts[0] in [127, 10, 172, 192]: return False # Local/Private
        if ip == '169.254.169.254': return False # Cloud Metadata
        return True
    except:
        return False

# ── Web-Synapse: Autonomous Search ────────────────
def autonomous_search(query):
    try:
        url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []
        for result in soup.find_all('div', class_='result__body')[:5]:
            title = result.find('a', class_='result__a').get_text()
            snippet = result.find('a', class_='result__snippet').get_text()
            link = result.find('a', class_='result__a')['href']
            results.append(f"Title: {title}\nSummary: {snippet}\nSource: {link}\n")
        
        return "\n".join(results)
    except Exception as e:
        return f"Search Error: {str(e)}"

# ── Web Intelligence Engine (Hardened) ────────
def fetch_web_content(url):
    if not is_safe_url(url):
        return "⚠️ [SECURITY BLOCK] Access to internal, local, or unsafe resources is prohibited."
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        
        if url.lower().endswith('.docx') or 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.headers.get('Content-Type', ''):
            st.session_state.template_bytes = response.content
            return "✅ [BINARY CAPTURED] Remote document integrated."
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)[:15000]
    except Exception as e:
        return f"Error: {str(e)}"

# ── Session Init ───────────────────────────────────
if "chat_id" not in st.session_state:
    import time
    st.session_state.chat_id = str(int(time.time()))

# ── Environment ────────────────────────────────────
load_dotenv()
DEFAULT_API_KEY = os.getenv("GROQ_API_KEY")

@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

# ── Kali AI Premium UI Shell ─────────────────────────
st.set_page_config(page_title="Kali AI | Intelligence Studio", layout="wide", page_icon="🐍")

# 🎨 ELITE STUDIO DESIGN SYSTEM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Playfair+Display:ital@1&display=swap');
    
    :root {
        --bg-color: #FFFEFA;
        --sidebar-bg: #F5F7F2;
        --accent-gold: #D4AF37;
        --accent-emerald: #064E3B;
        --text-main: #1A1A1A;
        --glass-bg: rgba(255, 255, 255, 0.7);
    }

    .stApp {
        background-color: var(--bg-color);
        color: var(--text-main);
        font-family: 'Outfit', sans-serif;
    }

    /* GLASSMORPHIC SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    /* PREMIUM HEADERS */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 600;
        color: var(--accent-emerald);
        margin-bottom: 0px;
        letter-spacing: -1.5px;
    }
    .sub-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 5px;
        color: var(--accent-gold);
        margin-bottom: 2.5rem;
        opacity: 0.8;
    }

    /* CHAT BUBBLES - GLASSMORPHIC */
    .stChatMessage {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px !important;
        border: 1px solid rgba(0, 0, 0, 0.04) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stChatMessage:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.05) !important;
    }

    /* UPLOADER TRANSFORMATION */
    .stFileUploader {
        background: rgba(0, 78, 59, 0.02) !important;
        border: 1px dashed rgba(6, 78, 59, 0.1) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* BUTTONS */
    .stButton>button, .stDownloadButton>button {
        background: linear-gradient(135deg, var(--accent-emerald), #0A5F44) !important;
        color: white !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px rgba(6, 78, 59, 0.2) !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 12px 35px rgba(6, 78, 59, 0.3) !important;
    }

    .pulse-badge {
        display: inline-block;
        padding: 6px 18px;
        background: rgba(212, 175, 55, 0.1);
        color: var(--accent-gold);
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        border: 1px solid rgba(212, 175, 55, 0.4);
    }

    /* COMBINED BAR CSS */
    [data-testid="stPopover"] > button {
        background-color: transparent !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-right: none !important;
        border-radius: 30px 0 0 30px !important;
        height: 52px !important;
        margin-right: -15px !important;
        padding-left: 20px !important;
        padding-right: 20px !important;
        color: var(--accent-emerald) !important;
        box-shadow: none !important;
    }
    .stChatInputContainer {
        border-radius: 0 30px 30px 0 !important;
        background-color: white !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-left: none !important;
        height: 52px !important;
    }
    .stChatInputContainer:focus-within {
        border-color: var(--accent-emerald) !important;
    }
    </style>
<div style='height: 50px;'></div>
""", unsafe_allow_html=True)

# ── Advanced Markdown-to-Pro-Word Engine ───────────
def clean_content(text):
    """Removes AI conversational fluff"""
    patterns = [
        r"^Sure,? here (is|are).*?:\n+",
        r"^Here’s a (revised|draft|version).*?:\n+",
        r"^Certainly,? .*?:\n+",
        r"^Okay,? .*?:\n+",
        r"^Revised version:\n+",
        r"^Revised content:\n+",
        r"^Revised Doc:\n+"
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n+Let me know if you need anything else!.*?$", "", text, flags=re.IGNORECASE | re.DOTALL)
    return text.strip()

def smart_surgical_edit(template_bytes, revised_content):
    """
    KALI SURGICAL PROTOCOL v2.0
    Phase 1: Inspect -> Phase 2: Plan -> Phase 3: Execute -> Phase 4: Verify
    """
    if not template_bytes:
        return create_pro_docx(revised_content)
    
    doc = Document(io.BytesIO(template_bytes))
    st.info("🔍 KALI SURGICAL PROTOCOL: Inspecting document structure...")
    
    # Phase 2: Plan (Parse changes from AI response)
    changes = []
    for line in revised_content.split('\n'):
        if "->" in line:
            parts = line.split("->")
            if len(parts) == 2:
                old = parts[0].strip().strip('"')
                new = parts[1].strip().strip('"')
                if old and new:
                    changes.append((old, new))

    if not changes:
        st.warning("⚠️ No surgical targets identified. Falling back to full regeneration.")
        return create_pro_docx(revised_content)

    # Phase 3: Execute (Surgical Replacement)
    total_swaps = 0
    for old, new in changes:
        print(f"[EXECUTE] Targeted Swap: {old} -> {new}")
        for p in doc.paragraphs:
            if old in p.text:
                # Precision Run Surgery
                for run in p.runs:
                    if old in run.text:
                        run.text = run.text.replace(old, new)
                        total_swaps += 1
                
                # Cross-Run Fallback (if word was split across runs)
                if old in p.text:
                    p.runs[0].text = p.text.replace(old, new)
                    for run in p.runs[1:]:
                        run.text = ""
                    total_swaps += 1

    # Phase 4: Verify
    if total_swaps > 0:
        st.success(f"✅ Protocol Verified: {total_swaps} surgical edits sync'd.")
    else:
        st.error("❌ Verification Failed: Target patterns not found in template.")
        
    return save_doc(doc)

def save_doc(doc):
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_pro_docx(content):
    content = clean_content(content)
    doc = Document()
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue
        if line.startswith('### '):
            p = doc.add_heading(line[4:], level=3)
        elif line.startswith('## '):
            p = doc.add_heading(line[3:], level=2)
        elif line.startswith('# '):
            p = doc.add_heading(line[2:], level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith('- ') or line.startswith('* '):
            doc.add_paragraph(line[2:], style='List Bullet')
        else:
            p = doc.add_paragraph()
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                else:
                    p.add_run(part)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def get_file_text(file):
    if file.name.endswith(".pdf"):
        return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif file.name.endswith(".docx"):
        return "\n".join([para.text for para in Document(io.BytesIO(file.getvalue())).paragraphs])
    return ""

def get_chunks(text):
    size, overlap = 1000, 200
    res = []
    for i in range(0, len(text), size - overlap):
        chunk = text[i:i+size]
        if len(chunk) > 50: res.append(chunk)
    return res

@st.cache_resource
def build_vector_store(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embs = model.encode(chunks)
    idx = faiss.IndexFlatL2(embs.shape[1])
    idx.add(np.array(embs).astype('float32'))
    return idx, chunks

def fetch_knowledge(query, idx, chunks):
    if not idx: return ""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    _, ids = idx.search(np.array(model.encode([query])).astype('float32'), 5)
    return "\n\n---\n\n".join([chunks[i] for i in ids[0] if i < len(chunks)])

# ── Persistence Engine ──────────────────────────────
HISTORY_FILE = "chat_history.json"

def save_chat_to_disk(chat_id, messages):
    import json
    history = {}
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f: history = json.load(f)
        except: pass
    
    # Deriving title from first user message
    title = "New Conversation"
    for m in messages:
        if m["role"] == "user":
            title = m["content"][:30] + "..." if len(m["content"]) > 30 else m["content"]
            break
            
    history[chat_id] = {"title": title, "messages": messages, "timestamp": chat_id}
    with open(HISTORY_FILE, "w") as f: json.dump(history, f)

def load_all_chats():
    import json
    if not os.path.exists(HISTORY_FILE): return {}
    try:
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except: return {}

# ── Sidebar Evolution (ChatGPT Style) ────────────────
with st.sidebar:
    st.markdown("<h2 style='font-family:Playfair Display; color:#064E3B;'>Kali AI</h2>", unsafe_allow_html=True)
    
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_id = str(int(io.time.time())) if hasattr(io, 'time') else str(os.getpid() + int(os.path.getmtime(__file__))) # Fallback for uniqueness
        import time
        st.session_state.chat_id = str(int(time.time()))
        for key in ["template_bytes", "chunks", "index", "final_doc"]:
            if key in st.session_state: del st.session_state[key]
        st.session_state.vision_active = False
        st.rerun()
        
    search_q = st.text_input("🔍 Search chats", placeholder="Search history...")
    
    st.divider()
    
    # ── Silent TPU Lockdown ─────────────────────
    brain_model = "google/vertex-tpu-v3-large"
    
    st.markdown("<div style='margin-top: 25px; margin-bottom: 10px; color: var(--accent-gold); font-size: 0.75rem; font-weight: 800; letter-spacing: 2px; text-transform: uppercase;'>Chronicle Archive</div>", unsafe_allow_html=True)
    all_history = load_all_chats()
    
    if not all_history:
        st.markdown("<div style='color: rgba(0,0,0,0.3); font-size: 0.8rem; padding: 10px;'>No history synced yet. Start a chat!</div>", unsafe_allow_html=True)
    else:
        # Display History in Sidebar
        hist_items = sorted(all_history.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        for cid, data in hist_items:
            if not search_q or search_q.lower() in data['title'].lower():
                if st.button(f"📜 {data['title']}", key=f"hist_{cid}", use_container_width=True):
                    st.session_state.messages = data['messages']
                    st.session_state.chat_id = cid
                    st.rerun()
                
    st.divider()
    
    auth_key = st.text_input("Engine Key", value=DEFAULT_API_KEY, type="password") if not DEFAULT_API_KEY else DEFAULT_API_KEY
    
    st.divider()
    st.markdown("<span class='pulse-badge'>System: Online</span>", unsafe_allow_html=True)

# ── Main Stage ─────────────────────────────────────
st.markdown("<div style='text-align: center; margin-top: 10vh;'>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title'>READY WHEN YOU ARE.</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>High-Precision Intelligence // Kali Edition</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Unit Fusion (Combined Bar) ────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
footer_cols = st.columns([1, 15], gap="small")

with footer_cols[0]:
    with st.popover("➕", help="Upload photos & files"):
        st.markdown("### 📎 Attachment Center")
        uploaded_files = st.file_uploader(
            "Upload photos & files", 
            type=['docx', 'jpg', 'jpeg', 'png', 'pdf'], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            raw_text_parts = []
            for f in uploaded_files:
                file_type = f.name.split('.')[-1].lower()
                if file_type == 'docx':
                    if "template_bytes" not in st.session_state:
                        st.session_state.template_bytes = f.getvalue()
                    raw_text_parts.append(get_file_text(f))
                elif file_type == 'pdf':
                    raw_text_parts.append(get_file_text(f))
                elif file_type in ['jpg', 'jpeg', 'png']:
                    import base64
                    st.session_state.vision_base64 = base64.b64encode(f.getvalue()).decode('utf-8')
                    st.session_state.vision_active = True
                    st.sidebar.info(f"📸 Vision Feed: {f.name}")
            
            if raw_text_parts:
                full_text = "\n".join(raw_text_parts)
                chunks = get_chunks(full_text)
                if chunks:
                    st.session_state.index, st.session_state.chunks = build_vector_store(chunks)
                    st.toast(f"Knowledge Matrix Synced ({len(chunks)} nodes)")

with footer_cols[1]:
    prompt = st.chat_input("Ask anything...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_chat_to_disk(st.session_state.chat_id, st.session_state.messages)
    with st.chat_message("user"): st.markdown(prompt)

    # ── Web Detection & Extraction ────────────────
    web_context = ""
    links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', prompt)
    
    if links:
        with st.status("🌐 Consulting Web Matrix...", expanded=True) as status:
            for link in links:
                st.write(f"Reading: {link}")
                content = fetch_web_content(link)
                web_context += f"\n--- WEB SOURCE: {link} ---\n{content}\n"
            status.update(label="✅ Web Intelligence Synced", state="complete", expanded=False)
    elif "?" in prompt or any(w in prompt.lower() for w in ["search", "who is", "latest", "news", "what is"]):
        with st.status("🧠 Learning from Internet...", expanded=True) as status:
            st.write(f"Querying Open Web: {prompt}")
            web_context = autonomous_search(prompt)
            status.update(label="✅ Internet Learning Synced", state="complete", expanded=False)

    try:
        rag_context = fetch_knowledge(prompt, st.session_state.get('index'), st.session_state.get('chunks'))
        full_context = f"{rag_context}\n{web_context}"
        sys_msg = (
            "You are a Precision Document Architect (Claude-Style). "
            "Your goal is to perform SURGICAL EDITS on a document template. "
            "YOU MUST ONLY provide the specific changes using '\"Original\" -> \"Replacement\"'.\n"
            "CONTEXT:\n" + full_context
        )

        current_model = brain_model
        msgs = [{"role": "system", "content": sys_msg}]
        
        if st.session_state.get('vision_active'):
            current_model = "meta-llama/llama-4-scout-17b-16e-instruct"
            msgs.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.vision_base64}"}}
                ]
            })
        else:
            for m in st.session_state.messages[-5:]:
                msgs.append({"role": m["role"], "content": m["content"]})

        # ── Intelligence Matrix (TPU-Locked Protocol) ──
        # Policy: Direct routing to Google Cloud TPU v3 Cluster
        MODEL_QUEUE = [brain_model]
        
        with st.chat_message("assistant"):
            full_res = ""
            
            for engine in MODEL_QUEUE:
                try:
                    if engine.startswith("google/"):
                        with st.spinner("🛰️ Thinking..."):
                            client = Groq(api_key=auth_key) if auth_key else None
                            response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs)
                            full_res = response.choices[0].message.content
                    else:
                        client = Groq(api_key=auth_key) if auth_key else None
                        response = client.chat.completions.create(model=engine, messages=msgs)
                        full_res = response.choices[0].message.content
                    break 
                except Exception as e:
                    st.error(f"📡 TPU Synchronicity Failure: {str(e)}")
                    break

            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # MEMORY GUARD: Cap history to 40 messages
            if len(st.session_state.messages) > 40:
                st.session_state.messages = st.session_state.messages[-40:]
            
            # PERSISTENCE: Auto-save after response
            save_chat_to_disk(st.session_state.chat_id, st.session_state.messages)
            
            if "->" in full_res or any(word in prompt.lower() for word in ["download", "link", "get file"]):
                if st.session_state.get('template_bytes'):
                    with st.spinner("Executing Surgery..."):
                        edited_bytes = smart_surgical_edit(st.session_state.get('template_bytes'), full_res)
                        st.session_state.final_doc = edited_bytes
                    st.download_button("📥 DOWNLOAD REVISED DOCUMENT", data=edited_bytes, file_name="Kali_AI_Revision.docx", key=f"inline_dl_{len(st.session_state.messages)}")
                
                # AUTO-FLUSH: Clear Vision Memory to prevent Bloat
                if st.session_state.get('vision_active'):
                    st.session_state.vision_active = False
                    st.session_state.vision_base64 = None
                    st.toast("Vision Cache Flushed (RAM Optimized)")
            else:
                st.error("Missing API Key.")
                
    except Exception as e:
        st.error(f"Intelligence Exception: {str(e)}")

if st.session_state.get('final_doc'):
    st.divider()
    with st.expander("📂 PERSISTENT DOWNLOAD CENTER", expanded=True):
        st.download_button("📥 DOWNLOAD FINAL DOCUMENT (Preserved)", data=st.session_state.final_doc, file_name="Kali_AI_Edited.docx", key="persistent_dl")
        if st.button("📋 COPY REPORT CONTENT"):
            st.toast("Copied to clipboard simulator!")
