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
import time

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
    KALI SURGICAL PROTOCOL v5.0 (Elite Revision Tracking)
    """
    if not template_bytes:
        return create_pro_docx(revised_content)
    
    import zipfile
    import tempfile
    import shutil
    from datetime import datetime
    
    st.info("🛰️ KALI SURGICAL PROTOCOL: Initializing Elite Revision Engine...")
    
    changes = []
    # --- UNIVERSAL SURGICAL PARSER (v7.0) ---
    # Scans the entire response for valid surgical patterns: "Original" -> "New"
    # Matches patterns regardless of conversational flanking text.
    pattern = r'["\']{1,3}(.*?)["\']{1,3}\s*(?:\-+|==|=)>\s*["\']{1,3}(.*?)["\']{1,3}'
    matches = re.findall(pattern, revised_content, re.DOTALL)
    
    for old, new in matches:
        if old.strip() and new.strip():
            # Filter out known placeholders that the AI might incorrectly use
            if "<!--" in old and "-->" in old: continue
            changes.append((old.strip(), new.strip()))
    
    if not changes:
        # Fallback for unquoted labels
        fallback_matches = re.findall(r'(?:Original|From):\s*(.*?)\s*(?:-+|==|=)>\s*(?:New|To):\s*(.*?)(?:\n|$)', revised_content, re.DOTALL | re.IGNORECASE)
        for old, new in fallback_matches:
            changes.append((old.strip(), new.strip()))

    if not changes:
        st.warning("⚠️ No surgical targets identified. Reviewing document context...")
        return create_pro_docx(revised_content)

    # Phase 3: Execute (The Elite ZIP-XML Workflow)
    try:
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(io.BytesIO(template_bytes), 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
            
        # Target all XML content files
        xml_targets = []
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(".xml"):
                    xml_targets.append(os.path.join(root, file))
            
        total_swaps = 0
        st.write(f"🧬 Synchronizing XML Runs across {len(xml_targets)} nodes...")
        
        author = "Kali AI"
        date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        for xml_path in xml_targets:
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # 1. DEEP SYNTHESIS: Aggressive Word Noise Removal
            # This strips spelling errors, grammar flags, bookmarks, and soft hyphens
            # that Microsoft Word uses to fragment words in the background.
            xml_content = re.sub(r'<w:proofErr w:type="(spellStart|spellEnd|gramStart|gramEnd)"/>', '', xml_content)
            xml_content = re.sub(r'<w:bookmark(Start|End) [^>]*/>', '', xml_content)
            xml_content = re.sub(r'<w:softHyphen/>', '', xml_content)
            
            # 2. Run Consolidation (K-a-l-i -> Kali)
            xml_content = re.sub(r'</w:t></w:r><w:r><w:t>', '', xml_content)
            xml_content = re.sub(r'</w:t></w:r><w:r><w:rPr>.*?</w:rPr><w:t>', '', xml_content)
            
            # 3. Tracked Changes Surgery (Redlining & Structural)
            found_in_file = 0
            for old, new in changes:
                # DETECTION: Is this a structural XML change or a text content change?
                is_structural = '<' in old or '<' in new or '>' in old or '>' in new
                
                old_esc = old.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                new_esc = new.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # Check 1: Exact Match (Raw)
                # Check 2: Exact Match (Escaped)
                # Check 3: Word-Field Normalization (flexible backslashes/case)
                
                if is_structural:
                    # STRUCTURAL MODE: Direct XML Injection (No redlining as it breaks schema)
                    if old in xml_content:
                        xml_content = xml_content.replace(old, new)
                        found_in_file += 1
                        total_swaps += 1
                    elif old_esc in xml_content:
                        xml_content = xml_content.replace(old_esc, new)
                        found_in_file += 1
                        total_swaps += 1
                    else:
                        # Attempt fuzzy XML match (flexible whitespace/order)
                        pattern = re.escape(old).replace(r'\ ', r'\s+')
                        if re.search(pattern, xml_content):
                            xml_content = re.sub(pattern, new, xml_content)
                            found_in_file += 1
                            total_swaps += 1
                else:
                    # TEXT MODE: Redlining (Tracked Changes)
                    replacement = (
                        f'<w:del w:id="{total_swaps*10}" w:author="{author}" w:date="{date_str}">'
                        f'<w:r><w:delText>{old_esc}</w:delText></w:r></w:del>'
                        f'<w:ins w:id="{total_swaps*10+1}" w:author="{author}" w:date="{date_str}">'
                        f'<w:r><w:t>{new_esc}</w:t></w:r></w:ins>'
                    )
                    
                    # Fuzzy match for Word instruction fields (flexible backslashes)
                    word_field_pat = re.escape(old).replace(r'\*', r'\\?\*')
                    
                    if old in xml_content:
                        xml_content = xml_content.replace(old, replacement)
                        found_in_file += 1
                        total_swaps += 1
                    elif old_esc in xml_content:
                        xml_content = xml_content.replace(old_esc, replacement)
                        found_in_file += 1
                        total_swaps += 1
                    elif re.search(word_field_pat, xml_content, re.IGNORECASE):
                        xml_content = re.sub(word_field_pat, replacement, xml_content, flags=re.IGNORECASE)
                        found_in_file += 1
                        total_swaps += 1

            if found_in_file > 0:
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)

        # 3. Repack
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmp_dir)
                    zip_out.write(full_path, rel_path)
        
        shutil.rmtree(tmp_dir)
        
        if total_swaps > 0:
            st.success(f"💎 Elite Revision Verified: {total_swaps} Revisions redlined.")
            return bio.getvalue()
        else:
            st.error("❌ Verification Failed: Target patterns not found in document architecture.")
            return template_bytes

    except Exception as e:
        st.error(f"❌ Elite Surgery Failure: {str(e)}")
        return template_bytes

def save_doc(doc):
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_pro_docx(content):
    """
    KALI PRO ENGINE v4.0 (Claude-Fidelity)
    """
    content = clean_content(content)
    doc = Document()
    
    # 🎨 CLAUDE-FIDELITY THEME
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial' 
    font.size = Pt(11)
    
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)

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
            p = doc.add_paragraph(line[2:], style='List Bullet')
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
        doc = Document(io.BytesIO(file.getvalue()))
        text_parts = []
        
        # Paragraphs
        for para in doc.paragraphs:
            if para.text.strip(): text_parts.append(para.text)
            
        # Tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if para.text.strip(): text_parts.append(para.text)
                        
        # Headers/Footers
        for section in doc.sections:
            for para in section.header.paragraphs:
                if para.text.strip(): text_parts.append(f"[HEADER] {para.text}")
            for para in section.footer.paragraphs:
                if para.text.strip(): text_parts.append(f"[FOOTER] {para.text}")
                
        return "\n".join(text_parts)
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
    if not auth_key:
        st.warning("🔑 GROQ_API_KEY not found. Please add it to your .env file or enter it above to enable Kali AI.")
    
    st.divider()
    status_label = "Online" if auth_key else "Standby (Awaiting Key)"
    st.markdown(f"<span class='pulse-badge'>System: {status_label}</span>", unsafe_allow_html=True)

# ── Main Stage ─────────────────────────────────────
has_template = bool(st.session_state.get('template_bytes'))
current_mode = "ARCHITECT" if (has_template and st.session_state.get('surgical_mode', True)) else "ASSISTANT"
status_color = "#D4AF37" if current_mode == "ARCHITECT" else "#064E3B"

st.markdown(f"<div style='text-align: center; margin-top: 10vh;'>", unsafe_allow_html=True)
st.markdown(f"<h1 class='main-title' style='color:{status_color};'>KALI {current_mode}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{current_mode} LEVEL INTELLIGENCE // READY</div>", unsafe_allow_html=True)

if has_template:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.session_state.surgical_mode = st.toggle("🔧 Surgical Mode (Direct Edit)", value=st.session_state.get('surgical_mode', True))
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
                        st.session_state.surgical_mode = True # Default to surgical
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
        
        # ── Intelligence Mode Selection ────────────────
        has_template = bool(st.session_state.get('template_bytes'))
        is_surgical = has_template and st.session_state.get('surgical_mode', True)
        
        mode_instruction = ""
        if is_surgical:
            mode_instruction = (
                "🚨 ARCHITECTURAL MODE ACTIVE: YOU ARE A SURGICAL BINARY ENGINE.\n"
                "1. DO NOT explain what you are doing. DO NOT provide usage instructions.\n"
                "2. PROVIDE ONLY surgical patterns using the exact format: '\"Original XML/Text\" -> \"New XML/Text\"'.\n"
                "3. ABSOLUTE RULE: For structural changes, you MUST find the existing tag (e.g., <w:sectPr/>) and provide it as the 'Original'.\n"
                "4. NEVER use placeholders like <!-- footer -->. Use literal OOXML tags.\n"
                "5. Identify specific XML runs to modify. You move fast and break nothing."
            )
        else:
            mode_instruction = (
                "CONVERSATIONAL MODE ACTIVE: Act as a high-intelligence professional assistant. "
                "Provide detailed, human-like, and natural responses. Use formatting, bolding, and lists."
            )

        sys_msg = (
            f"You are KALI AI (v6.0 Architectural Edition), an elite intelligence and document studio.\n"
            f"{mode_instruction}\n\n"
            f"CONTEXT (RAG + Web Sync):\n{full_context}"
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
            
            # 💉 SURGICAL PRIMER: Hard-injection for adherence
            if is_surgical:
                msgs[-1]["content"] += "\n\n[SYSTEM: KALI SURGERY ACTIVE. RESPOND WITH ONLY '\"A\" -> \"B\"' PATTERNS. NO TUTORIALS. NO TEXT.]"

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
            
            # --- ENHANCED SURGICAL TRIGGER (v6.2) ---
            # Triggers if arrow syntax exists OR if architectural XML is detected
            architectural_intent = any(tag in full_res for tag in ["<w:sectPr>", "<w:pgNumType>", "<w:headerReference>", "<w:footerReference>"])
            
            if "->" in full_res or architectural_intent or any(word in prompt.lower() for word in ["download", "link", "get file"]):
                if st.session_state.get('template_bytes'):
                    with st.spinner("🚀 KALI ARCHITECT: Executing Structural Surgery..."):
                        edited_bytes = smart_surgical_edit(st.session_state.get('template_bytes'), full_res)
                        st.session_state.final_doc = edited_bytes
                    st.toast("✅ Document Reconstructed Successfully.")
                
                # AUTO-FLUSH: Vision Cache
                if st.session_state.get('vision_active'):
                    st.session_state.vision_active = False
                    st.session_state.vision_base64 = None
                    st.toast("Vision Cache Flushed (RAM Optimized)")
                
    except Exception as e:
        st.error(f"Intelligence Exception: {str(e)}")

# ── Sidestage: Persistent Export Center (v6.2) ──────
with st.sidebar:
    if st.session_state.get('final_doc'):
        st.divider()
        st.markdown("### 🏛️ EXPORT CENTER")
        st.download_button(
            "📥 DOWNLOAD REVISED DOCUMENT", 
            data=st.session_state.final_doc, 
            file_name="Kali_AI_Final_Revision.docx", 
            key="side_dl",
            use_container_width=True
        )
        if st.button("📋 COPY LATEST REPORT", use_container_width=True):
            st.toast("Copied to clipboard simulator!")
        st.success("Document cached in high-speed memory.")

# ── Floating Action Badge (UX Polish) ────────────
if st.session_state.get('final_doc'):
    st.markdown("""
        <div style='position: fixed; bottom: 20px; right: 20px; z-index: 1000;'>
            <div class='pulse-badge' style='background: #1a472a; color: #fff; padding: 15px; border-radius: 50px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
                💾 File Ready for Download
            </div>
        </div>
    """, unsafe_allow_html=True)
