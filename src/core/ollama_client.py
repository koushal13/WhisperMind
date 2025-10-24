"""
Ollama client for local LLM inference.
"""

import aiohttp
import asyncio
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = None
        
    async def initialize(self):
        """Initialize the HTTP session."""
        self.session = aiohttp.ClientSession()
        
        # Check if Ollama is available
        if not await self.is_available():
            raise ConnectionError(
                f"Ollama server not available at {self.base_url}. "
                f"Please ensure Ollama is running."
            )
        
        # Check if model is available
        if not await self.is_model_available():
            logger.warning(f"Model '{self.model}' not found. Attempting to pull...")
            await self.pull_model()
    
    async def is_available(self) -> bool:
        """Check if Ollama server is available."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Failed to check Ollama availability: {e}")
            return False
    
    async def is_model_available(self) -> bool:
        """Check if the specified model is available."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'].split(':')[0] for model in data.get('models', [])]
                    return self.model in models
                return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False
    
    async def pull_model(self) -> bool:
        """Pull the specified model from Ollama registry."""
        try:
            logger.info(f"Pulling model '{self.model}'...")
            
            payload = {"name": self.model}
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status == 200:
                    # Stream the response for progress updates
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode())
                                if 'status' in data:
                                    logger.info(f"Pull status: {data['status']}")
                            except json.JSONDecodeError:
                                continue
                    
                    logger.info(f"Successfully pulled model '{self.model}'")
                    return True
                else:
                    logger.error(f"Failed to pull model: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    async def generate_response(
        self,
        message: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """
        Generate a response using the LLM.
        
        Args:
            message: User message
            context: Additional context from RAG
            temperature: Response creativity (0.0 to 1.0)
            max_tokens: Maximum response length
            
        Returns:
            Generated response text
        """
        try:
            # Construct the prompt
            system_prompt = (
                "You are WhisperMind, a helpful AI assistant that answers questions "
                "based on the provided context and your knowledge. Be conversational, "
                "helpful, and accurate. If you don't know something, say so."
            )
            
            user_prompt = message
            if context.strip():
                user_prompt = f"Context:\n{context}\n\nQuestion: {message}"
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('message', {}).get('content', 'No response generated.')
                else:
                    error_text = await response.text()
                    logger.error(f"Ollama API error: {response.status} - {error_text}")
                    return f"Sorry, I encountered an error generating a response."
                    
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }
            
            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('embedding', [])
                else:
                    logger.error(f"Failed to generate embeddings: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('models', [])
                return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def cleanup(self):
        """Clean up the HTTP session."""
        if self.session:
            await self.session.close()


# Example usage
if __name__ == "__main__":
    async def main():
        client = OllamaClient(model="llama3")
        
        try:
            await client.initialize()
            
            response = await client.generate_response(
                "What is machine learning?",
                context="Machine learning is a subset of artificial intelligence."
            )
            print(f"Response: {response}")
            
            models = await client.list_models()
            print(f"Available models: {[m['name'] for m in models]}")
            
        finally:
            await client.cleanup()
    
    asyncio.run(main())