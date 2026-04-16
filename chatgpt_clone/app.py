import streamlit as st
st.set_page_config(page_title="Kali AI | Intelligence Studio v2", page_icon="DOC", layout="wide")

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
    st.error("INITIALIZATION FAILURE: groq or python-dotenv missing.")
    st.stop()

# PERSISTENCE ENGINE
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
        pass

def load_all_chats():
    try:
        if not os.path.exists(HISTORY_DIR): os.makedirs(HISTORY_DIR)
        if not os.path.exists(HISTORY_FILE): return {}
        with open(HISTORY_FILE, "r") as f: return json.load(f)
    except:
        return {}

def is_safe_url(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']: return False
        hostname = parsed.hostname
        if not hostname: return False
        ip = socket.gethostbyname(hostname)
        parts = list(map(int, ip.split('.')))
        if parts[0] in [127, 10, 172, 192]: return False
        if ip == '169.254.169.254': return False
        return True
    except:
        return False

def clean_content(text):
    patterns = [
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
    KALI TITANIUM SURGICAL ENGINE v18.0 (LXML Precision)
    """
    if not template_bytes:
        return create_pro_docx(revised_content)
    
    import zipfile
    import tempfile
    import shutil
    import io
    import os
    from datetime import datetime
    import re
    from lxml import etree
    
    changes = []
    pattern_quoted = r'(?:["\']{1,3})(.*?)(?:["\']{1,3})\s*(?:\-+|==|=)>\s*(?:["\']{1,3})(.*?)(?:["\']{1,3})(?=\s*["\']|$)'
    matches = re.findall(pattern_quoted, revised_content)
    for old, new in matches:
        if old.strip() and new.strip():
            changes.append((old.strip(), new.strip()))
    
    if not changes:
        fallback_matches = re.findall(r'(?:Original|From|Old):\s*(.*?)\s*(?:-+|==|=)>\s*(?:New|To|Updated):\s*(.*?)(?:\n|$)', revised_content, re.DOTALL | re.IGNORECASE)
        for old, new in fallback_matches:
            changes.append((old.strip(), new.strip()))

    if not changes:
        return template_bytes

    try:
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(io.BytesIO(template_bytes), 'r') as zip_ref:
            zip_ref.extractall(tmp_dir)
            
        xml_targets = []
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(".xml"):
                    xml_targets.append(os.path.join(root, file))
            
        namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        total_swaps = 0
        author = "Kali AI"
        date_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        for xml_path in xml_targets:
            try:
                parser = etree.XMLParser(remove_blank_text=False)
                tree = etree.parse(xml_path, parser)
                root = tree.getroot()
                
                text_nodes = root.xpath('//w:t', namespaces=namespaces)
                for node in text_nodes:
                    if not node.text: continue
                    node_text = node.text
                    
                    for old, new in changes:
                        if old in node_text:
                            parent_r = node.getparent()
                            grandparent = parent_r.getparent() if parent_r is not None else None
                            
                            if grandparent is not None:
                                d_node = etree.Element("{%s}del" % namespaces['w'], 
                                                     attrib={"{%s}id" % namespaces['w']: str(total_swaps),
                                                             "{%s}author" % namespaces['w']: author,
                                                             "{%s}date" % namespaces['w']: date_str})
                                r_old = etree.Element("{%s}r" % namespaces['w'])
                                dt_node = etree.Element("{%s}delText" % namespaces['w'])
                                dt_node.text = old
                                r_old.append(dt_node)
                                d_node.append(r_old)
                                
                                i_node = etree.Element("{%s}ins" % namespaces['w'], 
                                                     attrib={"{%s}id" % namespaces['w']: str(total_swaps+1),
                                                             "{%s}author" % namespaces['w']: author,
                                                             "{%s}date" % namespaces['w']: date_str})
                                i_ptr = etree.Element("{%s}r" % namespaces['w'])
                                t_node = etree.Element("{%s}t" % namespaces['w'])
                                t_node.text = new
                                i_ptr.append(t_node)
                                i_node.append(i_ptr)
                                
                                idx = grandparent.index(parent_r)
                                grandparent.insert(idx, d_node)
                                grandparent.insert(idx + 1, i_node)
                                grandparent.remove(parent_r)
                                total_swaps += 1
                                break
                
                with open(xml_path, 'wb') as f:
                    tree.write(f, encoding='utf-8', xml_declaration=True, standalone='yes')
            except: continue

        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for root_dir, dirs, files in os.walk(tmp_dir):
                for file in files:
                    if file.startswith('.') or file.startswith('_'): continue
                    full_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(full_path, tmp_dir)
                    zip_out.write(full_path, rel_path)
        
        shutil.rmtree(tmp_dir)
        final_bytes = bio.getvalue()
        
        if verify_docx_bytes(final_bytes):
            if total_swaps > 0:
                st.success(f"Titanium LXML Surgery: {total_swaps} Revisions Verified.")
                return final_bytes
            return template_bytes
        else:
            st.error("XML Schema Violation detected. Reverting surgery.")
            return template_bytes

    except Exception as e:
        st.error(f"Surgery Failure: {str(e)}")
        return template_bytes

def create_pro_docx(content):
    content = clean_content(content)
    doc = Document()
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue
        if line.startswith('### '):
            doc.add_heading(line[4:], level=3)
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=2)
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

# MAIN UI
st.title("Kali AI Intelligence Studio v2.0")
st.markdown("### Industrial-Grade Multimodal Analysis & Surgical DOCX Editing")

chats = load_all_chats()
with st.sidebar:
    st.markdown("## Intelligence Feed")
    if chats:
        for cid, info in sorted(chats.items(), reverse=True):
            if st.button(f"Conversation: {info['title'][:15]}", key=cid):
                st.session_state.current_chat_id = cid
                st.session_state.messages = info["messages"]
    if st.button("New Clear Horizon"):
        st.session_state.messages = []
        st.session_state.current_chat_id = str(int(time.time()))
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(int(time.time()))
if "template_doc" not in st.session_state:
    st.session_state.template_doc = None

uploaded_file = st.file_uploader("Upload Knowledge Base (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
if uploaded_file:
    st.session_state.template_doc = uploaded_file.getvalue()
    st.success("Knowledge Base Synchronized.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Initiate deep scan..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        SYSTEM_PROMPT = """You are KALI-V2, an elite industrial AI document engineer.
        When editing DOCX, you MUST use the surgical output format: 'Original' -> 'New'
        Rules:
        1. Always use Tracked Changes format.
        2. Maintain perfect XML architecture."""
        
        try:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "|")
            response_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Neural Core Error: {str(e)}")
            full_response = "Access Denied: Groq API Key required."
            response_placeholder.markdown(full_response)
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_chat_to_disk(st.session_state.current_chat_id, st.session_state.messages)

    if "->" in full_response and st.session_state.template_doc:
        edited_bytes = smart_surgical_edit(st.session_state.template_doc, full_response)
        st.download_button("Download Hardened Intel", data=edited_bytes, file_name="Kali_AI_Report.docx")
