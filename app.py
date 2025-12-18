import sys
import os

# --- SQLITE FIX FOR CLOUD DEPLOYMENTS ---
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    print("✅ Cloud Mode: Using pysqlite3")
except ImportError:
    print("✅ Local Mode: Using standard sqlite3")

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import uuid

# --- PDF HANDLING ---
try:
    import pypdf
    import io
except ImportError:
    pypdf = None
    print("WARNING: pypdf not installed.")

# --- CUSTOM MODULES ---
# Removed 'get_sentiment_stats' from imports
from utils.db_handler import init_db, get_analytics, get_all_logs, delete_chat_log, get_chat_history, db
from utils.ai_handler import get_ai_response
from utils.rag_engine import add_document_to_knowledge, get_all_documents, delete_document_by_id

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# --- DATABASE INITIALIZATION ---
init_db(app)

# --- MIDDLEWARE ---
@app.before_request
def assign_session():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

# --- USER ROUTES ---

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/api/history', methods=['GET'])
def get_history_api():
    session_id = session.get('user_id')
    history = get_chat_history(session_id, limit=50)
    
    json_history = []
    for row in history:
        json_history.append({
            'role': row.role,
            'content': row.content
        })
        
    return jsonify(json_history)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_message = data['message']
    session_id = session.get('user_id')
    
    # REMOVED: TextBlob/Sentiment Analysis logic here to save RAM
    
    # AI Handler logs the messages internally now
    bot_response = get_ai_response(session_id, user_message)
    return jsonify({'response': bot_response})

# --- ADMIN ROUTES ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv("ADMIN_PASSWORD", "admin123"):
            session['is_admin'] = True
            return redirect('/admin/dashboard')
        else:
            return "Invalid Password", 401
    return render_template('login.html')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('is_admin'):
        return redirect('/admin/login')
    
    stats = get_analytics()
    logs = get_all_logs()
    knowledge = get_all_documents()
    # REMOVED: mood = get_sentiment_stats()
    
    return render_template('dashboard.html', stats=stats, logs=logs, knowledge=knowledge)

# UPLOADS
@app.route('/admin/upload', methods=['POST'])
def upload_knowledge():
    if not session.get('is_admin'): return jsonify({'error': 'Unauthorized'}), 401
    
    text = request.form.get('knowledge_text', '')
    
    if 'pdf_file' in request.files:
        file = request.files['pdf_file']
        if file.filename != '':
            try:
                file_stream = io.BytesIO(file.read())
                pdf_reader = pypdf.PdfReader(file_stream)#type: ignore
                pdf_text = ""
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content: pdf_text += content + "\n"
                
                if pdf_text:
                    text = (text or "") + "\n\n" + pdf_text
            except Exception as e:
                print(f"PDF Error: {e}")
                return "Error reading PDF", 500

    if text and text.strip():
        add_document_to_knowledge(text)
        return redirect('/admin/dashboard')
    
    return "No content provided", 400

# DELETIONS
@app.route('/admin/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    if not session.get('is_admin'): return jsonify({'error': 'Unauthorized'}), 401
    delete_chat_log(log_id)
    return redirect('/admin/dashboard')

@app.route('/admin/delete_knowledge/<doc_id>', methods=['POST'])
def delete_knowledge(doc_id):
    if not session.get('is_admin'): return jsonify({'error': 'Unauthorized'}), 401
    delete_document_by_id(doc_id)
    return redirect('/admin/dashboard')

if __name__ == '__main__':
    app.run(debug=True, port=5000)