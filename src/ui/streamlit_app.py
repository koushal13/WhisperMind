"""
Streamlit web interface for WhisperMind chatbot.
"""

import streamlit as st
import asyncio
import tempfile
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from chatbot import WhisperMindChatbot
from core.config import Config


# Streamlit page config
st.set_page_config(
    page_title="WhisperMind - Local AI Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


class StreamlitUI:
    """Streamlit user interface for the chatbot."""
    
    def __init__(self):
        """Initialize the UI."""
        self.chatbot = None
        self.config = None
        
        # Initialize session state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'chatbot_status' not in st.session_state:
            st.session_state.chatbot_status = {}
    
    async def initialize_chatbot(self):
        """Initialize the chatbot if not already done."""
        if not st.session_state.initialized:
            try:
                with st.spinner("Initializing WhisperMind chatbot..."):
                    self.config = Config()
                    self.chatbot = WhisperMindChatbot()
                    await self.chatbot.initialize()
                    
                    # Load documents if available
                    docs_path = "data/documents"
                    if os.path.exists(docs_path):
                        docs_count = await self.chatbot.load_documents(docs_path)
                        if docs_count > 0:
                            st.success(f"Loaded {docs_count} documents from {docs_path}")
                    
                    st.session_state.initialized = True
                    st.success("WhisperMind chatbot initialized successfully!")
                    
            except Exception as e:
                st.error(f"Failed to initialize chatbot: {e}")
                logger.error(f"Initialization error: {e}")
                return False
        
        return True
    
    def render_sidebar(self):
        """Render the sidebar with configuration and controls."""
        with st.sidebar:
            st.title("🧠 WhisperMind")
            st.markdown("*Local AI Chatbot with Voice*")
            
            # Status section
            st.subheader("📊 Status")
            if st.session_state.initialized:
                status = st.session_state.get('chatbot_status', {})
                st.success("✅ Chatbot Ready")
                
                if status:
                    st.metric("Documents Loaded", status.get('documents_loaded', 0))
                    st.metric("Ollama Available", "✅" if status.get('ollama_available', False) else "❌")
                    st.metric("Voice Enabled", "✅" if status.get('voice_enabled', False) else "❌")
            else:
                st.warning("⏳ Initializing...")
            
            st.divider()
            
            # Configuration section
            st.subheader("⚙️ Settings")
            
            # RAG settings
            use_rag = st.checkbox("Use RAG (Document Search)", value=True, help="Search local documents for context")
            
            # Voice settings
            voice_enabled = st.checkbox("Enable Voice Input", value=False, help="Allow voice input via microphone")
            
            if voice_enabled:
                st.info("🎤 Voice input will be available in chat")
            
            # Model settings
            with st.expander("🤖 Model Settings"):
                temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="Response creativity")
                max_tokens = st.slider("Max Tokens", 100, 4000, 2048, 100, help="Maximum response length")
            
            st.divider()
            
            # Document management
            st.subheader("📚 Documents")
            
            uploaded_files = st.file_uploader(
                "Upload documents",
                type=['txt', 'pdf', 'docx', 'md'],
                accept_multiple_files=True,
                help="Upload documents to add to knowledge base"
            )
            
            if uploaded_files:
                if st.button("Process Uploaded Files"):
                    self.process_uploaded_files(uploaded_files)
            
            if st.button("Refresh Document Index"):
                self.refresh_documents()
            
            st.divider()
            
            # Actions
            st.subheader("🔧 Actions")
            
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            if st.button("Get Chatbot Status"):
                self.update_status()
            
            # Store settings in session state
            st.session_state.use_rag = use_rag
            st.session_state.voice_enabled = voice_enabled
            st.session_state.temperature = temperature
            st.session_state.max_tokens = max_tokens
    
    def render_main_content(self):
        """Render the main chat interface."""
        st.title("💬 Chat with WhisperMind")
        
        if not st.session_state.initialized:
            st.info("👈 Please wait for initialization to complete")
            return
        
        # Display chat messages
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    
                    # Show source documents if available
                    if message["role"] == "assistant" and "sources" in message:
                        with st.expander("📖 Source Documents"):
                            for source in message["sources"]:
                                st.markdown(f"**{source['filename']}** (similarity: {source['similarity']:.3f})")
                                st.markdown(f"*{source['content'][:200]}...*")
        
        # Chat input
        prompt = st.chat_input("Ask WhisperMind anything...")
        
        # Voice input section
        if st.session_state.get('voice_enabled', False):
            with st.expander("🎤 Voice Input"):
                audio_bytes = st.audio_input("Record your question")
                
                if audio_bytes:
                    if st.button("Process Voice Input"):
                        self.process_voice_input(audio_bytes)
        
        # Process text input
        if prompt:
            self.process_text_input(prompt)
    
    def process_text_input(self, prompt: str):
        """Process text input from user."""
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_data = asyncio.run(self.get_chatbot_response(prompt))
                
                st.markdown(response_data["response"])
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_data["response"],
                    "sources": response_data.get("sources", [])
                })
        
        st.rerun()
    
    def process_voice_input(self, audio_bytes: bytes):
        """Process voice input from user."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            with st.spinner("Transcribing voice input..."):
                transcribed_text, response = asyncio.run(
                    self.chatbot.voice_chat(temp_path)
                )
            
            if transcribed_text:
                st.success(f"Transcribed: {transcribed_text}")
                self.process_text_input(transcribed_text)
            else:
                st.error("Failed to transcribe voice input")
            
        except Exception as e:
            st.error(f"Voice processing error: {e}")
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def get_chatbot_response(self, message: str) -> Dict[str, Any]:
        """Get response from chatbot with source information."""
        try:
            # Get response
            response = await self.chatbot.chat(
                message=message,
                use_rag=st.session_state.get('use_rag', True)
            )
            
            # Get source documents if RAG is enabled
            sources = []
            if st.session_state.get('use_rag', True) and self.chatbot.retriever:
                retrieved_docs = await self.chatbot.retriever.retrieve(message, top_k=3)
                sources = [
                    {
                        "filename": doc.metadata.get("filename", "Unknown"),
                        "content": doc.content,
                        "similarity": doc.similarity
                    }
                    for doc in retrieved_docs
                ]
            
            return {
                "response": response,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error getting chatbot response: {e}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "sources": []
            }
    
    def process_uploaded_files(self, uploaded_files):
        """Process uploaded files and add to knowledge base."""
        try:
            with st.spinner("Processing uploaded files..."):
                # Save files to temporary directory
                temp_dir = tempfile.mkdtemp()
                saved_files = []
                
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_files.append(file_path)
                
                # Process documents
                docs_count = asyncio.run(self.chatbot.load_documents(temp_dir))
                
                if docs_count > 0:
                    st.success(f"Successfully processed {docs_count} document chunks from {len(uploaded_files)} files")
                else:
                    st.warning("No documents were processed")
                
                # Clean up
                for file_path in saved_files:
                    try:
                        os.unlink(file_path)
                    except:
                        pass
                os.rmdir(temp_dir)
                
        except Exception as e:
            st.error(f"Error processing files: {e}")
    
    def refresh_documents(self):
        """Refresh document index from documents directory."""
        try:
            with st.spinner("Refreshing document index..."):
                docs_count = asyncio.run(self.chatbot.load_documents("data/documents"))
                if docs_count > 0:
                    st.success(f"Refreshed index with {docs_count} document chunks")
                else:
                    st.info("No documents found in data/documents directory")
        except Exception as e:
            st.error(f"Error refreshing documents: {e}")
    
    def update_status(self):
        """Update chatbot status."""
        try:
            status = asyncio.run(self.chatbot.get_status())
            st.session_state.chatbot_status = status
            st.success("Status updated")
        except Exception as e:
            st.error(f"Error updating status: {e}")
    
    def run(self):
        """Run the Streamlit application."""
        # Initialize chatbot
        asyncio.run(self.initialize_chatbot())
        
        # Render UI
        self.render_sidebar()
        self.render_main_content()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "🧠 **WhisperMind** - Privacy-first local AI chatbot with voice capabilities | "
            "Powered by Ollama, ChromaDB, Whisper & Coqui TTS"
        )


def main():
    """Main entry point for Streamlit app."""
    ui = StreamlitUI()
    ui.run()


if __name__ == "__main__":
    main()