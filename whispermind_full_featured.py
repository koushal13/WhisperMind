"""
WhisperMind - Enhanced Full-Featured Voice-Enabled AI Chatbot

Author: koushal13 (https://github.com/koushal13)
Repository: https://github.com/koushal13/WhisperMind
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
WHISPER_LOCAL_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    import whisper  # Local Whisper model
    VOICE_AVAILABLE = True
    WHISPER_LOCAL_AVAILABLE = True
    # For microphone, we'll use Streamlit's audio_input instead of pyaudio
    MICROPHONE_AVAILABLE = True  # We'll use browser-based recording
except ImportError as e:
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
        self.tts_engine = None
        self.is_speaking = False
        self._speaking_lock = threading.Lock()
        
        if VOICE_AVAILABLE:
            # Initialize local Whisper model silently in background
            if not hasattr(st.session_state, 'whisper_model'):
                import whisper
                st.session_state.whisper_model = whisper.load_model("base")
            
            try:
                self.recognizer = sr.Recognizer()
                
                # Initialize TTS with better voice settings
                self.tts_engine = pyttsx3.init()
                
                # Configure TTS for clear male voice
                voices = self.tts_engine.getProperty('voices')
                if voices and len(voices) > 0:
                    # Try to find a good male voice
                    male_voice = None
                    for voice in voices:
                        # Check for male voices or specific good voices on macOS
                        voice_name = voice.name.lower()
                        if any(name in voice_name for name in ['alex', 'daniel', 'thomas', 'male']):
                            male_voice = voice
                            break
                    
                    # Use male voice if found, otherwise use default
                    if male_voice:
                        self.tts_engine.setProperty('voice', male_voice.id)
                        print(f"Using voice: {male_voice.name}")
                    else:
                        self.tts_engine.setProperty('voice', voices[0].id)
                        print(f"Using default voice: {voices[0].name}")
                
                # Set optimal speech parameters for clarity
                self.tts_engine.setProperty('rate', 175)  # Good speaking pace
                self.tts_engine.setProperty('volume', 1.0)  # Full volume
                
            except Exception as e:
                st.error(f"Voice initialization error: {e}")
                self.recognizer = None
    
    def convert_audio_for_recognition(self, audio_data):
        """Convert audio data to a format compatible with speech recognition, avoiding FLAC issues."""
        try:
            # Handle both raw bytes and UploadedFile objects
            if hasattr(audio_data, 'getvalue'):
                audio_bytes = audio_data.getvalue()
            else:
                audio_bytes = audio_data
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            return tmp_path
        except Exception as e:
            raise Exception(f"Audio conversion error: {e}")

    def listen_for_speech_browser(self, audio_data):
        """Process audio using completely local Whisper model - 100% offline, no internet."""
        print("🔍 Whisper: Starting audio processing...")
        try:
            # Handle both raw bytes and UploadedFile objects
            if hasattr(audio_data, 'getvalue'):
                audio_bytes = audio_data.getvalue()
            else:
                audio_bytes = audio_data
            
            print(f"📊 Audio size: {len(audio_bytes)} bytes")
            
            # Basic audio validation
            if len(audio_bytes) < 1000:
                print("⚠️ Audio too short")
                return None, "Audio too short - please record a longer message"
            
            # Create temporary file for local Whisper processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            try:
                # Use local Whisper model - completely offline!
                print("🧠 Checking Whisper model availability...")
                if hasattr(st.session_state, 'whisper_model'):
                    try:
                        print("🎯 Running Whisper transcription...")
                        # Try direct Whisper transcription
                        result = st.session_state.whisper_model.transcribe(tmp_path)
                        transcribed_text = result["text"].strip()
                        print(f"📝 Raw transcription: '{transcribed_text}'")
                        
                        if transcribed_text:
                            print(f"✅ Transcription successful!")
                            return transcribed_text, None
                        else:
                            print("❌ Empty transcription result")
                            return None, "Could not understand the audio - please speak more clearly"
                    except Exception as whisper_error:
                        print(f"❌ Whisper error: {str(whisper_error)}")
                        # If ffmpeg is missing, provide helpful message
                        error_msg = str(whisper_error)
                        if "ffmpeg" in error_msg.lower() or "no such file" in error_msg.lower():
                            return None, "🔧 Audio processing requires ffmpeg. Install with: brew install ffmpeg. For now, please type your message."
                        else:
                            return None, f"Whisper processing error: {str(whisper_error)[:100]}"
                else:
                    print("❌ Whisper model not found in session state")
                    return None, "Local Whisper model not loaded. Please refresh the page."
                        
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            return None, f"Audio processing error: {str(e)[:100]}"

    
    def _manual_audio_processing(self, audio_file_path):
        """Manual audio processing when standard methods fail."""
        try:
            # Read the raw audio file and attempt basic recognition
            import wave
            import struct
            
            # Try to open as WAV and read basic info
            with wave.open(audio_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / sample_rate
                
                if duration < 0.1:
                    return None, "Audio too short - please record a longer message"
                elif duration > 30:
                    return None, "Audio too long - please keep recordings under 30 seconds"
                
            # For now, provide a helpful message while we work on the technical issue
            return None, "🎤 Voice processing detected your audio but transcription needs fixing. Please type your message for now."
            
        except Exception as e:
            return None, "Please type your message in the text box below."
    
    def _fallback_speech_recognition(self, audio_content):
        """Fallback method that shows instructions for users when FLAC fails."""
        try:
            # Provide helpful message and alternative
            message = """
            🎤 Voice recognition temporarily unavailable due to system compatibility.
            
            **Alternative options:**
            1. Type your question in the text box
            2. Upload a different audio format
            3. Try refreshing the page
            
            **Technical note:** This is a known issue with FLAC audio processing on some Mac systems.
            """
            return None, message.strip()
        except Exception as e:
            return None, f"System compatibility issue. Please use text input instead."
    
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
        """Convert text to speech with thread safety."""
        if not self.tts_engine or not text.strip():
            return False
        
        # Prevent multiple simultaneous speech operations
        if self.is_speaking:
            return False
            
        try:
            with self._speaking_lock:
                if self.is_speaking:  # Double-check after acquiring lock
                    return False
                
                self.is_speaking = True
                
                def speak_safely():
                    try:
                        # Use a fresh engine instance to avoid run loop conflicts
                        temp_engine = pyttsx3.init()
                        
                        # Copy settings from main engine
                        voices = temp_engine.getProperty('voices')
                        if voices:
                            for voice in voices:
                                voice_name = voice.name.lower()
                                if any(name in voice_name for name in ['alex', 'daniel', 'thomas', 'male']):
                                    temp_engine.setProperty('voice', voice.id)
                                    break
                        
                        temp_engine.setProperty('rate', 175)
                        temp_engine.setProperty('volume', 1.0)
                        
                        # Speak the text
                        temp_engine.say(text)
                        temp_engine.runAndWait()
                        
                        # Clean up
                        temp_engine.stop()
                        del temp_engine
                        
                    except Exception as e:
                        print(f"TTS Error: {e}")
                    finally:
                        self.is_speaking = False
                
                # Run in background thread
                thread = threading.Thread(target=speak_safely, daemon=True)
                thread.start()
                return True
                
        except Exception as e:
            self.is_speaking = False
            print(f"Text-to-speech error: {e}")
            return False
    
    def speak(self, text):
        """Alias for speak_text method for compatibility."""
        return self.speak_text(text)
    
    def stop_speaking(self):
        """Stop any ongoing speech synthesis."""
        try:
            with self._speaking_lock:
                if self.is_speaking:
                    self.is_speaking = False
                    # Try to stop the main engine if it exists
                    if self.tts_engine:
                        try:
                            self.tts_engine.stop()
                        except:
                            pass  # Ignore stop errors
                return True
        except Exception as e:
            print(f"Error stopping speech: {e}")
            return False

def main():
    st.title("🧠 WhisperMind - Local AI Chatbot with Voice")
    
    # Enhanced custom CSS for modern UI
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border: 2px solid #e1e8ed !important;
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        background: #fafbfc !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background: white !important;
    }
    
    /* Modern text input styling */
    .stTextInput > div > div > input {
        border: none !important;
        background: transparent !important;
        font-size: 16px !important;
        padding: 15px 0 !important;
        height: auto !important;
        line-height: 1.5 !important;
    }
    
    .stTextInput > div > div > input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Clean button styling - uniform for all buttons */
    .stButton > button {
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        border: none !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #f8fafc !important;
        color: #64748b !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(0,0,0,0.15) !important;
        background: #e2e8f0 !important;
    }
    
    /* Primary send button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
    }
    
    /* Primary button (Send) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background: white !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
        border: 1px solid #f0f2f6 !important;
    }
    
    /* Success/error messages */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* Voice status */
    .voice-status {
        font-size: 12px;
        color: #8899a6;
        text-align: center;
        margin-top: 10px;
        font-style: italic;
    }
    
    /* Voice button styling - exact same size as other buttons */
    .stAudio button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 3px 15px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stAudio button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.4) !important;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        
        if VOICE_AVAILABLE:
            st.success("✅ Voice features available - 100% LOCAL & OFFLINE")
            st.info("🔒 **Completely Local**: Using local Whisper model - no internet required, full privacy!")
            
            # Check if ffmpeg is available
            import subprocess
            ffmpeg_available = False
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                ffmpeg_available = True
                st.success("✅ ffmpeg installed - voice recognition ready!")
            except:
                st.warning("⚠️ ffmpeg not found - voice input needs setup")
                with st.expander("🔧 Click to see ffmpeg installation instructions"):
                    st.markdown("""
                    **Install ffmpeg for voice recognition:**
                    
                    1. **Install Homebrew** (if not already installed):
                    ```bash
                    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                    ```
                    
                    2. **Install ffmpeg**:
                    ```bash
                    brew install ffmpeg
                    ```
                    
                    3. **Restart this app**
                    
                    *For now, you can still use text input below!*
                    """)
            
            voice_input_enabled = st.checkbox("Enable Voice Input", value=ffmpeg_available, key="voice_input_cb")
            voice_output_enabled = st.checkbox("Enable Voice Output (Male Voice)", value=True, key="voice_output_cb")
        else:
            st.error("❌ Voice features unavailable")
            st.info("💡 Install voice packages:")
            st.code("pip install speechrecognition pyttsx3 pyobjc-core pyobjc-framework-Cocoa")
            voice_input_enabled = False
            voice_output_enabled = False
        
        st.divider()

    # Initialize voice processor silently after sidebar
    # Force re-initialization to ensure latest TTS fixes are applied
    if 'voice_processor' not in st.session_state or not hasattr(st.session_state.voice_processor, '_speaking_lock'):
        st.session_state.voice_processor = VoiceProcessor() if VOICE_AVAILABLE else None    # Display chat messages cleanly
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Chat messages without extra controls
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Clean, modern interface styling with perfect button alignment
    st.markdown("""
    <style>
    .main-chat-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 25px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    .input-row {
        display: flex;
        align-items: center;
        gap: 15px;
        background: white;
        padding: 12px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    .input-row:focus-within {
        border-color: #667eea;
        box-shadow: 0 4px 25px rgba(102, 126, 234, 0.15);
    }
    /* Ensure buttons are perfectly aligned with same height */
    .stButton, .stAudio {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 50px;
    }
    .stButton > button {
        height: 50px !important;
        min-height: 50px !important;
        width: 100% !important;
        border-radius: 25px !important;
        border: 2px solid #e2e8f0 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
    }
    .stAudio > div {
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .status-area {
        margin-top: 15px;
        min-height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .status-message {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        text-align: center;
        transition: all 0.3s ease;
    }
    .status-processing {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        animation: pulse 2s infinite;
    }
    .status-success {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    .status-error {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for voice transcription
    if 'voice_transcription' not in st.session_state:
        st.session_state.voice_transcription = ""
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    
    # Initialize status message state
    if 'status_message' not in st.session_state:
        st.session_state.status_message = ""
    if 'status_type' not in st.session_state:
        st.session_state.status_type = ""

    # Main chat interface - Clean and Simple
    with st.container():
        st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)
        
        # Single row with repositioned buttons: Text Input + Voice + (Send & Clear together)
        col1, col2, col3 = st.columns([8, 1, 2])
        
        with col1:
            # Initialize session state
            if 'input_value' not in st.session_state:
                st.session_state.input_value = ""
            
            # Update with voice transcription (but only show briefly)
            if st.session_state.voice_transcription:
                # Just show the transcription briefly but don't wait for manual send
                user_input_display = st.session_state.voice_transcription
                st.session_state.voice_transcription = ""
            else:
                user_input_display = st.session_state.input_value
            
            # Main text input - clean and full width
            user_input = st.text_input(
                "message",
                value=user_input_display,
                placeholder="Ask me anything...",
                key="main_chat_input",
                label_visibility="collapsed"
            )
            
            st.session_state.input_value = user_input
        
        with col2:
            # Voice button - only if available
            if VOICE_AVAILABLE and voice_input_enabled:
                audio_bytes = st.audio_input("Voice", label_visibility="collapsed", key="voice_recorder")
                
                if audio_bytes and not st.session_state.get('processing_voice', False):
                    print("🎤 Audio detected! Starting processing...")
                    import hashlib
                    try:
                        audio_data = audio_bytes.getvalue() if hasattr(audio_bytes, 'getvalue') else audio_bytes
                        audio_hash = hashlib.md5(audio_data).hexdigest()
                        print(f"🔍 Audio hash: {audio_hash[:8]}...")
                        
                        if 'last_audio_hash' not in st.session_state or st.session_state.last_audio_hash != audio_hash:
                            print("✅ New audio detected, processing...")
                            st.session_state.last_audio_hash = audio_hash
                            st.session_state.processing_voice = True
                            
                            # Set processing status
                            st.session_state.status_message = "🎤 Processing audio..."
                            st.session_state.status_type = "processing"
                        else:
                            print("🔄 Duplicate audio detected, skipping...")
                            
                            try:
                                print("🎧 Starting Whisper transcription...")
                                text, error = st.session_state.voice_processor.listen_for_speech_browser(audio_bytes)
                                
                                if text and text.strip():
                                    print(f"✅ Transcription successful: '{text.strip()}'")
                                    # Put transcription in text box and prompt user to send
                                    st.session_state.processing_voice = False
                                    
                                    # Add to input value (will show in text box)
                                    st.session_state.input_value = text.strip()
                                    st.session_state.voice_transcription = ""
                                    
                                    # Show prompt to click Send button
                                    st.session_state.status_message = f"✅ Ready to send: '{text.strip()[:40]}{'...' if len(text.strip()) > 40 else ''}' - Click 🚀 Send"
                                    st.session_state.status_type = "success"
                                    print("📝 Transcript written to text box - waiting for user to click Send")
                                    st.rerun()
                                else:
                                    error_msg = error or "Could not understand"
                                    print(f"❌ Transcription failed: {error_msg}")
                                    st.session_state.status_message = f"❌ {error_msg[:40]}{'...' if len(error_msg) > 40 else ''}"
                                    st.session_state.status_type = "error"
                                    st.session_state.processing_voice = False
                                    
                            except Exception as audio_error:
                                print(f"❌ Audio processing error: {str(audio_error)}")
                                st.session_state.status_message = f"❌ Audio error: {str(audio_error)[:30]}..."
                                st.session_state.status_type = "error"
                                st.session_state.processing_voice = False
                                
                    except Exception as e:
                        print(f"❌ General voice processing error: {str(e)}")
                        st.session_state.processing_voice = False
                        st.session_state.status_message = f"❌ Error: {str(e)[:30]}..."
                        st.session_state.status_type = "error"
            else:
                # Empty space if voice not available
                st.write("")
        
        with col3:
            # Send and Clear buttons together
            button_col1, button_col2 = st.columns([1, 1])
            
            with button_col1:
                # Send button
                send_clicked = st.button("🚀", key="send_btn", help="Send", type="primary")
            
            with button_col2:
                # Clear button
                if st.button("🗑️", key="clear_btn", help="Clear"):
                    st.session_state.messages = []
                    st.session_state.voice_transcription = ""
                    st.session_state.input_value = ""
                    st.session_state.status_message = ""
                    st.session_state.status_type = ""
                    if 'last_audio_hash' in st.session_state:
                        del st.session_state.last_audio_hash
                    if 'voice_recorder' in st.session_state:
                        del st.session_state.voice_recorder
                    st.rerun()
        
        # Dedicated status area below input
        st.markdown('<div class="status-area">', unsafe_allow_html=True)
        if st.session_state.status_message:
            status_class = f"status-{st.session_state.status_type}"
            st.markdown(f'<div class="status-message {status_class}">{st.session_state.status_message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    # Handle manual send button click
    if send_clicked and user_input.strip():
        print("🚀 Manual send button clicked!")
        input_text = user_input.strip()
        print(f"💭 Input text: '{input_text[:50]}{'...' if len(input_text) > 50 else ''}'")
        
        # Set processing status
        print("🤖 Starting AI processing...")
        st.session_state.status_message = "🤖 Processing your question..."
        st.session_state.status_type = "processing"
        
        process_user_input(input_text, selected_model, ollama_available, voice_output_enabled)
        print("✅ AI processing completed!")
        
        # Auto-speak the response if voice output is enabled
        if voice_output_enabled and st.session_state.messages:
            latest_message = st.session_state.messages[-1]
            if latest_message["role"] == "assistant":
                st.session_state.status_message = "🔊 Speaking response..."
                st.session_state.status_type = "processing"
                if st.session_state.voice_processor:
                    st.session_state.voice_processor.speak(latest_message["content"])
                    st.session_state.status_message = "✅ Response spoken!"
                    st.session_state.status_type = "success"
        
        # Clear everything after a brief moment
        st.session_state.input_value = ""
        st.session_state.voice_transcription = ""
        st.session_state.status_message = ""
        st.session_state.status_type = ""
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
                col_speak, col_stop = st.columns([3, 1])
                with col_speak:
                    st.session_state.voice_processor.speak_text(response)
                    st.caption("🔊 Speaking response...")
                with col_stop:
                    if st.button("🔇 Stop", key=f"stop_speak_{len(st.session_state.messages)}", help="Stop Speaking"):
                        if st.session_state.voice_processor:
                            st.session_state.voice_processor.stop_speaking()
                        st.success("🔇 Speech stopped")
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            error_msg = "Sorry, Ollama is not available. Please start Ollama first."
            st.error(error_msg)
            
            if VOICE_AVAILABLE and voice_output_enabled and st.session_state.voice_processor:
                col_speak, col_stop = st.columns([3, 1])
                with col_speak:
                    st.session_state.voice_processor.speak_text(error_msg)
                    st.caption("🔊 Speaking error...")
                with col_stop:
                    if st.button("🔇 Stop", key=f"stop_error_{len(st.session_state.messages)}", help="Stop Speaking"):
                        if st.session_state.voice_processor:
                            st.session_state.voice_processor.stop_speaking()
                        st.success("🔇 Speech stopped")

if __name__ == "__main__":
    main()