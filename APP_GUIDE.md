# WhisperMind App Guide

## 📱 Available Applications

### 🚀 `whispermind_minimal.py` - **RECOMMENDED FOR DAILY USE**
**Simple, clean, and efficient voice AI chatbot**

#### ✅ When to Use:
- **Quick voice conversations** with AI
- **Clean, distraction-free** interface
- **Fast startup** and lightweight performance
- **Focus on core functionality** only
- **Daily use** and quick queries

#### 🎯 Features:
- ✅ Voice recording with Whisper transcription
- ✅ Text input with auto-clear after sending
- ✅ AI responses with voice output (TTS)
- ✅ Full-width layout (95% screen width)
- ✅ Clean workflow: Record → Review → Send → Hear Response
- ✅ Local Ollama integration (phi:latest model)

#### 🚀 To Run:
```bash
python3 -m streamlit run whispermind_minimal.py --server.port=8509
```

---

### ⚙️ `whispermind_full_featured.py` - **ADVANCED USERS**
**Feature-rich version with extensive customization**

#### ✅ When to Use:
- **Need advanced audio processing** options
- **Want sidebar configuration** controls
- **Require fallback mechanisms** for audio
- **Development and testing** purposes
- **Complex voice processing** scenarios

#### 🎯 Features:
- ✅ Everything from minimal version PLUS:
- ✅ Sidebar with model selection
- ✅ Multiple audio processing fallbacks
- ✅ Advanced error handling and recovery
- ✅ Complex status management system
- ✅ Multiple voice engine options
- ✅ Extensive configuration options
- ✅ HTTP-based Ollama integration

#### 🚀 To Run:
```bash
python3 -m streamlit run whispermind_full_featured.py --server.port=8507
```

---

## 🎯 Quick Decision Guide

### Choose **whispermind_minimal.py** if you want:
- ✅ **Simple daily use**
- ✅ **Fast and clean**
- ✅ **Just voice chat with AI**
- ✅ **No configuration needed**

### Choose **whispermind_full_featured.py** if you want:
- ✅ **Advanced customization**
- ✅ **Multiple audio options**
- ✅ **Sidebar controls**
- ✅ **Development features**

---

## 📊 Comparison Table

| Feature | Minimal | Full-Featured |
|---------|---------|---------------|
| **File Size** | 402 lines | 868 lines |
| **UI Layout** | Full-width, no sidebar | Wide layout + sidebar |
| **Voice Processing** | Single method | Multiple fallbacks |
| **Ollama Integration** | Native Python package | HTTP requests |
| **Startup Time** | Fast | Slower |
| **Memory Usage** | Lower | Higher |
| **Configuration** | Auto | Manual options |
| **Best For** | Daily use | Power users |

---

## 🔧 Current Recommendation

**Use `whispermind_minimal.py`** - It's currently running and optimized for your workflow:
- Clean interface with no clutter
- Voice recordings clear after sending
- TTS working for all responses
- Full-width layout for better UX
- All core functionality you need

**URL:** http://localhost:8509 (when running minimal version)