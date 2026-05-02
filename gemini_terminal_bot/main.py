import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Ensure you have GEMINI_API_KEY in your .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gemini 2.0 Flash with Google Search Grounding enabled
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[{"google_search_retrieval": {}}] # Correct format for tools
)

def ask(question: str):
    try:
        response = model.generate_content(question)
        print("\nAnswer:", response.text)
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("🚀 Gemini Search Bot Initialized (Type 'exit' to quit)")
    while True:
        q = input("\nAsk anything: ")
        if q.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        if q.strip():
            ask(q)
