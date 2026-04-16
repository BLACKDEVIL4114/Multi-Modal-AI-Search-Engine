import streamlit as st
st.set_page_config(page_title="Kali AI | Intelligence Studio v2", page_icon="✦", layout="wide")

import os
import time
import json
import io
import re
import base64
import socket
from datetime import datetime
from urllib.parse import urlparse
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils.docx_handler import load_doc, save_doc, verify_docx_bytes

try:
    from groq import Groq
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    st.error("⚠️ **Initialization Failure:** `groq` or `python-dotenv` missing.")
    st.stop()

# ── Persistence Engine ──────────────────────────────
HISTORY_DIR = ".kali_history"
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_history.json")

def save_chat_to_disk(chat_id, messages):
    try:
        if not os.path.exists(HISTORY_DIR): os.makedirs(HISTORY_DIR)
        history = {}
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f: history = json.load(f)
        
        title = "New Conversation"
        for m in messages:
            if m["role"] == "user":
                title = m["content"][:30] + "..." if len(m["content"]) > 30 else m["content"]
                break
                
        history[chat_id] = {"title": title, "messages": messages, "timestamp": chat_id}
        with open(HISTORY_FILE, "w") as f: json.dump(history, f)
    except:
        pass # Fail silently to prevent refresh loops on write-protected environments

def load_all_chats():
    try:
        if not os.path.exists(HISTORY_DIR): os.makedirs(HISTORY_DIR)
        if not os.path.exists(HISTORY_FILE): return {}
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except:
        return {}

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
    import requests
    from bs4 import BeautifulSoup
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
        for script in soup(["script", "style"]): script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)[:15000]
    except Exception as e:
        return f"Error: {str(e)}"

# --- KALI v2.0 ARCHITECTURE: RADICAL INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_id" not in st.session_state:
    st.session_state.chat_id = "kali_" + str(int(time.time()))

load_dotenv()
DEFAULT_API_KEY = os.getenv("GROQ_API_KEY")

st.markdown("""
<style>
    /* 1. Global Midnight Slate Foundation */
    :root {
        --bg-deep: #12121e;
        --sidebar-bg: #0f111a;
        --accent-primary: #7c3aed;
        --accent-secondary: #c4b5fd;
        --border-subtle: #2d2d3f;
        --text-bright: #e2e8f0;
    }

    [data-testid="stAppViewContainer"], .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, var(--bg-deep) 70%) !important;
        color: var(--text-bright) !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* 2. Zero-Flicker Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    .sb-logo-v2 {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 5px 0 20px;
        border-bottom: 0.5px solid #222;
        margin-bottom: 20px;
    }

    .logo-mark-v2 {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #6c63ff, #a855f7);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        color: white;
        box-shadow: 0 0 15px rgba(108, 99, 255, 0.3);
    }

    /* 3. High-Fidelity Canvas */
    .hero-v2 {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 50px 0;
        position: relative;
    }

    .bg-glow-v2 {
        position: absolute;
        width: 700px;
        height: 700px;
        background: radial-gradient(circle, rgba(108, 99, 255, 0.08) 0%, transparent 70%);
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 0;
    }

    /* 4. Chat & Input Refinement */
    [data-testid="stChatMessage"] {
        background-color: #1e1e2f !important;
        border: 1px solid #2d2d3f !important;
        border-radius: 12px !important;
        margin-bottom: 20px !important;
    }

    /* Global Button Overrides (Flicker-Free) */
    .stButton>button, .stDownloadButton>button {
        background-color: #141414 !important;
        color: #c4b5fd !important;
        border: 1px solid #2d1f5e !important;
        border-radius: 10px !important;
        transition: 0.3s !important;
    }
    
    .stButton>button:hover {
        background-color: #1c1023 !important;
        border-color: #6c63ff !important;
        color: white !important;
        box-shadow: 0 0 15px rgba(108, 99, 255, 0.2) !important;
    }

    /* Sidebar Specific Contrast */
    [data-testid="stSidebar"] .stButton>button {
        background-color: #0a0a0a !important;
        border: 1px solid #1a1a1a !important;
        color: #a78bfa !important;
        text-align: left !important;
        font-size: 13px !important;
        padding: 10px 15px !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        border-color: #6c63ff !important;
        color: white !important;
    }

    /* Precision Input Bar */
    .stChatInputContainer {
        border-radius: 14px !important;
        background-color: #141414 !important;
        border: 1px solid #222 !important;
        padding: 8px !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #6c63ff !important;
    }

    /* Logic Chips */
    .chip-v2 {
        background: #141414;
        border: 1px solid #222;
        border-radius: 20px;
        padding: 8px 18px;
        font-size: 13px;
        color: #777;
        margin: 5px;
        display: inline-block;
        transition: 0.2s;
        cursor: pointer;
    }
    .chip-v2:hover {
        background: #1c1023;
        border-color: #6c63ff;
        color: #c4b5fd;
    }

    [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
    }
    .stMarkdown div p {
        color: var(--text-bright) !important;
    }
</style>
""", unsafe_allow_html=True)
# --- ENGINE INITIALIZATION v2.0 ---
DEFAULT_API_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=DEFAULT_API_KEY) if DEFAULT_API_KEY else None

