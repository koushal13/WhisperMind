"""
Main chatbot application combining Ollama LLM, RAG, and voice processing.
"""

import os
import logging
from typing import Optional, List, Dict, Any
import asyncio
from pathlib import Path

from .rag.document_processor import DocumentProcessor
from .rag.vector_store import VectorStore
from .rag.retriever import DocumentRetriever
from .core.ollama_client import OllamaClient
from .voice.speech_to_text import SpeechToText
from .voice.text_to_speech import TextToSpeech
from .core.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperMindChatbot:
    """
    Privacy-first offline chatbot with voice capabilities and local knowledge.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the chatbot with configuration."""
        self.config = Config(config_path)
        
        # Core components
        self.ollama_client = None
        self.document_processor = None
        self.vector_store = None
        self.retriever = None
        
        # Voice components (optional)
        self.speech_to_text = None
        self.text_to_speech = None
        
        # State
        self.is_initialized = False
        self.voice_enabled = False
        
    async def initialize(self):
        """Initialize all components asynchronously."""
        try:
            logger.info("Initializing WhisperMind Chatbot...")
            
            # Initialize Ollama client
            self.ollama_client = OllamaClient(
                base_url=self.config.ollama.base_url,
                model=self.config.ollama.model
            )
            await self.ollama_client.initialize()
            
            # Initialize RAG components
            self.document_processor = DocumentProcessor()
            self.vector_store = VectorStore(
                persist_directory=self.config.chromadb.persist_directory,
                collection_name=self.config.chromadb.collection_name
            )
            self.retriever = DocumentRetriever(
                vector_store=self.vector_store,
                top_k=self.config.rag.top_k
            )
            
            # Initialize voice components if enabled
            if self.config.voice.enabled:
                self.speech_to_text = SpeechToText(
                    model_size=self.config.voice.whisper_model
                )
                self.text_to_speech = TextToSpeech(
                    model_name=self.config.voice.tts_model
                )
                self.voice_enabled = True
                logger.info("Voice components initialized")
            
            self.is_initialized = True
            logger.info("Chatbot initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            raise
    
    async def load_documents(self, document_path: str) -> int:
        """
        Load and process documents from the specified path.
        
        Args:
            document_path: Path to documents directory
            
        Returns:
            Number of documents processed
        """
        if not self.is_initialized:
            await self.initialize()
        
        logger.info(f"Loading documents from {document_path}")
        
        try:
            # Process documents
            documents = await self.document_processor.process_directory(document_path)
            
            if not documents:
                logger.warning("No documents found to process")
                return 0
            
            # Add to vector store
            await self.vector_store.add_documents(documents)
            
            logger.info(f"Successfully processed {len(documents)} documents")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            raise
    
    async def chat(self, message: str, use_rag: bool = True) -> str:
        """
        Process a text message and return a response.
        
        Args:
            message: User input message
            use_rag: Whether to use RAG for context retrieval
            
        Returns:
            Chatbot response
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            context = ""
            
            if use_rag:
                # Retrieve relevant context
                relevant_docs = await self.retriever.retrieve(message)
                if relevant_docs:
                    context = "\n\n".join([doc.content for doc in relevant_docs])
            
            # Generate response
            response = await self.ollama_client.generate_response(
                message=message,
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def voice_chat(self, audio_file_path: str) -> tuple[str, str]:
        """
        Process voice input and return text transcription and response.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Tuple of (transcribed_text, response)
        """
        if not self.voice_enabled:
            raise ValueError("Voice processing is not enabled")
        
        try:
            # Transcribe audio to text
            transcribed_text = await self.speech_to_text.transcribe(audio_file_path)
            logger.info(f"Transcribed: {transcribed_text}")
            
            # Get chatbot response
            response = await self.chat(transcribed_text)
            
            return transcribed_text, response
            
        except Exception as e:
            logger.error(f"Failed to process voice input: {e}")
            return "", f"Sorry, I couldn't process your voice input: {str(e)}"
    
    async def speak_response(self, text: str, output_path: str = "temp_audio.wav") -> str:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            
        Returns:
            Path to generated audio file
        """
        if not self.voice_enabled:
            raise ValueError("Voice processing is not enabled")
        
        try:
            audio_path = await self.text_to_speech.synthesize(text, output_path)
            return audio_path
            
        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the chatbot."""
        status = {
            "initialized": self.is_initialized,
            "voice_enabled": self.voice_enabled,
            "ollama_available": False,
            "documents_loaded": 0
        }
        
        if self.ollama_client:
            status["ollama_available"] = await self.ollama_client.is_available()
        
        if self.vector_store:
            status["documents_loaded"] = await self.vector_store.get_document_count()
        
        return status
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up chatbot resources...")
        
        if self.ollama_client:
            await self.ollama_client.cleanup()
        
        if self.vector_store:
            await self.vector_store.cleanup()
        
        logger.info("Cleanup complete")


# Example usage
if __name__ == "__main__":
    async def main():
        chatbot = WhisperMindChatbot()
        
        try:
            # Initialize
            await chatbot.initialize()
            
            # Load some documents
            docs_loaded = await chatbot.load_documents("data/documents")
            print(f"Loaded {docs_loaded} documents")
            
            # Test chat
            response = await chatbot.chat("Hello, how are you?")
            print(f"Response: {response}")
            
            # Get status
            status = await chatbot.get_status()
            print(f"Status: {status}")
            
        finally:
            await chatbot.cleanup()
    
    asyncio.run(main())