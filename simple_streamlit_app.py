"""
Enhanced Streamlit app with voice capabilities for WhisperMind.
"""

import streamlit as st
import requests
import json
import os
import tempfile
import threading
import time
from pathlib import Path

# Voice processing imports with graceful fallback
VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    # Try importing pyaudio for microphone access
    try:
        import pyaudio
        VOICE_AVAILABLE = True
        MICROPHONE_AVAILABLE = True
    except ImportError:
        VOICE_AVAILABLE = True
        MICROPHONE_AVAILABLE = False
        st.info("🎤 Microphone access requires: pip install pyaudio")
except ImportError:
    VOICE_AVAILABLE = False
    MICROPHONE_AVAILABLE = False

st.set_page_config(
    page_title="WhisperMind - Local AI Chatbot with Voice",
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

class VoiceProcessor:
    """Voice input/output processor with file upload fallback."""
    
    def __init__(self):
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        
        if VOICE_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                if MICROPHONE_AVAILABLE:
                    self.microphone = sr.Microphone()
                
                # Initialize TTS
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS
                voices = self.tts_engine.getProperty('voices')
                if voices and len(voices) > 0:
                    self.tts_engine.setProperty('voice', voices[0].id)
                self.tts_engine.setProperty('rate', 180)
                self.tts_engine.setProperty('volume', 0.9)
                
            except Exception as e:
                st.error(f"Voice initialization error: {e}")
                self.recognizer = None
    
    def listen_for_speech(self, timeout=5):
        """Listen for speech input from microphone."""
        if not self.recognizer or not self.microphone:
            return None, "Microphone not available"
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            with self.microphone as source:
                st.info("🎤 Listening... Speak now!")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            try:
                # Use Google's free speech recognition
                text = self.recognizer.recognize_google(audio)
                return text, None
            except sr.UnknownValueError:
                return None, "Could not understand audio"
            except sr.RequestError as e:
                return None, f"Speech recognition error: {e}"
                
        except sr.WaitTimeoutError:
            return None, "No speech detected within timeout"
        except Exception as e:
            return None, f"Error during speech recognition: {e}"
    
    def transcribe_audio_file(self, audio_file_path):
        """Transcribe uploaded audio file."""
        if not self.recognizer:
            return None, "Speech recognition not available"
        
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            try:
                text = self.recognizer.recognize_google(audio)
                return text, None
            except sr.UnknownValueError:
                return None, "Could not understand audio"
            except sr.RequestError as e:
                return None, f"Speech recognition error: {e}"
                
        except Exception as e:
            return None, f"Error processing audio file: {e}"
    
    def speak_text(self, text):
        """Convert text to speech."""
        if not self.tts_engine:
            return False
        
        try:
            # Run TTS in a separate thread to avoid blocking
            def speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=speak)
            thread.daemon = True
            thread.start()
            return True
            
        except Exception as e:
            st.error(f"Text-to-speech error: {e}")
            return False

