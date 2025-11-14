# 🧠 WhisperMind - Local Knowledge Chatbot with Voice Input

A privacy-first, offline AI chatbot that combines the power of Ollama's local language models with Retrieval Augmented Generation (RAG) and voice capabilities. WhisperMind can answer questions from your personal documents and interact with you through voice, all while keeping your data completely private and offline.

## 🎥 Demo

### Watch WhisperMind in Action

<div align="center">

**🎬 Demo Video 1 - Core Chat Features**

https://github.com/user-attachments/assets/2bb9d392-1953-437e-b829-0a7785c3a952

*Full demo showcasing document RAG, voice interaction, and privacy-first AI chat*

**🎬 Demo Video 2 - Enhanced Voice Features**

https://private-user-images.githubusercontent.com/21079636/514573706-2dcbad40-33bb-4a3b-bbed-318f38ef8991.mov?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjMxNDY5NzIsIm5iZiI6MTc2MzE0NjY3MiwicGF0aCI6Ii8yMTA3OTYzNi81MTQ1NzM3MDYtMmRjYmFkNDAtMzNiYi00YTNiLWJiZWQtMzE4ZjM4ZWY4OTkxLm1vdj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTExMTQlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMTE0VDE4NTc1MlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWU0NWExNzlhNTkyZTNhNTRlZGFiNDQ5OWI1NjAwODg5YjkzMmM4N2QzMGQ1ZTgzNjM4NmRkZGRlMzAxNDJmZWEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.rm_DabHX3to2AqadUU9XAlZN8crRKEtLlJjlhdy6eb8

*Enhanced voice features with audio controls and speech toggle functionality*

</div>

**Key Features Demonstrated:**
- 🔒 **100% Offline Operation** - No data leaves your machine
- 💬 **Smart Chat Interface** - Real-time conversations with local AI models
- 🤖 **Multiple LLM Support** - Compatible with various Ollama models
- ⚡ **Fast Performance** - Optimized local inference with minimal latency
- 🎯 **Easy Setup** - Quick start with simple interface
- 🎤 **Voice Input & Output** - Speech-to-text with Whisper & controllable TTS
- 🔊 **Audio Controls** - Toggle audio responses on/off with radio buttons

**Additional Features (Full Version):**
- 📚 Document RAG capabilities (requires full setup)
- 🎤 Voice interaction (Whisper STT + TTS) - *Code ready, needs dependencies*

> 📖 *See [DEMO.md](DEMO.md) for detailed feature highlights and use cases*

## ✨ Features

- **🔒 100% Privacy-First**: Runs entirely offline - no cloud dependencies, no data tracking
- **📚 Smart Document RAG**: Answer questions from your local documents with AI-powered search
- **🎤 Voice Input**: Speech-to-text using OpenAI Whisper *(requires dependencies)*
- **🔊 Voice Output**: Text-to-speech responses *(requires dependencies)*
- **🌐 Beautiful Web Interface**: Intuitive Streamlit-based UI with real-time chat
- **💻 CLI Support**: Command-line interface for developers and power users
- **📄 Multi-Format Support**: Works with PDF, DOCX, TXT, MD, HTML files
- **🚀 Local LLM Power**: Powered by Ollama (Llama3, Mistral, CodeLlama, etc.)
- **⚡ Fast & Efficient**: Optimized for local inference with smart caching
- **🔧 Highly Configurable**: Customize models, voice settings, and RAG parameters
- **🌍 Cross-Platform**: Works seamlessly on macOS, Linux, and Windows

## 📊 Current Status

### ✅ What Works Now (No Additional Setup)
- **Basic AI Chat**: Immediate conversation with Ollama models
- **Model Selection**: Choose from your installed Ollama models
- **Simple Interface**: Clean web UI at `simple_streamlit_app.py`
- **Privacy-First**: 100% offline operation

### 🔧 Advanced Features (Requires Full Setup)
- **Document RAG**: Upload and query documents (needs `pip install -r requirements.txt`)
- **Voice Interaction**: Speech input/output (code ready, needs Whisper + TTS dependencies)
- **Advanced UI**: Full-featured interface with document management
- **CLI Tools**: Command-line interface for power users

*👆 The voice features are fully implemented in the codebase but require additional dependencies to run*

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **LLM**: Ollama (Llama3, Mistral, CodeLlama)
- **Vector Database**: ChromaDB for document embeddings
- **Speech-to-Text**: OpenAI Whisper
- **Text-to-Speech**: Coqui TTS
- **Web UI**: Streamlit
- **Document Processing**: PyPDF, python-docx, BeautifulSoup4

## 📁 Project Structure

