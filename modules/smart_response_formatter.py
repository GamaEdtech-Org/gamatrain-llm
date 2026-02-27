#!/usr/bin/env python3
"""
Smart Response Formatter
Detects question type and formats responses appropriately
"""
import re

class QuestionClassifier:
    """Classifies questions into factual or educational types"""
    
    # Keywords that indicate factual questions
    FACTUAL_KEYWORDS = [
        "where", "when", "who", "which", "what is the address",
        "what is the location", "how many", "how much",
        "does", "is there", "are there", "has", "have"
    ]
    
    # Keywords that indicate educational questions
    EDUCATIONAL_KEYWORDS = [
        "what is", "what are", "how does", "how do",
        "explain", "describe", "tell me about",
        "why", "how to", "what does", "define"
    ]
    
    @staticmethod
    def classify(question: str) -> str:
        """
        Classify question type
        Returns: 'factual' or 'educational'
        """
        question_lower = question.lower().strip()
        
        # Check for factual patterns first (more specific)
        for keyword in QuestionClassifier.FACTUAL_KEYWORDS:
            if keyword in question_lower:
                return "factual"
        
        # Check for educational patterns
        for keyword in QuestionClassifier.EDUCATIONAL_KEYWORDS:
            if keyword in question_lower:
                return "educational"
        
        # Default to factual for short questions
        if len(question.split()) <= 5:
            return "factual"
        
        return "educational"


class ResponseFormatter:
    """Formats response prompts based on question type"""
    
    @staticmethod
    def format_prompt(question: str, question_type: str, context: str = "") -> str:
        """
        Format the prompt based on question type
        
        Args:
            question: The user's question
            question_type: 'factual' or 'educational'
            context: Additional context (e.g., from RAG)
        
        Returns:
            Formatted prompt for the LLM
        """
        if question_type == "factual":
            return ResponseFormatter._format_factual(question, context)
        else:
            return ResponseFormatter._format_educational(question, context)
    
    @staticmethod
    def _format_factual(question: str, context: str) -> str:
        """Format prompt for factual questions - direct answer"""
        prompt = f"""Answer this question directly and concisely.

Question: {question}
"""
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += "\nProvide a clear, direct answer without unnecessary elaboration."
        return prompt
    
    @staticmethod
    def _format_educational(question: str, context: str) -> str:
        """Format prompt for educational questions - structured response"""
        prompt = f"""Answer this educational question with a well-structured response.

Question: {question}
"""
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += """
Structure your response as follows:

1. Concept Explanation: Brief, clear definition
2. Example: Real-world example to illustrate the concept
3. Step-by-Step Explanation: Break down the key points
4. Check Your Understanding: A simple question to verify comprehension

Keep each section concise and focused."""
        return prompt
