# 🧠 WhisperMind - Local Knowledge Chatbot with Voice Input

A privacy-first, offline AI chatbot that combines the power of Ollama's local language models with Retrieval Augmented Generation (RAG) and voice capabilities. WhisperMind can answer questions from your personal documents and interact with you through voice, all while keeping your data completely private and offline.

## ✨ Features

- **🔒 Privacy-First**: Runs entirely offline - no cloud dependencies
- **📚 RAG-Powered**: Answer questions from your local documents
- **🎤 Voice Input**: Speech-to-text using OpenAI Whisper
- **🔊 Voice Output**: Text-to-speech using Coqui TTS
- **🌐 Web Interface**: Beautiful Streamlit-based UI
- **💻 CLI Support**: Command-line interface for power users
- **📄 Multi-Format**: Supports PDF, DOCX, TXT, MD, HTML files
- **🚀 Local Models**: Powered by Ollama (Llama3, Mistral, etc.)

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
│   │   └── streamlit_app.py     # Streamlit web UI
│   └── chatbot.py         # Main chatbot class
├── data/                  # Your documents
│   └── documents/         # Place your files here
├── models/                # Downloaded models
├── config/                # Configuration files
│   └── config.yaml        # Main configuration
├── requirements.txt       # Python dependencies
├── main.py               # CLI entry point
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** - Download from [ollama.com](https://ollama.com)
3. **Git** (optional)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Silent-Canoe-WhisperMind
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

4. **Copy environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

5. **Add your documents**
   ```bash
   # Place your documents in data/documents/
   # Supported formats: PDF, DOCX, TXT, MD, HTML
   ```

### Usage

#### Web Interface (Recommended)

Launch the beautiful Streamlit web interface:

```bash
python main.py --ui
```

Then open your browser to `http://localhost:8501`

#### Command Line Interface

For a simple CLI chat experience:

```bash
python main.py
```

#### Load Documents Only

To process documents without starting chat:

```bash
python main.py --load-docs data/documents
```

#### Test the System

Run a quick test to verify everything works:

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