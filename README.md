#  Sunmark School AI Voice Agent

A voice-enabled RAG (Retrieval-Augmented Generation) system providing about Sunmark School's admissions, curriculum, and facilities. This project compares two high-performance LLMs to ensure the most accurate responses for parents and students.


### Architecture Overview
* **Data Ingestion**: Scraped `https://www.sunmarke.com/` using `crawl4ai` and `LangChain`.
* **Vector Store**: Semantic data stored in **PGVector** using `HuggingFace` embeddings.
* **Backend**: `FastAPI` (Python) orchestrating the RAG pipeline with dynamic port binding for production stability.
* **Frontend**: `Next.js` with `TypeScript` featuring a dual-column comparison UI.
* **Voice Integration**: **Web Speech API** for real-time voice-to-text and **SpeechSynthesis** for text-to-voice output.



### LLM Selection & Justification

Used **Groq (llama-3.3-70b-versatile)** and **OpenRouter (openai/gpt-3.5-turbo)** for LLM inference:
1.  **Groq**: Selected for its industry-leading inference speed, which is critical for a "live" voice agent experience.
2.  **OpenRouter**: Selected as a robust fallback to ensure high availability and reliability.


### Setup Instructions

This repository includes all required configuration files:
* `uv.lock` and `pyproject.toml` (Python/Backend) 
* `package.json` (Next.js/Frontend) 
* `.env.example` (Environment template without actual keys) 

**2. Backend Setup**
```bash
# Clone the repo
git clone <your-repo-url>
cd sunmark-ai-chatbot

# Install dependencies using uv
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Update .env with DATABASE_URL, GROQ_API_KEY, and OPENROUTER_API_KEY

# Run the server
uvicorn main:app --reload
```

### Frontend Setup
To run the frontend locally for development or testing:

```bash
# Navigate to the frontend directory
cd frontend
# Install necessary packages
npm install
# Start the development server
npm run dev
```
### Assumptions & Limitations

1. **Voice Compatibility:** The voice-to-text feature requires a modern browser with Web Speech API support (Chrome/Edge recommended).

2. **Data Refresh:** The current RAG context is based on a snapshot of the school's website as of March 2026.