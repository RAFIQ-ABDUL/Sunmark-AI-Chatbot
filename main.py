import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple
from rag_pipeline import groq_chain, openrouter_chain

app = FastAPI(title="Sunmark School Chatbot")

# CORS for Next.js frontend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = []

@app.post("/ask")
async def ask_question(request: ChatRequest):
    inputs = {
        "input": request.input,
        "chat_history": request.chat_history
    }

    try:
        # Simultaneous Execution using to_thread (since invoke is blocking) 
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)