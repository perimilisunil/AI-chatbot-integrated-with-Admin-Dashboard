import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.rag_engine import search_knowledge
from utils.db_handler import get_chat_history, log_message

load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)# type:ignore
    except Exception as e:
        print(f"API Config Error: {e}")

SYSTEM_INSTRUCTION = """
You are 'Fitness Bot', a specialized Fitness and Health Assistant.
Your goal is to help users with workouts, nutrition, and general wellness.

RULES:
1. STRICTLY answer only questions related to Fitness, Health, Nutrition, and Anatomy.
2. If the user asks about coding, politics, or general off-topic chat, politely refuse.
3. Use the provided Context to answer if available.
"""

# --- Model Selection ---
model = None
if api_key:
    try:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)#type: ignore
        print("✅ Model initialized: gemini-2.5-flash")
    except Exception as e:
        print(f"❌ Model Init Error: {e}")

# --- MAIN FUNCTION ---
def get_ai_response(session_id, user_message):
    
    if not model:
        return "Error: Could not connect to Google Gemini. Check your API Key."

    # 1. Save User Message
    log_message(session_id, "user", user_message)
    
    # 2. RAG Search
    try:
        rag_data = search_knowledge(user_message)
        context_text = "\n".join(rag_data) if rag_data else "No specific documents found."
    except Exception as e:
        print(f"RAG Error: {e}")
        context_text = "Error retrieving documents."
    
    # 3. History
    history_rows = get_chat_history(session_id)
    history_formatted = []
    
    for row in history_rows:
        role = "user" if row.role == "user" else "model"
        history_formatted.append({"role": role, "parts": [{"text": row.content}]})
    
    # 4. Generate
    full_prompt = f"Context from Knowledge Base:\n{context_text}\n\nUser Question: {user_message}"
    
    try:
        chat = model.start_chat(history=history_formatted)
        response = chat.send_message(full_prompt)
        ai_text = response.text
    except Exception as e:
        print(f"Gemini Generation Error: {e}")
        ai_text = "I'm having trouble connecting to the AI service right now."
        
    # 5. Save AI Response 
    log_message(session_id, "model", ai_text)
    
    return ai_text