def main():
    st.title("🧠 WhisperMind - Local AI Chatbot with Voice")
    
    # Initialize voice processor
    if 'voice_processor' not in st.session_state:
        st.session_state.voice_processor = VoiceProcessor() if VOICE_AVAILABLE else None
    
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
        
        # Voice status
        st.divider()
        st.subheader("🎤 Voice Features")
        
        if not VOICE_AVAILABLE:
            st.error("❌ Voice features unavailable")
            st.info("💡 Install voice packages:")
            st.code("pip install speechrecognition pyttsx3")
            voice_input_enabled = False
            voice_output_enabled = False
        else:
            if MICROPHONE_AVAILABLE:
                st.success("✅ Voice features available")
                voice_input_enabled = st.checkbox("Enable Voice Input", value=True)
            else:
                st.warning("⚠️ Microphone unavailable")
                st.info("💡 Install: pip install pyaudio")
                voice_input_enabled = False
            
            voice_output_enabled = st.checkbox("Enable Voice Output", value=True)
            
            # Test microphone button
            if voice_input_enabled and st.session_state.voice_processor:
                if st.button("🎤 Test Microphone"):
                    with st.spinner("Testing microphone..."):
                        text, error = st.session_state.voice_processor.listen_for_speech(timeout=3)
                        if text:
                            st.success(f"✅ Heard: '{text}'")
                        else:
                            st.error(f"❌ {error}")
            
            # Audio file upload as alternative
            if VOICE_AVAILABLE and st.session_state.voice_processor:
                st.markdown("**Or upload audio file:**")
                uploaded_audio = st.file_uploader(
                    "Upload audio file",
                    type=['wav', 'mp3', 'flac', 'aiff'],
                    help="Upload audio file for transcription"
                )
                
                if uploaded_audio:
                    if st.button("🎵 Transcribe Audio"):
                        with st.spinner("Transcribing audio file..."):
                            # Save uploaded file temporarily
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                tmp_file.write(uploaded_audio.getvalue())
                                tmp_path = tmp_file.name
                            
                            try:
                                text, error = st.session_state.voice_processor.transcribe_audio_file(tmp_path)
                                if text:
                                    st.success(f"✅ Transcribed: '{text}'")
                                    # Process as if it was spoken
                                    process_user_input(text, selected_model, ollama_available, voice_output_enabled)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {error}")
                            finally:
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass
        
        st.divider()
        
        # App info
        st.subheader("ℹ️ About")
        st.markdown("""
        **Enhanced WhisperMind** with voice capabilities!
        
        **Current Features:**
        - 💬 Chat with local Ollama models
        - 🎤 Voice input (speech-to-text) - *install deps*
        - 📁 Audio file transcription - *planned*
        - 🔊 Voice output (text-to-speech) - *install deps*
        - 🔒 100% offline privacy
        - ⚡ Real-time processing
        
        **Voice Setup:**
        ```bash
        pip install speechrecognition pyttsx3
        # For microphone: pip install pyaudio
        ```
        
        **Voice Options:**
        - 🎤 Live microphone input
        - 📁 Upload audio files (.wav, .mp3)
        - 🔊 AI voice responses
        """)
    
    # Chat interface
    st.subheader("💬 Chat with Voice")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Add speak button for assistant messages
            if message["role"] == "assistant" and VOICE_AVAILABLE and voice_output_enabled:
                if st.button(f"🔊 Speak", key=f"speak_{len(st.session_state.messages)}_{message['content'][:20]}"):
                    st.session_state.voice_processor.speak_text(message["content"])
                    st.success("🔊 Speaking...")
    
    # Voice input section
    if VOICE_AVAILABLE and voice_input_enabled and MICROPHONE_AVAILABLE and st.session_state.voice_processor:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🎤 Voice Input", type="secondary"):
                with st.spinner("🎤 Listening for your voice..."):
                    text, error = st.session_state.voice_processor.listen_for_speech(timeout=10)
                    
                    if text:
                        st.success(f"✅ Heard: '{text}'")
                        # Process the voice input as if it was typed
                        process_user_input(text, selected_model, ollama_available, voice_output_enabled)
                        st.rerun()
                    else:
                        st.error(f"❌ Voice input failed: {error}")
    
    elif VOICE_AVAILABLE and not MICROPHONE_AVAILABLE:
        st.info("💡 Upload audio files in the sidebar for voice transcription!")
    
    elif not VOICE_AVAILABLE:
        st.info("💡 Install voice packages to enable speech features!")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything... (or use voice input above)"):
        process_user_input(prompt, selected_model, ollama_available, voice_output_enabled)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

def process_user_input(prompt, selected_model, ollama_available, voice_output_enabled):
    """Process user input (text or voice) and generate response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    if ollama_available:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = chat_with_ollama(prompt, selected_model)
            st.markdown(response)
            
            # Auto-speak response if voice output is enabled
            if VOICE_AVAILABLE and voice_output_enabled and st.session_state.voice_processor:
                st.session_state.voice_processor.speak_text(response)
                st.caption("🔊 Speaking response...")
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            error_msg = "Sorry, Ollama is not available. Please start Ollama first."
            st.error(error_msg)
            
            if VOICE_AVAILABLE and voice_output_enabled and st.session_state.voice_processor:
                st.session_state.voice_processor.speak_text(error_msg)

if __name__ == "__main__":
    main()