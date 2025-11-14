"""
Simple Streamlit app to test WhisperMind quickly.
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="WhisperMind - Local AI Chatbot",
    page_icon="🧠",
    layout="wide",
)

def check_ollama():
    """Check if Ollama is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_ollama_models():
    """Get available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except:
        pass
    return []

def chat_with_ollama(message, model="llama3"):
    """Send message to Ollama and get response."""
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": model,
            "prompt": message,
            "stream": False
        }
        
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def main():
    st.title("🧠 WhisperMind - Local AI Chatbot")
    
    # Check Ollama status
    with st.sidebar:
        st.subheader("📊 Status")
        
        ollama_available = check_ollama()
        if ollama_available:
            st.success("✅ Ollama is running")
            models = get_ollama_models()
            
            if models:
                selected_model = st.selectbox("Select Model", models, 
                                           index=0 if "llama3" not in [m.split(":")[0] for m in models] 
                                           else [m.split(":")[0] for m in models].index("llama3"))
            else:
                st.warning("No models found")
                selected_model = "llama3"
                st.info("💡 Try running: `ollama pull llama3`")
        else:
            st.error("❌ Ollama is not running")
            st.info("💡 Start Ollama with: `ollama serve`")
            selected_model = "llama3"
        
        st.divider()
        
        # App info
        st.subheader("ℹ️ About")
        st.markdown("""
        This is a simplified version of WhisperMind running with basic Ollama integration.
        
        **Features:**
        - Chat with local Ollama models
        - No cloud dependencies
        - Privacy-first design
        
        **To enable full features:**
        1. Install dependencies: `pip install -r requirements.txt`
        2. Run the full app: `python launch.py`
        """)
    
    # Chat interface
    st.subheader("💬 Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
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
        if ollama_available:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_with_ollama(prompt, selected_model)
                st.markdown(response)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.chat_message("assistant"):
                st.error("Sorry, Ollama is not available. Please start Ollama first.")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

if __name__ == "__main__":
    main()