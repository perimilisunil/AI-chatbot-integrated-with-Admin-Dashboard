import os
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()

def init_db(app):
    """Initializes the database."""
    # Check for Cloud Database URL or fall back to SQLite
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully.")

# --- TABLE MODEL (No Sentiment Column) ---
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    role = db.Column(db.String(10))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# --- HELPER FUNCTIONS ---

def log_message(session_id, role, content, sentiment=None): 
   
    if current_app:
        new_log = ChatLog(
            session_id=session_id, role=role,  content=content)# type:ignore
        db.session.add(new_log)
        db.session.commit()

def get_chat_history(session_id, limit=10):
    """Gets recent messages in Chronological Order."""
    if current_app:
        # 1. Fetch the last 'limit' messages (Newest First) using ID
        recent_messages = ChatLog.query.filter_by(session_id=session_id)\
                            .order_by(ChatLog.id.desc())\
                            .limit(limit)\
                            .all()
        
        # 2. REVERSE the list so it reads Oldest -> Newest (Top -> Bottom)
        return recent_messages[::-1] 
    return []

def get_analytics():
    if current_app:
        total = ChatLog.query.count()
        users = db.session.query(ChatLog.session_id.distinct()).count()
        return {'total_messages': total, 'active_users': users}
    return {'total_messages': 0, 'active_users': 0}

def get_all_logs():
    if current_app:
        return ChatLog.query.order_by(ChatLog.id.desc()).limit(50).all()
    return []

def delete_chat_log(log_id):
    if current_app:
        log = ChatLog.query.get(log_id)
        if log:
            db.session.delete(log)
            db.session.commit()
