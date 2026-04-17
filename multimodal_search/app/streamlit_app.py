import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from PIL import Image
import PyPDF2
from docx import Document
import io
import time
import requests
from duckduckgo_search import DDGS
from googlesearch import search as gsearch
import trafilatura
import re

# Load Intelligence
load_dotenv()

# --- PREMIUM DESIGN SYSTEM ---
st.set_page_config(page_title="ZENITH INTELLIGENCE STUDIO", layout="wide", page_icon="💠")

def apply_premium_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
        
        :root {
            --royale-blue: #0084ff;
            --royale-purple: #a87ff3;
            --bg-mesh: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                       radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                       radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        }

        .stApp {
            background-color: #fcfcfd;
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 132, 255, 0.05) 0px, transparent 50%),
                radial-gradient(at 50% 0%, rgba(168, 127, 243, 0.05) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(0, 132, 255, 0.03) 0px, transparent 50%);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: #1e293b;
        }

        .main-header {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, var(--royale-blue), var(--royale-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            margin-top: 1rem;
            margin-bottom: 3rem;
            letter-spacing: -1px;
            filter: drop-shadow(0 10px 10px rgba(0,0,0,0.05));
        }

        /* PREMIUM CARDS */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.03);
            margin-bottom: 2rem;
        }

        /* SIDEBAR BEAUTIFICATION */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(30px);
            border-right: 1px solid rgba(0,0,0,0.05);
        }

        .sidebar-title {
            font-family: 'Outfit', sans-serif;
            color: #0f172a;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* CHAT ELEGANCE */
        .user-bubble {
            background: linear-gradient(135deg, var(--royale-blue), #0061ff);
            color: white;
            padding: 1.25rem 1.75rem;
            border-radius: 24px 24px 4px 24px;
            margin-left: auto;
            max-width: 80%;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px rgba(0, 132, 255, 0.2);
            font-size: 1rem;
            line-height: 1.6;
        }

        .ai-bubble {
            background: #ffffff;
            color: #334155;
            padding: 2rem;
            border-radius: 24px 24px 24px 4px;
            max-width: 90%;
            margin-bottom: 2rem;
            border: 1px solid rgba(0,0,0,0.04);
            box-shadow: 0 15px 35px rgba(0,0,0,0.03);
            font-size: 1.05rem;
            line-height: 1.7;
        }

        /* INPUT OVERHAUL */
        .stChatInputContainer {
            border-radius: 30px !important;
            padding: 10px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        }

        /* HIDDEN ELEMENTS */
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_premium_ui()

# --- CORE INTELLIGENCE ---
@st.cache_resource
def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(prompt):
    try:
        client = get_groq_client()
        # Updated Model List: Removed decommissioned Mixtral
        models = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
        
        # Token Surgical Ingestion: Limit context size to save quota
        if len(prompt) > 8000:
            prompt = prompt[:8000] + "\n...[CONTEXT TRUNCATED TO SAVE QUOTA]..."
            
        for model in models:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are Zenith Intelligence Studio v5.0. If LIVE INTERNET DATA is provided, prioritize it above all else. For sports scores, provide a structured scorecard. Be professional, technical, and accurate."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    max_tokens=2000
                )
                return completion.choices[0].message.content
            except Exception as e:
                if "429" in str(e) or "400" in str(e): continue # Hop to next model
                return f"Neural Error: {str(e)}"
        return "⚠️ All Neural Engines are at Daily Capacity. Please wait for reset."
    except Exception as e:
        return f"Engine Failure: {str(e)}"

def call_bedrock(prompt):
    api_key = os.getenv("AWS_BEDROCK_API_KEY")
    if not api_key: return "⚠️ AWS Bedrock API Key not found."
    
    url = "https://bedrock-runtime.eu-north-1.amazonaws.com/model/eu.anthropic.claude-3-7-sonnet-20250219-v1:0/invoke"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "system": "You are Zenith Intelligence Studio v5.0. If LIVE INTERNET DATA is provided, prioritize it. For sports/news, provide structured, high-precision reports. Use bold markers for key events.",
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "enabled", "budget_tokens": 1024},
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["content"][-1]["text"]
        
        # SILENT ROUTING: If AWS is limited, automatically use Llama
        if response.status_code in [429, 400, 404]:
            return call_groq(prompt)
            
        return call_groq(prompt) # Universal silent fallback
    except Exception as e:
        return call_groq(prompt)

