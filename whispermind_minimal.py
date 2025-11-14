#!/usr/bin/env python3
"""
WhisperMind - Clean & Simple Voice-Enabled AI Chatbot
"""

import streamlit as st
import threading
import tempfile
import os
import hashlib
import time

# Voice processing imports
try:
    import speech_recognition as sr
    import pyttsx3
    import whisper
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# Ollama imports
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class VoiceProcessor:
    """Simple voice processor with local Whisper and TTS."""
    
    def __init__(self):
        self.tts_engine = None
        self.is_speaking = False
        self._speaking_lock = threading.Lock()
        
        if VOICE_AVAILABLE:
            # Initialize local Whisper model
            if not hasattr(st.session_state, 'whisper_model'):
                st.session_state.whisper_model = whisper.load_model("base")
            
            # Initialize TTS
            try:
                self.tts_engine = pyttsx3.init()
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    for voice in voices:
                        if any(name in voice.name.lower() for name in ['daniel', 'alex', 'thomas']):
                            self.tts_engine.setProperty('voice', voice.id)
                            print(f"Using voice: {voice.name}")
                            break
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 1.0)
            except Exception as e:
                print(f"TTS initialization error: {e}")
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio using local Whisper."""
        print("🔍 Whisper: Starting audio processing...")
        try:
            # Get audio bytes
            if hasattr(audio_data, 'getvalue'):
                audio_bytes = audio_data.getvalue()
            else:
                audio_bytes = audio_data
            
            print(f"📊 Audio size: {len(audio_bytes)} bytes")
            
            if len(audio_bytes) < 1000:
                print("⚠️ Audio too short")
                return None, "Audio too short - please record a longer message"
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                print("🧠 Checking Whisper model...")
                if hasattr(st.session_state, 'whisper_model'):
                    print("🎯 Running Whisper transcription...")
                    result = st.session_state.whisper_model.transcribe(tmp_path)
                    transcribed_text = result["text"].strip()
                    print(f"📝 Raw transcription: '{transcribed_text}'")
                    
                    if transcribed_text:
                        print("✅ Transcription successful!")
                        return transcribed_text, None
                    else:
                        print("❌ Empty transcription result")
                        return None, "Could not understand the audio"
                else:
                    print("❌ Whisper model not found")
                    return None, "Whisper model not loaded"
                    
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Transcription error: {str(e)}")
            return None, f"Transcription error: {str(e)[:100]}"
    
    def speak_text(self, text):
        """Convert text to speech safely."""
        if not self.tts_engine or not text.strip():
            print("❌ TTS: No engine or empty text")
            return False
        
        # Allow multiple concurrent TTS by checking and stopping previous
        if self.is_speaking:
            print("⏸️ TTS: Stopping previous speech...")
            self.stop_speaking()
            time.sleep(0.5)  # Brief pause
            
        try:
            with self._speaking_lock:
                self.is_speaking = True
                print(f"🎤 TTS: Starting speech for text length {len(text)}")
                
                def speak_safely():
                    try:
                        temp_engine = pyttsx3.init()
                        voices = temp_engine.getProperty('voices')
                        if voices:
                            for voice in voices:
                                if any(name in voice.name.lower() for name in ['daniel', 'alex', 'thomas']):
                                    temp_engine.setProperty('voice', voice.id)
                                    print(f"🗣️ TTS: Using voice {voice.name}")
                                    break
                        temp_engine.setProperty('rate', 175)
                        temp_engine.setProperty('volume', 1.0)
                        print(f"📢 TTS: Speaking text...")
                        temp_engine.say(text)
                        temp_engine.runAndWait()
                        temp_engine.stop()
                        del temp_engine
                        print(f"✅ TTS: Speech completed")
                    except Exception as e:
                        print(f"❌ TTS Error: {e}")
                    finally:
                        self.is_speaking = False
                        print(f"🔄 TTS: Speech flag cleared")
                
                thread = threading.Thread(target=speak_safely, daemon=True)
                thread.start()
                return True
                
        except Exception as e:
            self.is_speaking = False
            print(f"❌ TTS Setup Error: {e}")
            return False
            print(f"Text-to-speech error: {e}")
            return False
    
    def stop_speaking(self):
        """Stop ongoing speech."""
        try:
            with self._speaking_lock:
                self.is_speaking = False
                if self.tts_engine:
                    try:
                        self.tts_engine.stop()
                    except:
                        pass
                return True
        except Exception as e:
            print(f"Error stopping speech: {e}")
            return False

def check_ollama():
    """Check if Ollama is available."""
    if not OLLAMA_AVAILABLE:
        return False, []
    try:
        client = ollama.Client()
        models_response = client.list()
        if hasattr(models_response, 'models') and models_response.models:
            model_names = [model.model for model in models_response.models]
            print(f"🔍 Found Ollama models: {model_names}")
            return True, model_names
        else:
            print("❌ No models found in Ollama")
            return True, []  # Ollama is available but no models
    except Exception as e:
        print(f"❌ Ollama connection error: {e}")
        return False, []

def chat_with_ollama(prompt, model="phi"):
    """Chat with Ollama model."""
    try:
        client = ollama.Client()
        response = client.chat(model=model, messages=[
            {"role": "user", "content": prompt}
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.set_page_config(page_title="WhisperMind", page_icon="🧠", layout="centered")
    
    st.title("🧠 WhisperMind - Voice AI Chatbot")
    st.markdown("*Local voice processing with Whisper & Ollama*")

    # Check Ollama
    ollama_available, models = check_ollama()
    # Use the first available model or default to phi if available
    if models:
        selected_model = models[0]
        print(f"📋 Available models: {models}")
        print(f"🎯 Using model: {selected_model}")
    else:
        selected_model = "phi:latest"
        print(f"⚠️ No models detected, defaulting to: {selected_model}")

    # Initialize voice processor
    if 'voice_processor' not in st.session_state:
        st.session_state.voice_processor = VoiceProcessor() if VOICE_AVAILABLE else None

    # Initialize session states
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if 'input_value' not in st.session_state:
        st.session_state.input_value = ""
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Modern styling
    st.markdown("""
    <style>
    .stApp > div:first-child {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 98% !important;
    }
    .main > div {
        max-width: 98% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .block-container {
        max-width: 98% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    .main-container {
        padding: 15px !important;
        margin: 5px 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    .stButton > button {
        height: 60px !important;
        border-radius: 30px !important;
        border: 3px solid #4f46e5 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-size: 20px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
        color: white !important;
    }
    .stButton > button:focus {
        color: white !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    .stButton > button:active {
        color: white !important;
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Text input and Send button
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Audio response preference
    audio_response = st.radio(
        "🔊 Audio Response",
        options=[True, False],
        format_func=lambda x: "🔊 On - Hear answer" if x else "🔇 Off - Text only",
        horizontal=True,
        index=0,
        key="audio_response_toggle"
    )
    
    st.markdown("---")
    
    # Input controls layout with send button on the right
    col_inputs, col_send = st.columns([3, 1])
    
    with col_inputs:
        # Text input section
        st.markdown("#### ✍️ Type Your Question")
        text_key = f"main_input_{st.session_state.get('input_counter', 0)}"
        user_input = st.text_input(
            "Type your question here...",
            value=st.session_state.input_value,
            placeholder="Ask me anything...",
            key=text_key,
            label_visibility="collapsed"
        )
        # Update session state with current input
        if user_input != st.session_state.input_value:
            st.session_state.input_value = user_input
        
        # Voice input section
        st.markdown("#### 🎤 Record Question")
        
        if VOICE_AVAILABLE:
            # Use dynamic key to clear audio input after sending
            audio_key = f"voice_input_{st.session_state.input_counter}"
            audio_bytes = st.audio_input("Click to record", key=audio_key, label_visibility="collapsed")
            
            if audio_bytes:
                # Process voice input
                audio_hash = hashlib.md5(audio_bytes.getvalue()).hexdigest()
                
                if 'last_audio_hash' not in st.session_state or st.session_state.last_audio_hash != audio_hash:
                    print(f"🎤 Processing new audio: {audio_hash[:8]}...")
                    st.session_state.last_audio_hash = audio_hash
                    
                    # Clear any previous transcription status
                    if 'transcription_status' in st.session_state:
                        del st.session_state.transcription_status
                    
                    with st.spinner("🎧 Transcribing..."):
                        text, error = st.session_state.voice_processor.transcribe_audio(audio_bytes)
                        
                        if text and text.strip():
                            print(f"✅ Transcription: '{text.strip()}'")
                            st.session_state.input_value = text.strip()
                            st.session_state.input_counter += 1  # Force input refresh
                            st.session_state.transcription_status = f"✅ {text.strip()}"
                            st.rerun()
                        else:
                            error_msg = error or "Could not understand audio"
                            st.session_state.transcription_status = f"❌ {error_msg}"
                            st.rerun()
            
            # Display current transcription status
            if 'transcription_status' in st.session_state:
                if st.session_state.transcription_status.startswith("✅"):
                    st.success(st.session_state.transcription_status)
                    st.caption("👆 Text added above - click Send when ready")
                else:
                    st.error(st.session_state.transcription_status)
        else:
            st.warning("🚫 Voice not available")
    
    with col_send:
        # Align send button to middle of input section
        st.write("")  # Top spacing
        st.write("")  # More spacing
        send_clicked = st.button("🚀 SEND\nQUESTION", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process send
    if send_clicked and user_input.strip():
        print(f"🚀 Sending: '{user_input.strip()}'")
        
        # Clear transcription status when sending
        if 'transcription_status' in st.session_state:
            del st.session_state.transcription_status
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        # Clear input fields after sending
        st.session_state.input_value = ""
        st.session_state.input_counter += 1  # This will clear both text and audio inputs
        
        with st.chat_message("user"):
            st.markdown(user_input.strip())
        
        # Generate response
        if ollama_available:
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    response = chat_with_ollama(user_input.strip(), selected_model)
                st.markdown(response)
                
                # Voice response with stop button (only if audio response is enabled)
                if VOICE_AVAILABLE and st.session_state.voice_processor and audio_response:
                    response_id = len(st.session_state.messages)
                    col_speak, col_stop = st.columns([3, 1])
                    with col_speak:
                        print(f"🔊 Starting TTS for response {response_id}...")
                        st.session_state.voice_processor.speak_text(response)
                        st.caption("🔊 Speaking response...")
                    with col_stop:
                        if st.button("🔇 Stop", key=f"stop_speech_{response_id}"):
                            print(f"🔇 Stopping speech for response {response_id}")
                            st.session_state.voice_processor.stop_speaking()
                            st.success("🔇 Speech stopped")
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.error("❌ Ollama not available. Please start Ollama first.")
            st.info("Install Ollama: https://ollama.ai")
        
        # Clear input after sending
        st.session_state.input_value = ""
        st.session_state.input_counter += 1  # Force input refresh
        st.rerun()

if __name__ == "__main__":
    main()