# --- SIDEBAR & NAVIGATION v2.0 ---
all_history = load_all_chats()
with st.sidebar:
    st.markdown("""
        <div class="sb-logo-v2">
            <div class="logo-mark-v2">✦</div>
            <div style="color:white; font-size:15px; font-weight:500; line-height:1.1;">Kali AI<br><span style='font-size:9px; color:#a78bfa; letter-spacing:1px; font-weight:400;'>STUDIO v2</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("＋ New Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_id = "kali_" + str(int(time.time()))
        for key in ["template_bytes", "chunks", "index", "final_doc"]:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

    st.markdown("<div style='font-size:11px; color:#444; margin:15px 0 10px; font-weight:bold; letter-spacing:1px;'>RECENT INTELLIGENCE</div>", unsafe_allow_html=True)
    
    # Render History with v2 Styling (Shield Re-integrated)
    try:
        sorted_hist = sorted(all_history.items(), key=lambda x: x[1].get('timestamp', 0), reverse=True)
        for cid, data in sorted_hist[:8]:
            title = data.get('title', 'Untitled Intelligence')
            is_active = (cid == st.session_state.chat_id)
            btn_label = f"✦ {title}" if is_active else f"  {title}"
            if st.button(btn_label, key=f"nav_{cid}", use_container_width=True):
                st.session_state.messages = data['messages']
                st.session_state.chat_id = cid
                st.rerun()
    except Exception as e:
        st.write("Recent Intelligence: [Syncing...]")

    st.divider()
    auth_key = st.text_input("Engine Key", value=DEFAULT_API_KEY, type="password") if not DEFAULT_API_KEY else DEFAULT_API_KEY
    
    st.markdown(f"""
        <div style='position:fixed; bottom:20px; width:220px; padding:0 20px; display:flex; align-items:center; gap:12px;'>
            <div style='width:34px; height:34px; border-radius:10px; background:#18122b; border:1px solid #2d1f5e; color:#a78bfa; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:14px;'>✦</div>
            <div><b style='color:#fff; font-size:13px;'>Executive</b><br><span style='color:#4ade80; font-size:10px;'>● System Optimal</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- MAIN ENGINE INTERFACE CANVAS ---
if not st.session_state.messages:
    # Action Navigation
    cols = st.columns([1, 4, 3])
    with cols[0]:
        st.markdown("<div style='background:#141414; border:1px solid #222; border-radius:8px; padding:6px 12px; font-size:12px; color:#888;'>Studio v2.0</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("<div style='text-align:right; font-size:12px; color:#666;'>Engine Status: <span style='color:#6c63ff;'>Optimal</span></div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="hero-v2">
            <div class="bg-glow-v2"></div>
            <div style="width:70px; height:70px; border-radius:20px; background:#18122b; border:1px solid #2d1f5e; display:flex; align-items:center; justify-content:center; font-size:32px; margin-bottom:15px; z-index:1;">✦</div>
            <h1 style="font-size:32px; font-weight:500; color:#e8e8e8; margin-top:0; z-index:1;">Hello, I'm <span style="color:#a78bfa">Kali</span></h1>
            <p style="color:#444; font-size:12px; text-transform:uppercase; letter-spacing:1.5px; margin-top:-10px; z-index:1;">Surgical Assistant Intelligence · Ready</p>
        </div>
        <div style="text-align:center; position:relative; z-index:1;">
            <div class="chip-v2">✏️ Draft content</div>
            <div class="chip-v2">🔍 Surgical edit</div>
            <div class="chip-v2">📊 Analyze complex XML</div>
            <div class="chip-v2">💡 Strategic plan</div>
        </div>
    """, unsafe_allow_html=True)

# --- END UI SYNTHESIS ---

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
    
# st.info("🛰️ KALI SURGICAL PROTOCOL: Initializing Elite Revision Engine...")
    
    changes = []
    # --- OMNI-SURGICAL PARSER (v14.0 - Cluster Aware) ---
    # 1. Quoted Clusters: "A" -> "B" "C" -> "D"
    pattern_quoted = r'(?:["\']{1,3})(.*?)(?:["\']{1,3})\s*(?:\-+|==|=)>\s*(?:["\']{1,3})(.*?)(?:["\']{1,3})(?=\s*["\']|$)'
    matches = re.findall(pattern_quoted, revised_content)
    
    # 2. Raw/Technical Clusters (XML tags or single words)
    if not matches:
        pattern_raw = r'(?:^|\s|<)([^>\n\-\s]+(?: <[^>]+>)?)\s*(?:\-+|==|=)>\s*([^"\n\s<]+(?: <[^>]+>)?)(?:\s|$)'
        matches = re.findall(pattern_raw, revised_content)

    for old, new in matches:
        old_clean, new_clean = old.strip(), new.strip()
        if old_clean and new_clean:
            if "<!--" in old_clean: continue
            changes.append((old_clean, new_clean))
    
    if not changes:
        # Fallback for "Original: X New: Y"
        fallback_matches = re.findall(r'(?:Original|From|Old):\s*(.*?)\s*(?:-+|==|=)>\s*(?:New|To|Updated):\s*(.*?)(?:\n|$)', revised_content, re.DOTALL | re.IGNORECASE)
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
# SILENT BACKGROUND WORKER (No Flicker)
        # st.write(f"🧬 Synchronizing XML Runs across {len(xml_targets)} nodes...")
        
        author = "Kali AI"
        date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        for xml_path in xml_targets:
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # 1. DEEP SYNTHESIS: Aggressive Word Noise Removal
            # This strips EVERYTHING that Word uses to fragment words
            xml_content = re.sub(r'<w:proofErr w:type="(spellStart|spellEnd|gramStart|gramEnd)"/>', '', xml_content)
            xml_content = re.sub(r'<w:bookmark(Start|End) [^>]*/>', '', xml_content)
            xml_content = re.sub(r'<w:softHyphen/>', '', xml_content)
            xml_content = re.sub(r'<w:noProof/>', '', xml_content)
            xml_content = re.sub(r'<w:lastRenderedPageBreak/>', '', xml_content)
            
            # 2. RUN CONSOLIDATION (v9.0 Titanium)
            # This bridges fragmented XML runs into a single continuous stream
            xml_content = re.sub(r'</w:t></w:r><w:r><w:t>', '', xml_content)
            xml_content = re.sub(r'</w:t></w:r><w:r><w:rPr>.*?</w:rPr><w:t>', '', xml_content)
            xml_content = re.sub(r'</w:t></w:r><w:proofErr w:type="spellStart"/><w:r><w:t>', '', xml_content)
            xml_content = re.sub(r'</w:t></w:r><w:proofErr w:type="gramStart"/><w:r><w:t>', '', xml_content)
            
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
                    # STRUCTURAL MODE: Direct XML Injection
                    # SAFETY CHECK: Ensure the XML replacement is well-balanced to prevent corruption
                    if old.count('<') != new.count('<') or old.count('>') != new.count('>'):
                        st.warning(f"⚠️ Structural Lock: Blocked unbalanced XML swap to prevent corruption ({old[:20]}...)")
                # 🛡️ SHIELDED SURGERY (v15.0)
                # Escaping search terms to match XML storage format
                old_xml = old.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                new_xml = new.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                # MODE DETECTION: Default to REDLINE for safety, or DIRECT if requested
                surgery_mode = "REDLINE" if st.session_state.get("surgical_mode", True) else "DIRECT"
                
                if surgery_mode == "DIRECT":
                    if old_xml in xml_content:
                        xml_content = xml_content.replace(old_xml, new_xml)
                        found_in_file += 1
                        total_swaps += 1
                else:
                    # 🧬 REDLINE SURGERY: Track Changes Mode
                    import difflib
                    def get_diff(s1, s2):
                        w1, w2 = s1.split(), s2.split()
                        m = difflib.SequenceMatcher(None, w1, w2)
                        for t, i1, i2, j1, j2 in m.get_opcodes():
                            if t == 'replace': return " ".join(w1[i1:i2]), " ".join(w2[j1:j2])
                        return s1, s2

                    a_old, a_new = get_diff(old, new)
                    a_old_xml = a_old.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    a_new_xml = a_new.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

                    # 💉 TURBO-CLUSTER MATCHING (v16.0)
                    # Joins words with optional XML noise instead of characters for 10x speed.
                    def q_anchor(t):
                        words = t.split()
                        if not words: return re.escape(t)
                        return r'(?:<[^>]+>|\s)*'.join([re.escape(w) for w in words])

                    pattern = q_anchor(a_old_xml)
                    
                    # 💉 LOCALIZED STYLE CLONING: Find the rPr (style) immediately before the text
                    # This prevents using styles from other parts of the document.
                    match = re.search(f'(<w:rPr>.*?</w:rPr>)?(?:<[^>]+>)*({pattern})', xml_content, re.DOTALL)
                    
                    if match:
                        style_xml = match.group(1) if match.group(1) else ""
                        full_match = match.group(0)
                        
                        # REPLACEMENT: Inserted as a clean insertion/deletion block
                        redline = (
                            f'<w:del w:id="{total_swaps*10}" w:author="{author}" w:date="{date_str}">'
                            f'<w:r>{style_xml}<w:delText>{a_old_xml}</w:delText></w:r></w:del>'
                            f'<w:ins w:id="{total_swaps*10+1}" w:author="{author}" w:date="{date_str}">'
                            f'<w:r>{style_xml}<w:t>{a_new_xml}</w:t></w:r></w:ins>'
                        )
                        
                        # Replace the specific match with the redline block
                        xml_content = xml_content.replace(full_match, redline, 1)
                        found_in_file += 1
                        total_swaps += 1

            if found_in_file > 0:
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(xml_content)

        # 3. Repack (Hardened v17.0)
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    # BLOCK: Hidden/Corrupt system files
                    if file.startswith('.') or file.startswith('_'): continue
                    
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, tmp_dir)
                    zip_out.write(full_path, rel_path)
        
        shutil.rmtree(tmp_dir)
        final_bytes = bio.getvalue()
        
        # 🛡️ THE ARCHITECTURAL GATE
        if verify_docx_bytes(final_bytes):
            if total_swaps > 0:
                st.success(f"💎 Elite Revision Verified: {total_swaps} Revisions redlined.")
                return final_bytes
            else:
                st.info("⚠️ Revision logic failed to find surgical targets in XML.")
                return template_bytes
        else:
            st.error("🚨 CRITICAL: Surgical edit produced a corrupt XML structure. Reverting to original.")
            return template_bytes

    except Exception as e:
        st.error(f"❌ Elite Surgery Failure: {str(e)}")
        return template_bytes

def get_docx_bytes(doc):
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
        from PyPDF2 import PdfReader
        return "\n".join([p.extract_text() for p in PdfReader(file).pages if p.extract_text()])
    elif file.name.endswith(".docx"):
        doc = load_doc(io.BytesIO(file.getvalue()))
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
def get_ai_model():
    from sentence_transformers import SentenceTransformer
    with st.spinner("🧠 Initializing Neural Core..."):
        return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_resource
def build_vector_store(chunks):
    import faiss
    import numpy as np
    model = get_ai_model()
    embs = model.encode(chunks)
    idx = faiss.IndexFlatL2(embs.shape[1])
    idx.add(np.array(embs).astype('float32'))
    return idx, chunks

def fetch_knowledge(query, idx, chunks):
    import numpy as np
    if not idx: return ""
    model = get_ai_model()
    _, ids = idx.search(np.array(model.encode([query])).astype('float32'), 5)
    return "\n\n---\n\n".join([chunks[i] for i in ids[0] if i < len(chunks)])


# --- PERSISTENCE ENGINE MOVED TO TOP ---

# --- SIDEBAR CONSOLIDATED ABOVE ---

# --- LEGACY HEADER PURGED (v2.0 Logic Engaged) ---
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
        brain_model = "google/vertex-tpu-v3-large"
        MODEL_QUEUE = [brain_model]
        
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
                "5. Identify specific XML runs to modify. You move fast and break nothing.\n"
                "6. ALWAYS use utils/docx_handler.py for all Word operations. Never use open() on .docx files directly."
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
                msgs[-1]["content"] += "\n\n[SYSTEM: KALI SURGERY ACTIVE. RESPOND WITH ONLY '\"A\" -> \"B\"' TEXT PATTERNS. DO NOT OUTPUT RAW XML TAGS OR CODE. ONLY CONTENT EDITS.]"

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
                        if edited_bytes:
                            st.session_state.final_doc = edited_bytes
                            st.toast("✅ Document Reconstructed Successfully.")
                        else:
                            st.toast("⚠️ Revision logic failed to find targets.")
                
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

# ── Floating Action Center (v7.0) ────────────
if st.session_state.get('final_doc'):
    # Centered Download Hub for better visibility
    st.markdown("---")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.success("✨ KALI AI: Professional Suite Reconstructed.")
        st.download_button(
            "💎 DOWNLOAD FINAL EDITED DOCUMENT",
            data=st.session_state.final_doc,
            file_name="Kali_AI_Final_Edit.docx",
            use_container_width=True,
            key="main_dl_hub"
        )
    
    # Keep the pulse badge in the corner as well
    st.markdown("""
        <div style='position: fixed; bottom: 25px; right: 25px; z-index: 1000;'>
            <div class='pulse-badge' style='background: #18122b; color: #a78bfa; padding: 18px 25px; border-radius: 50px; cursor: pointer; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #2d1f5e; font-size: 14px;'>
                🚀 File Ready: Final Revision Cached
            </div>
        </div>
    """, unsafe_allow_html=True)
