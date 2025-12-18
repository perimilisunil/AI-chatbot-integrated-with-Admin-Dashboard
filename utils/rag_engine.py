import google.generativeai as genai
import os
import sys
from dotenv import load_dotenv
from typing import Any, List # Import Any to shut up the type checker

load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)# type: ignore

# GLOBAL VARS
# FIX: We type hint this as 'Any' so VS Code stops complaining about .query()
collection: Any = None
chroma_client: Any = None

def init_chroma():
    """
    Initializes ChromaDB only when needed.
    """
    global collection, chroma_client
    
    # If already loaded, skip
    if collection: return True

    try:
        print("⏳ Attempting to load ChromaDB...")
        import chromadb
        from chromadb import Documents, EmbeddingFunction, Embeddings

        # 1. Define a Dummy Embedding Function
        class GoogleGenerativeAIEmbeddingFunction(EmbeddingFunction):
            # FIX for Line 32: We add '# type: ignore' to tell the editor 
            # "We know this is an empty list, allow it."
            def __call__(self, input: Documents) -> Embeddings:
                return [[] for _ in input] # type: ignore

        # 2. Check for Cloud Persistence
        path = "/data/chroma_db" if os.path.exists('/data') else "./chroma_db"
        
        chroma_client = chromadb.PersistentClient(path=path)
        
        # 3. Initialize Collection
        collection = chroma_client.get_or_create_collection(
            name="fitness_knowledge",
            embedding_function=GoogleGenerativeAIEmbeddingFunction()
        )
        print(f"✅ ChromaDB loaded successfully. Path: {path}")
        return True
    except Exception as e:
        print(f"⚠️ RAG Disabled (Memory Limit or Missing Lib): {e}")
        return False

# --- Helper Function ---
def get_embedding(text, task_type):
    """Generates vector embeddings using Google Gemini."""
    model_names = ["models/text-embedding-004", "text-embedding-004"]
    for model in model_names:
        try:
            return genai.embed_content(model=model, content=text, task_type=task_type)# type: ignore
        except:
            continue
    raise Exception("Embedding failed.")

# --- Main Functions (Used by Chat) ---

def add_document_to_knowledge(text_chunk):
    # Try to init. If fails (Out of Memory), return False
    if not init_chroma(): return False
    
    try:
        result = get_embedding(text_chunk, "retrieval_document")
        # 'collection' is now typed as Any, so no red lines here
        collection.add(
            documents=[text_chunk],
            embeddings=[result['embedding']],
            ids=[str(abs(hash(text_chunk)))]
        )
        return True
    except Exception as e:
        print(f"RAG Add Error: {e}")
        return False

def search_knowledge(query):
    if not init_chroma(): return []
    
    try:
        result = get_embedding(query, "retrieval_query")
        results = collection.query(
            query_embeddings=[result['embedding']],
            n_results=3
        )
        # Safe access to dictionary keys
        if results and 'documents' in results and results['documents']:
             return results['documents'][0]
        return []
    except Exception as e:
        print(f"RAG Search Error: {e}")
        return []

# --- Admin Functions (Used by Dashboard) ---

def get_all_documents():
    """Fetches all documents for the admin dashboard."""
    if not init_chroma(): return []
    try:
        data = collection.get()
        documents = []
        # Check if data exists and has the required keys
        if data and 'ids' in data and 'documents' in data:
            ids = data['ids']
            docs = data['documents']
            # Ensure lists are not None before looping
            if ids and docs:
                for i in range(len(ids)):
                    documents.append({'id': ids[i], 'text': docs[i]})
        return documents
    except Exception as e: 
        print(f"Get Documents Error: {e}")
        return []

def delete_document_by_id(doc_id):
    """Deletes a specific document."""
    if not init_chroma(): return False
    try:
        # doc_id needs to be a list for chroma
        collection.delete(ids=[doc_id])
        return True
    except: return False