```
WhisperMind/
├── src/                    # Main application code
│   ├── core/              # Core components
│   │   ├── ollama_client.py    # Ollama API client
│   │   └── config.py           # Configuration management
│   ├── rag/               # RAG system
│   │   ├── document_processor.py  # Document processing
│   │   ├── vector_store.py      # ChromaDB vector store
│   │   └── retriever.py         # Document retrieval
│   ├── voice/             # Voice processing
│   │   ├── speech_to_text.py    # Whisper STT
│   │   └── text_to_speech.py    # Coqui TTS
│   ├── ui/                # User interfaces
│   │   └── streamlit_app.py     # Advanced Streamlit web UI
│   └── chatbot.py         # Main chatbot class
├── data/                  # Your documents
│   └── documents/         # Place your files here
├── models/                # Downloaded models
├── config/                # Configuration files
│   └── config.yaml        # Main configuration
├── launch.py              # Main launcher (cross-platform)
├── simple_streamlit_app.py # Simple UI for quick testing
├── main.py               # CLI entry point
├── requirements.txt       # Python dependencies
├── DEMO.md               # Demo video and features
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** - Download from [ollama.com](https://ollama.com)
3. **Git** (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/koushal13/WhisperMind.git
   cd WhisperMind
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and start Ollama**
   ```bash
   # Download Ollama from https://ollama.com
   # Then pull a model (this may take a few minutes)
   ollama pull llama3
   ```

4. **Quick Start with Simple Interface**
   ```bash
   # For immediate testing with basic features
   python3 -m streamlit run simple_streamlit_app.py --server.port 8502
   ```

5. **Full Application Launch**
   ```bash
   # For complete features including RAG and voice
   python launch.py
   ```

6. **Add your documents (optional)**
   ```bash
   # Place your documents in data/documents/
   # Supported formats: PDF, DOCX, TXT, MD, HTML
   ```

### Usage

#### Quick Start - Simple Interface

For immediate testing with basic chat functionality (no additional dependencies needed):

```bash
python3 -m streamlit run simple_streamlit_app.py --server.port 8502
```

Then open your browser to `http://localhost:8502`

**Current Features:** Chat with Ollama models, model selection, conversation history

#### Full Application - Advanced Features

Launch with advanced features (requires `pip install -r requirements.txt`):

```bash
python launch.py
```

Then open your browser to `http://localhost:8501`

**Additional Features:** Document RAG, voice interaction, advanced configuration

#### Web Interface Features

- **Real-time Chat**: Instant responses with message history
- **Document Upload**: Drag & drop files to add to knowledge base
- **Voice Controls**: Enable microphone input and audio responses
- **Model Selection**: Choose from available Ollama models
- **Settings Panel**: Customize temperature, tokens, and RAG parameters

#### Command Line Interface

For developers and CLI enthusiasts:

```bash
python main.py
```

#### Document Processing Only

To index documents without starting chat:

```bash
python main.py --load-docs data/documents
```

#### System Test

Verify your installation:

```bash
python main.py --test
```

## 📚 Adding Documents

1. Place your documents in the `data/documents/` folder
2. Supported formats:
   - **PDF** files (`.pdf`)
   - **Word documents** (`.docx`)
   - **Text files** (`.txt`)
   - **Markdown** (`.md`)
   - **HTML** (`.html`, `.htm`)

3. The system will automatically process and index them for search

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
# Example configuration
ollama:
  model: "llama3"  # or mistral, codellama, etc.
  temperature: 0.7
  
voice:
  enabled: true
  whisper_model: "base"  # tiny, base, small, medium, large
  
rag:
  top_k: 5  # Number of documents to retrieve
  similarity_threshold: 0.7
```

## 🎤 Voice Features

### Speech-to-Text (Whisper)
- Models: `tiny`, `base`, `small`, `medium`, `large`
- Automatic language detection
- High accuracy transcription

### Text-to-Speech (Coqui TTS)
- Natural-sounding voices
- Multiple language support
- Configurable speakers

## 🔧 Advanced Usage

### Multiple Interfaces

WhisperMind offers flexible usage options:

1. **Simple Interface** (`simple_streamlit_app.py`):
   - Quick testing and basic chat
   - Minimal dependencies
   - Fast startup

2. **Full Interface** (`launch.py`):
   - Complete RAG functionality
   - Voice features
   - Document management
   - Advanced settings

### Custom Ollama Models

```bash
# Use different models
ollama pull mistral
ollama pull codellama
```

Then update `config/config.yaml`:
```yaml
ollama:
  model: "mistral"
```

### GPU Acceleration

For faster processing with NVIDIA GPUs:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Custom Embedding Models

Edit the configuration to use different embedding models:

```yaml
chromadb:
  embedding_model: "all-mpnet-base-v2"  # Higher quality embeddings
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not found**
   - Make sure Ollama is installed and running
   - Check if `ollama` command works in terminal

2. **Model not available**
   - Pull the model: `ollama pull llama3`
   - Check available models: `ollama list`

3. **Voice features not working**
   - Install additional audio dependencies:
     ```bash
     pip install librosa soundfile
     ```

4. **Out of memory errors**
   - Use smaller models (`tiny` Whisper, smaller Ollama models)
   - Reduce `chunk_size` in configuration

5. **Slow performance**
   - Use GPU if available
   - Reduce `max_tokens` in configuration
   - Use smaller models

### Performance Tips

- **For laptops**: Use `whisper: tiny` and `ollama: llama3:8b`
- **For desktops**: Use `whisper: base` and `ollama: llama3:70b`
- **For servers**: Use `whisper: large` and largest available models

## 🧪 Development

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/
```

### Code Formatting

```bash
pip install black flake8
black src/
flake8 src/
```

### Adding New Document Types

Extend `src/rag/document_processor.py` to support additional formats.

## 📋 Requirements

- **System**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ for models and documents
- **Python**: 3.8 or higher

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **OpenAI Whisper** - Speech recognition
- **Coqui TTS** - Text-to-speech synthesis
- **ChromaDB** - Vector database
- **Streamlit** - Web interface framework

## 📞 Support

- Check the [Issues](issues) page for known problems
- Create a new issue for bugs or feature requests
- Join discussions in the community

---

**Happy chatting with WhisperMind! 🧠💬**