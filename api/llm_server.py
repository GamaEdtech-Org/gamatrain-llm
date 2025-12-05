"""
Gamatrain LLM API Server (FastAPI + Ollama)
===========================================

This is a high-performance FastAPI server that acts as a gateway/proxy to the Ollama API.
It handles CORS, request validation, and forwards chat requests to the local Ollama instance.

Requirements:
    pip install fastapi uvicorn httpx

Usage:
    python llm_server.py
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import logging

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gamatrain-qwen"
HOST = "0.0.0.0"
PORT = 8000

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GamatrainAPI")

# App Init
app = FastAPI(title="Gamatrain AI API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False
    temperature: float = 0.7

class ChatResponse(BaseModel):
    role: str
    content: str
    model: str

@app.get("/")
async def root():
    return {"status": "online", "service": "Gamatrain AI Gateway"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """
    OpenAI-compatible-ish endpoint that forwards to Ollama.
    """
    logger.info(f"Received chat request with {len(request.messages)} messages")
    
    payload = {
        "model": MODEL_NAME,
        "messages": [msg.dict() for msg in request.messages],
        "stream": request.stream,
        "options": {
            "temperature": request.temperature
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            
            ollama_data = response.json()
            
            # Extract content from Ollama response
            # Ollama response format: {"model": "...", "created_at": "...", "message": {"role": "assistant", "content": "..."}}
            return {
                "id": "chatcmpl-gamatrain",
                "object": "chat.completion",
                "created": 1234567890,
                "model": MODEL_NAME,
                "choices": [
                    {
                        "index": 0,
                        "message": ollama_data.get("message", {}),
                        "finish_reason": "stop"
                    }
                ]
            }
            
        except httpx.RequestError as exc:
            logger.error(f"Ollama connection error: {exc}")
            raise HTTPException(status_code=503, detail="Could not connect to AI Engine (Ollama)")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Ollama API error: {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail="AI Engine Error")

if __name__ == "__main__":
    uvicorn.run("llm_server:app", host=HOST, port=PORT, reload=True)
