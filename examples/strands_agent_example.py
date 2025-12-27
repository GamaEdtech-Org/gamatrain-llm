"""
Simple Strands Agent Example

This example demonstrates how to create a basic AI agent using the Strands SDK.
The agent can use tools like calculator, Python REPL, and HTTP requests.

Before running, set your API key as an environment variable:
- For Bedrock (default): export AWS_BEDROCK_API_KEY=your_key
- For Anthropic: export ANTHROPIC_API_KEY=your_key
- For OpenAI: export OPENAI_API_KEY=your_key
- For Gemini: export GOOGLE_API_KEY=your_key
"""

from strands import Agent
from strands_tools import calculator

# Create a simple agent with the calculator tool
# Uses Bedrock Claude 4 Sonnet by default
agent = Agent(
    tools=[calculator],
    system_prompt="You are a helpful math assistant. Use the calculator tool for any calculations."
)

# Test the agent with a simple math question
print("Testing the Strands Agent...")
print("-" * 40)

response = agent("What is 25 * 17 + 123?")
print(f"\nAgent response: {response}")

# Demonstrate conversation memory
print("\n" + "-" * 40)
print("Testing conversation memory...")
response = agent("Now divide that result by 2")
print(f"\nAgent response: {response}")