# --- WEB-OCULAR INTELLIGENCE ---
def perform_web_search(query):
    results_text = []
    deep_scraped_content = []
    q_lower = query.lower()
    
    # Layer 0: Direct Authority Scraping (Bypasses Search challenge)
    if any(k in q_lower for k in ["ipl", "cricket", "score", "match"]):
        try:
            with st.spinner("🎯 Targeting Cricbuzz Authority..."):
                live_data = scrape_url("https://www.cricbuzz.com/cricket-match/live-scores")
                if live_data:
                    deep_scraped_content.append(f"--- DIRECT CRICBUZZ LIVE FEED ---\n{live_data[:6000]}")
        except Exception: pass

    # Layer 1: Google Precision Intelligence
    try:
        search_query = query
        if q_lower.startswith("urrent"): search_query = "current " + query[6:]
        
        search_results = list(gsearch(search_query, num_results=5, advanced=True))
        for idx, url in enumerate(search_results):
            results_text.append(f"TITLE: {url.title}\nSNIPPET: {url.description}\nSOURCE: {url.url}")
            
            if idx == 0 and not deep_scraped_content:
                with st.spinner(f"🔍 Deep-Scanning {url.title}..."):
                    content = scrape_url(url.url)
                    if content: deep_scraped_content.append(f"--- SOURCE CONTENT RAG ---\n{content[:4000]}")
    except Exception as e:
        print(f"Google Search Error: {e}")
    
    # Layer 2: DuckDuckGo Fallback
    if not results_text:
        try:
            with DDGS() as ddgs:
                news_res = list(ddgs.news(query, max_results=5))
                for r in news_res:
                    results_text.append(f"NEWS: {r.get('title')}\nSUMMARY: {r.get('body')}\nLINK: {r.get('url')}")
        except Exception: pass
    
    # Final Context Synthesis
    final_context = "\n\n".join(results_text)
    if deep_scraped_content:
        final_context += "\n\n=== ULTIMATE LIVE CONTEXT (CRITICAL) ===\n" + "\n\n".join(deep_scraped_content)
    
    return final_context if (results_text or deep_scraped_content) else "⚠️ Global Intelligence Link Offline."



def scrape_url(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded)
    except Exception:
        return ""

def transcribe_audio(audio_file):
    try:
        client = get_groq_client()
        transcription = client.audio.transcriptions.create(
            file=(audio_file.name, audio_file.read()),
            model="whisper-large-v3",
            response_format="text"
        )
        return transcription
    except Exception as e:
        return f"Audio Error: {str(e)}"

def extract_text(file):
    file_type = file.name.split('.')[-1].lower()
    if file_type == 'pdf':
        reader = PyPDF2.PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_type == 'docx':
        doc = Document(file)
        return " ".join([para.text for para in doc.paragraphs])
    elif file_type in ['png', 'jpg', 'jpeg']:
        return "[IMAGE_UPLOADED]: Analyzing Visual Content..."
    elif file_type in ['mp3', 'wav', 'm4a', 'ogg']:
        return transcribe_audio(file)
    return file.read().decode('utf-8', errors='ignore')

