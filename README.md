# 🚀 Sunmark School AI Voice Agent

A voice-enabled RAG (Retrieval-Augmented Generation) system providing about Sunmark School's admissions, curriculum, and facilities. This project compares two high-performance LLMs to ensure the most accurate responses for parents and students.

### 🔗 Deployed Application URLs
* **Frontend (Vercel)**: [https://sunmark-ai-chatbot.vercel.app/](https://sunmark-ai-chatbot.vercel.app/)
* **Backend (Render)**: [https://sunmark-ai-chatbot.onrender.com](https://sunmark-ai-chatbot.onrender.com)
* *Note: The application will remain live for at least 7 days after submission.*

---

### 🏗️ Architecture Overview
* **Data Ingestion**: Scraped `https://www.sunmarke.com/` using `crawl4ai` and `LangChain`.
* **Vector Store**: Semantic data stored in **PGVector** using `HuggingFace` embeddings.
* **Backend**: `FastAPI` (Python) orchestrating the RAG pipeline with dynamic port binding for production stability.
* **Frontend**: `Next.js` with `TypeScript` featuring a dual-column comparison UI.
* **Voice Integration**: **Web Speech API** for real-time voice-to-text and **SpeechSynthesis** for text-to-voice output.

---

### 🧠 LLM Selection & Justification
During the development and testing phase, initially implemented **Gemini**, **Kimi**, and **DeepSeek**. However, due to the high volume of testing required to refine the RAG retrieval accuracy and system stability, exhausted the free-tier rate limits and quotas for these providers.

To ensure the system remains **stable and performant** for the final assessment and live demo, pivoted to **Groq (llama-3.3-70b-versatile)** and **OpenRouter (openai/gpt-3.5-turbo)**:
1.  **Groq**: Selected for its industry-leading inference speed, which is critical for a "live" voice agent experience.
2.  **OpenRouter**: Selected as a robust fallback to ensure high availability and reliability.

---

### 💰 Estimated Costs (per 1,000 queries)
| Service | Estimated Cost | Notes |
| :--- | :--- | :--- |
| **Groq API** | $0.00 | Currently utilizing the Free Tier. |
| **OpenRouter** | ~$0.01 - $0.03 | Based on average token usage for RAG contexts. |
| **Hosting (Vercel/Render)** | $0.00 | Utilizing Free Tiers. |
| **Total** | **<$0.05** | Highly cost-efficient for school-scale deployment. |

---

### 🛠️ Setup Instructions

**1. [cite_start]Project Structure **
This repository includes all required configuration files:
* `uv.lock` and `pyproject.toml` (Python/Backend) 
* [cite_start]`package.json` (Next.js/Frontend) 
* [cite_start]`.env.example` (Environment template without actual keys) 

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