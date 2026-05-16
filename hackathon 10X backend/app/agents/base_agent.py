import json
from app.core.llm_client import llm_client

class BaseAgent:
    """Base class for all agents in the pipeline."""
    
    def __init__(self, name: str, system_prompt: str = "You are a helpful AI agent."):
        self.name = name
        self.system_prompt = system_prompt
        
    async def run(self, context: dict) -> dict:
        """
        Executes the agent with the provided context. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement run()")

    async def _call_llm(self, prompt: str) -> dict:
        """Helper to call LLM"""
        return await llm_client.call(prompt=prompt, system_prompt=self.system_prompt)
