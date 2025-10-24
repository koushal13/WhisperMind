"""
Main entry point for WhisperMind chatbot.
"""

import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.chatbot import WhisperMindChatbot
from src.core.config import Config


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="WhisperMind - Local AI Chatbot")
    parser.add_argument("--config", default="config/config.yaml", help="Configuration file path")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit UI")
    parser.add_argument("--load-docs", help="Load documents from directory")
    parser.add_argument("--test", action="store_true", help="Run test chat session")
    
    args = parser.parse_args()
    
    # Initialize chatbot
    chatbot = WhisperMindChatbot(config_path=args.config)
    
    try:
        if args.ui:
            # Launch Streamlit UI
            import subprocess
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "src/ui/streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "localhost"
            ])
        
        elif args.load_docs:
            # Load documents only
            await chatbot.initialize()
            docs_count = await chatbot.load_documents(args.load_docs)
            print(f"Loaded {docs_count} documents from {args.load_docs}")
        
        elif args.test:
            # Run test chat session
            await test_chat_session(chatbot)
        
        else:
            # Interactive CLI chat
            await cli_chat(chatbot)
    
    finally:
        await chatbot.cleanup()


async def cli_chat(chatbot: WhisperMindChatbot):
    """Run interactive CLI chat session."""
    print("🧠 WhisperMind - Local AI Chatbot")
    print("Type 'quit' to exit, 'status' for system status\n")
    
    await chatbot.initialize()
    
    # Try to load documents
    docs_count = await chatbot.load_documents("data/documents")
    if docs_count > 0:
        print(f"📚 Loaded {docs_count} documents\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if user_input.lower() == 'status':
                status = await chatbot.get_status()
                print(f"Status: {status}")
                continue
            
            if not user_input:
                continue
            
            print("🤔 Thinking...")
            response = await chatbot.chat(user_input)
            print(f"WhisperMind: {response}\n")
        
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")


async def test_chat_session(chatbot: WhisperMindChatbot):
    """Run a test chat session."""
    print("🧪 Running test chat session...")
    
    await chatbot.initialize()
    
    test_questions = [
        "Hello, how are you?",
        "What is machine learning?",
        "Can you tell me about artificial intelligence?",
        "What are the benefits of local AI models?"
    ]
    
    for question in test_questions:
        print(f"\nTest Question: {question}")
        response = await chatbot.chat(question)
        print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    # Test status
    status = await chatbot.get_status()
    print(f"\nSystem Status: {status}")
    
    print("✅ Test session complete!")


if __name__ == "__main__":
    asyncio.run(main())