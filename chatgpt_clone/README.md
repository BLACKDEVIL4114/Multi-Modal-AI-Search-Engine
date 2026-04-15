# My AI Assistant+ (ChatGPT Clone)

A lightweight ChatGPT-style application built with Streamlit and the Groq API.

## Features
- **Fast Chat**: Powered by Llama 3 for near-instant responses.
- **PDF Interaction**: Upload any PDF to ask questions about its content.
- **Conversation Memory**: Remembers your previous messages in the current session.
- **Streaming Responses**: Clean UI where text appears as it is generated.
- **Sidebar Config**: Easily switch models or clear chat history.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key**:
   - Rename `.env.example` to `.env` (if applicable) or edit the `.env` file.
   - Add your Groq API key: `GROQ_API_KEY=gsk_...`
   - *Alternatively, you can paste the key directly into the sidebar of the app.*

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## How to use PDF Mode
1. Open the sidebar.
2. Click "Browse files" under PDF Knowledge.
3. Once the text is extracted, the AI will use that information to answer your questions.
