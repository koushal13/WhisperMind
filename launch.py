"""
Simple launcher for WhisperMind with basic error handling.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_ollama():
    """Check if Ollama is running."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def start_ollama():
    """Start Ollama server."""
    print("🚀 Starting Ollama server...")
    try:
        subprocess.Popen(['ollama', 'serve'], shell=True)
        print("✅ Ollama server started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Ollama: {e}")
        return False

def launch_streamlit():
    """Launch Streamlit app."""
    # Try virtual environment first, fall back to system Python
    if sys.platform == "win32":
        venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = Path(__file__).parent / ".venv" / "bin" / "python"
    
    # Use virtual environment if it exists, otherwise use current Python
    if venv_python.exists():
        python_path = str(venv_python)
    else:
        python_path = sys.executable
        print("⚠️  Virtual environment not found, using system Python")
    
    app_path = Path(__file__).parent / "src" / "ui" / "streamlit_app.py"
    
    print("🌐 Launching WhisperMind web interface...")
    print("📱 The app will open at: http://localhost:8501")
    print("🔄 This may take a moment to load...")
    
    try:
        subprocess.run([
            python_path, "-m", "streamlit", "run", 
            str(app_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 WhisperMind stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")

def main():
    """Main launcher function."""
    print("🧠 WhisperMind - Local AI Chatbot Launcher")
    print("="*50)
    
    # Check if Ollama is available
    if not check_ollama():
        print("⚠️  Ollama not found or not running")
        
        # Try to start Ollama
        if not start_ollama():
            print("❌ Please install Ollama from: https://ollama.com")
            print("   Then run: ollama pull llama3")
            return
        
        # Wait a moment for Ollama to start
        import time
        time.sleep(3)
    
    print("✅ Ollama is available")
    
    # Launch Streamlit
    launch_streamlit()

if __name__ == "__main__":
    main()