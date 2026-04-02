import asyncio
import os
from typing import List, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage # For history mapping

# Import your updated chains from rag_pipeline.py
from rag_pipeline import groq_chain, openrouter_chain

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Sunmark School Chatbot API")

# 1. Pull the origins from the environment variable
# If not found, it defaults to localhost for local development
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")

# 2. Convert the string "url1,url2" into a Python list ["url1", "url2"]
origins = [origin.strip() for origin in raw_origins.split(",")]

# 3. Check if using a wildcard "*"
# This is the "safety switch" to prevent the app from crashing on Render
is_wildcard = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not is_wildcard, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model
class ChatRequest(BaseModel):
    input: str
    # Expecting list of tuples: [("human", "hi"), ("ai", "hello")]
    chat_history: List[Tuple[str, str]] = []

def format_history(history):
    """Converts raw tuples from frontend into LangChain Message objects"""
    formatted = []
    for role, message in history:
        if role.lower() == "human" or role.lower() == "user":
            formatted.append(HumanMessage(content=message))
        else:
            formatted.append(AIMessage(content=message))
    return formatted

# API endpoints
@app.get("/")
def read_root():
    return {"message": "Sunmark School API is running"}

@app.post("/ask")
async def ask_question(request: ChatRequest):
    # Prepare the input for the LangChain pipeline
    inputs = {
        "input": request.input,
        "chat_history": format_history(request.chat_history)
    }

    try:
        # Run both Groq and OpenRouter in parallel to save time
        # to_thread is used because invoke() is a synchronous call
        results = await asyncio.gather(
            asyncio.to_thread(groq_chain, inputs),
            asyncio.to_thread(openrouter_chain, inputs)
        )
        
        return {
            "query": request.input,
            "responses": {
                "groq": results[0],
                "openrouter": results[1]
            }
        }
    except Exception as e:
        print(f"Server Error: {str(e)}") # Helpful for debugging in Vercel logs
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
def health():
    return {"status": "online", "version": "1.1-hf-api"}

# Production Entry Point
if __name__ == "__main__":
    import uvicorn
    # Vercel and other platforms provide a PORT environment variable
    port = int(os.getenv("PORT", 8000)) 
    uvicorn.run(app, host="0.0.0.0", port=port)