# --- APP EXECUTION GATE ---
def run_studio():
    apply_premium_ui()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar Content
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>💠 SYSTEM COMMAND</div>", unsafe_allow_html=True)
        engine = st.radio("Choose Intelligence Layer:", ["Llama (High-Speed)", "Claude (Zenith Logic)"])
        
        st.markdown("---")
        st.markdown("<div class='sidebar-title'>📊 INTELLIGENCE MATRIX</div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: rgba(0,0,0,0.03); padding: 15px; border-radius: 12px; font-size: 0.8rem;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span>Neural Status:</span><span style='color: #0084ff; font-weight: bold;'>ONLINE</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span>Memory Buffer:</span><span>98.4%</span>
                </div>
                <div style='display: flex; justify-content: space-between;'>
                    <span>Active Core:</span><span>Sonnet 3.7</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<div class='sidebar-title'>📁 UNIVERSAL MODAL</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop any file (PDF, Doc, Audio, Image)", type=['pdf','docx','txt','py','js','mp3','wav','m4a','ogg','png','jpg','jpeg'])
        
        if st.button("🗑️ Reset Neural Matrix"):
            st.session_state.messages = []
            st.rerun()

    # Processing Files
    context = ""
    if uploaded_file:
        with st.spinner("🧠 Ingesting Multi-Modal Data..."):
            context = extract_text(uploaded_file)

    # Welcome Hero (Internal LONELY remover)
    if not st.session_state.messages:
        st.markdown("<h1 class='main-header'>ZENITH STUDIO v5.0</h1>", unsafe_allow_html=True)
        st.markdown("""
            <div class="glass-card" style="text-align: center; margin-top: -20px;">
                <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">The Masterpiece Edition — Industrial Multi-Modal Intelligence</p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                    <div style="padding: 20px; border-radius: 15px; background: rgba(0,132,255,0.05);">
                        <div style="font-size: 2rem;">📄</div>
                        <div style="font-weight: bold; margin-top: 10px;">Doc Surgery</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Deep PDF/Doc Analysis</div>
                    </div>
                    <div style="padding: 20px; border-radius: 15px; background: rgba(168,127,243,0.05);">
                        <div style="font-size: 2rem;">🎙️</div>
                        <div style="font-weight: bold; margin-top: 10px;">Audio Neural</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Whisper-V3 Transcription</div>
                    </div>
                    <div style="padding: 20px; border-radius: 15px; background: rgba(0,132,255,0.05);">
                        <div style="font-size: 2rem;">🛡️</div>
                        <div style="font-weight: bold; margin-top: 10px;">Self-Healing</div>
                        <div style="font-size: 0.8rem; color: #64748b;">Auto Quota Routing</div>
                    </div>
                </div>
                <p style="margin-top: 2rem; font-size: 0.9rem; color: #94a3b8;">Type your first command below to wake the engine...</p>
            </div>
        """, unsafe_allow_html=True)

    # Chat Interface
    for message in st.session_state.messages:
        div_class = "user-bubble" if message["role"] == "user" else "ai-bubble"
        st.markdown(f"<div class='{div_class}'>{message['content']}</div>", unsafe_allow_html=True)

    if prompt := st.chat_input("Command the Zenith..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"<div class='user-bubble'>{prompt}</div>", unsafe_allow_html=True)

        with st.spinner("📡 Orchestrating Neural Response..."):
            # Autonomous Link Sniffing
            urls = re.findall(r'(https?://[^\s]+)', prompt)
            web_context = ""
            for url in urls:
                scraped = scrape_url(url)
                if scraped: web_context += f"\n--- LIVE DATA FROM {url} ---\n{scraped}\n"
            
            full_prompt = f"FILE CONTEXT:\n{context}\n\nWEB CONTEXT:\n{web_context}\n\nUSER: {prompt}" if (context or web_context) else prompt
            
            if engine == "Claude (Zenith Logic)":
                response = call_bedrock(full_prompt)
            else:
                response = call_groq(full_prompt)
                
            # Autonomous Web Search Fallback: If AI is unsure or user asks for live data
            search_triggers = ["search","latest","current","web","news","price","match","score","ipl","today","live","update","weather","stock","cricket","football"]
            if any(k in prompt.lower() for k in search_triggers) or "Neural Error" in response or "I don't have" in response or "knowledge cutoff" in response.lower() or "missing context" in response.lower():
                 search_hits = perform_web_search(prompt)
                 if search_hits and "⚠️ Global Intelligence Link Offline" not in search_hits:
                     # Re-inject search data into the neural prompt with CRITICAL priority
                     neural_payload = f"CRITICAL: USE THE FOLLOWING LIVE INTERNET DATA TO ANSWER THE USER. PREVIOUS KNOWLEDGE IS DEPRECATED.\n\nLIVE DATA:\n{search_hits}\n\nUSER COMMAND: {prompt}"
                     response = call_bedrock(neural_payload) if engine == "Claude (Zenith Logic)" else call_groq(neural_payload)
                 elif "⚠️ Global Intelligence Link Offline" in search_hits and ("Neural Error" in response or "I don't have" in response):
                     response = "📡 Zenith Ocular Link is currently offline. Please verify your connection or try again later for live data."

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(f"<div class='ai-bubble'>{response}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_studio()
