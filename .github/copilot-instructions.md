# Local Knowledge Chatbot with Voice Input

This project is a privacy-first, offline chatbot powered by Ollama that can:
- Answer questions from your local files using RAG (Retrieval Augmented Generation)
- Accept voice input via Whisper speech-to-text
- Respond with speech using Coqui TTS
- Run entirely offline without cloud dependencies

## Tech Stack
- **Language**: Python
- **LLM**: Ollama (llama3/mistral models)
- **Vector Database**: ChromaDB for RAG
- **Speech-to-Text**: OpenAI Whisper
- **Text-to-Speech**: Coqui TTS
- **UI**: Streamlit for web interface

## Project Structure
- `src/` - Main application code
- `data/` - Local documents for knowledge base
- `models/` - Downloaded models and embeddings
- `config/` - Configuration files
- `requirements.txt` - Python dependencies
- `README.md` - Setup and usage instructions

## Development Guidelines
- Prioritize privacy and offline functionality
- Use local models and processing only
- Implement proper error handling for model loading
- Optimize for memory usage with large language models
- Support multiple document formats (PDF, TXT, DOCX)