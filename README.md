# 🏋️‍♂️ Fitness Bot AI - Enterprise-Grade RAG Fitness Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Backend-Flask-green?style=for-the-badge&logo=flask&logoColor=white)
![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%201.5-orange?style=for-the-badge&logo=google&logoColor=white)
![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-purple?style=for-the-badge)
![Tailwind CSS](https://img.shields.io/badge/Frontend-Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

Fitness Bot is a production-ready, full-stack AI application designed to provide specialized fitness and health coaching. Unlike generic LLMs, FitBot leverages a **Retrieval-Augmented Generation (RAG)** engine to ingest, index, and retrieve specific domain knowledge (PDFs/Text) uploaded by administrators.

This project demonstrates a modular architecture capable of running complex AI workflows on constrained cloud environments (Free Tier optimizations).

---

## 🔗 Live Demo
### [🚀 Access Application Here](https://chatbot-bv7x.onrender.com)
*(Note: Deployed on Render Free Tier. Please allow up to 50 seconds for the server to wake up on the first request.)*

---

## 📸 Interface Preview

| **Intelligent Chat Interface** | **Admin Command Center** |
|:-----------------------------:|:-----------------------:|
| ![Chat UI](screenshots/chat_interface.png) | ![Dashboard](screenshots/admin_dashboard.png) |
| *Features: Markdown rendering, Dynamic Avatars, Glassmorphism UI.* | *Features: Real-time Analytics, RAG Training, Log Management.* |

---

## 🏗️ System Architecture

The application follows a **Service-Oriented Architecture (SOA)** using the Factory Pattern to ensure separation of concerns between Data, AI Logic, and Interface.

### The RAG Pipeline (Retrieval-Augmented Generation)
1.  **Ingestion:** Admin uploads unstructured data (PDFs/Text) via the Dashboard.
2.  **ETL Process:** `PyPDF` extracts raw text, which is cleaned and chunked.
3.  **Vectorization:** Google's `text-embedding-004` model converts chunks into high-dimensional vectors.
4.  **Indexing:** Vectors are stored in **ChromaDB** (Lightweight configuration).
5.  **Retrieval & Synthesis:** User queries trigger a vector search; relevant context is injected into the **Gemini 2.5 Flash** system prompt to generate accurate, hallucination-free responses.

---

## 🛠️ Technology Stack

| Domain | Technology | Justification |
| :--- | :--- | :--- |
| **Backend** | **Flask (Python)** | Lightweight micro-framework allowing granular control over the request lifecycle. |
| **Database** | **SQLAlchemy + SQLite** | robust ORM for relational data (Chat Logs, Sessions). Configured for Linux compatibility (`pysqlite3`). |
| **AI Core** | **Google Gemini 1.5 Flash** | Optimized for high throughput and low latency (15 RPM limits on Free Tier). |
| **Vector Search** | **ChromaDB** | Serverless vector store optimized for local persistent storage. |
| **Frontend** | **Tailwind CSS** | Utility-first CSS framework for rapid, responsive UI development without custom stylesheets. |
| **Infrastructure** | **Gunicorn + Render** | Production-grade WSGI server configured with custom timeouts for heavy AI loads. |

---

## 📂 Project Directory Structure

```text
fitness-ai-bot/
├── app.py                   # Application Entry Point & Route Definitions
├── requirements.txt         # Dependency Manifest (Linux compatible)
├── .gitignore               # Security Rules
├── README.md                # Documentation
│
├── utils/                   # 🧠 Core Logic Modules
│   ├── __init__.py
│   ├── ai_handler.py        # Gemini API Wrapper & Context Injection
│   ├── db_handler.py        # SQLAlchemy ORM Models & CRUD Operations
│   └── rag_engine.py        # ChromaDB Interface & Embedding Logic
│
├── templates/               # 🎨 Jinja2 Templates
│   ├── base.html            # Master Layout (Tailwind CDN)
│   ├── chat.html            # Chat Interface with JavaScript Logic
│   ├── dashboard.html       # Admin Panel & Analytics Charts
│   └── login.html           # Authentication View           
│                
└── screenshots/             # Documentation Images & Avatar Images
```
