"""
Simple test script for WhisperMind components.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_components():
    """Test individual components."""
    print("🧪 Testing WhisperMind Components")
    print("="*50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    try:
        from src.core.config import Config
        config = Config()
        print("   ✅ Configuration loaded successfully")
        print(f"   📋 Ollama model: {config.ollama.model}")
        print(f"   📋 Voice enabled: {config.voice.enabled}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
    
    # Test 2: Document Processing
    print("\n2. Testing Document Processing...")
    try:
        from src.rag.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test with our sample document
        docs = await processor.process_file("data/documents/whispermind_info.md")
        print(f"   ✅ Document processing works - {len(docs)} chunks created")
        print(f"   📋 First chunk preview: {docs[0].content[:100]}...")
    except Exception as e:
        print(f"   ❌ Document processing error: {e}")
    
    # Test 3: Vector Store (without embedding model)
    print("\n3. Testing Vector Store...")
    try:
        from src.rag.vector_store import VectorStore
        vector_store = VectorStore()
        print("   ✅ Vector store created (initialization will happen when needed)")
    except Exception as e:
        print(f"   ❌ Vector store error: {e}")
    
    # Test 4: Text-to-Speech
    print("\n4. Testing Text-to-Speech...")
    try:
        from src.voice.text_to_speech import TextToSpeech
        tts = TextToSpeech()
        await tts.initialize()
        voices = await tts.get_available_voices()
        print(f"   ✅ TTS initialized - {len(voices)} voices available")
        if voices:
            print(f"   📋 Sample voice: {voices[0]['name']}")
    except Exception as e:
        print(f"   ❌ TTS error: {e}")
    
    # Test 5: Speech-to-Text
    print("\n5. Testing Speech-to-Text...")
    try:
        from src.voice.speech_to_text import SpeechToText
        stt = SpeechToText(model_size="tiny")  # Use tiny model for quick test
        model_info = await stt.get_model_info()
        print(f"   ✅ STT ready - model: {model_info['model_size']}")
    except Exception as e:
        print(f"   ❌ STT error: {e}")
    
    # Test 6: Ollama Connection
    print("\n6. Testing Ollama Connection...")
    try:
        from src.core.ollama_client import OllamaClient
        client = OllamaClient()
        available = await client.is_available()
        if available:
            models = await client.list_models()
            print(f"   ✅ Ollama connected - {len(models)} models available")
            if models:
                print(f"   📋 Available models: {[m['name'] for m in models[:3]]}")
        else:
            print("   ⚠️  Ollama server not running (start with: ollama serve)")
    except Exception as e:
        print(f"   ❌ Ollama error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Component testing complete!")
    print("\n💡 Next steps:")
    print("   1. Ensure Ollama is running: ollama serve")
    print("   2. Start WhisperMind: python main.py --ui")


if __name__ == "__main__":
    asyncio.run(test_components())