#!/usr/bin/env python3
"""Test the model directly without RAG"""
import httpx
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gamatrain-qwen"

def test_query(prompt):
    print(f"\n{'='*50}")
    print(f"PROMPT: {prompt}")
    print(f"{'='*50}")
    
    response = httpx.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=60.0
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"RESPONSE: {data.get('response', 'No response')}")
    else:
        print(f"ERROR: {response.status_code}")

if __name__ == "__main__":
    # Test 1: Simple question
    test_query("What is 2+2?")
    
    # Test 2: About AI
    test_query("What is the difference between AI and Machine Learning?")
    
    # Test 3: Follow-up style
    test_query("You just explained Machine Learning. Now tell me how it differs from AI.")
    
    # Test 4: Context in prompt
    context = """Machine Learning is a subset of AI that uses data to train models.
AI is the broader field of creating intelligent systems."""
    test_query(f"Based on this: {context}\n\nHow is ML different from AI?")
