"""
Simplified Streamlit app for WhisperMind with better error handling.
"""

import streamlit as st
import asyncio
import tempfile
import os
import logging
from pathlib import Path
import sys

# Configure logging to suppress warnings
logging.basicConfig(level=logging.ERROR)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Page config
st.set_page_config(
    page_title="WhisperMind - Local AI Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def check_dependencies():
    """Check if all required components are available."""
    components = {
        "ollama": False,
        "documents": False,
        "config": False
    }
    
    try:
        # Check Ollama
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        components["ollama"] = response.status_code == 200
    except:
        pass
    
    # Check documents
    docs_path = Path("data/documents")
    if docs_path.exists():
        components["documents"] = len(list(docs_path.glob("*.*"))) > 0
    
    # Check config
    config_path = Path("config/config.yaml")
    components["config"] = config_path.exists()
    
    return components

def render_sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("🧠 WhisperMind")
        st.markdown("*Local AI Chatbot*")
        
        # Status check
        st.subheader("📊 System Status")
        
        components = check_dependencies()
        
        if components["ollama"]:
            st.success("✅ Ollama Connected")
        else:
            st.error("❌ Ollama Not Connected")
            st.markdown("**Start Ollama:**")
            st.code("ollama serve")
        
        if components["documents"]:
            st.success("✅ Documents Found")
        else:
            st.warning("⚠️ No Documents")
            st.markdown("Add files to `data/documents/`")
        
        if components["config"]:
            st.success("✅ Configuration OK")
        else:
            st.error("❌ Config Missing")
        
        st.divider()
        
        # Simple settings
        st.subheader("⚙️ Settings")
        use_rag = st.checkbox("Enable Document Search", value=True)
        
        st.divider()
        
        # File upload
        st.subheader("📚 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload text files",
            type=['txt', 'md'],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("Save Files"):
            save_uploaded_files(uploaded_files)

def save_uploaded_files(uploaded_files):
    """Save uploaded files to documents directory."""
    docs_dir = Path("data/documents")
    docs_dir.mkdir(exist_ok=True)
    
    for file in uploaded_files:
        file_path = docs_dir / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        st.success(f"Saved: {file.name}")

def simple_chat():
    """Simple chat interface without full WhisperMind integration."""
    st.title("💬 WhisperMind Chat")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm WhisperMind. I'm currently in setup mode. Please ensure Ollama is running and models are downloaded."}
        ]
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            response = get_simple_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def get_simple_response(prompt):
    """Get a simple response using Ollama API directly."""
    try:
        import requests
        
        # Simple Ollama API call
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "Sorry, I couldn't generate a response.")
        else:
            return f"Error: Ollama returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ **Ollama not connected.** Please start Ollama with: `ollama serve`"
    except requests.exceptions.Timeout:
        return "⏰ **Request timed out.** The model might be loading. Please try again."
    except Exception as e:
        return f"❌ **Error:** {str(e)}"

def main():
    """Main app function."""
    render_sidebar()
    
    # Check if system is ready
    components = check_dependencies()
    
    if not components["ollama"]:
        st.error("🚫 Ollama is not running")
        st.markdown("""
        **To get started:**
        1. Install Ollama from https://ollama.com
        2. Run: `ollama serve`
        3. Download a model: `ollama pull llama3`
        4. Refresh this page
        """)
        return
    
    # Show simple chat interface
    simple_chat()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🧠 **WhisperMind** - Privacy-first local AI chatbot | "
        "Powered by Ollama"
    )

if __name__ == "__main__":
    main()