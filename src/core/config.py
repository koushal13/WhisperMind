"""
Configuration management for WhisperMind chatbot.
"""

import yaml
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Ollama LLM configuration."""
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class ChromaDBConfig:
    """ChromaDB vector store configuration."""
    persist_directory: str = "models/chromadb"
    collection_name: str = "documents"
    embedding_model: str = "all-MiniLM-L6-v2"


@dataclass
class RAGConfig:
    """RAG system configuration."""
    top_k: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7


@dataclass
class VoiceConfig:
    """Voice processing configuration."""
    enabled: bool = True
    whisper_model: str = "base"  # tiny, base, small, medium, large
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"
    audio_sample_rate: int = 16000


@dataclass
class UIConfig:
    """User interface configuration."""
    streamlit_host: str = "localhost"
    streamlit_port: int = 8501
    theme: str = "dark"
    show_source_documents: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None


class Config:
    """Main configuration class."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize configuration from file or defaults.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        
        # Initialize with defaults
        self.ollama = OllamaConfig()
        self.chromadb = ChromaDBConfig()
        self.rag = RAGConfig()
        self.voice = VoiceConfig()
        self.ui = UIConfig()
        self.logging = LoggingConfig()
        
        # Load from file if it exists
        self.load_config()
        
        # Create directories
        self._create_directories()
        
        # Setup logging
        self._setup_logging()
    
    def load_config(self):
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found at {self.config_path}, using defaults")
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Update configurations
            if 'ollama' in config_data:
                self._update_dataclass(self.ollama, config_data['ollama'])
            
            if 'chromadb' in config_data:
                self._update_dataclass(self.chromadb, config_data['chromadb'])
            
            if 'rag' in config_data:
                self._update_dataclass(self.rag, config_data['rag'])
            
            if 'voice' in config_data:
                self._update_dataclass(self.voice, config_data['voice'])
            
            if 'ui' in config_data:
                self._update_dataclass(self.ui, config_data['ui'])
            
            if 'logging' in config_data:
                self._update_dataclass(self.logging, config_data['logging'])
            
            logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
    
    def save_config(self):
        """Save current configuration to YAML file."""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_data = {
                'ollama': self._dataclass_to_dict(self.ollama),
                'chromadb': self._dataclass_to_dict(self.chromadb),
                'rag': self._dataclass_to_dict(self.rag),
                'voice': self._dataclass_to_dict(self.voice),
                'ui': self._dataclass_to_dict(self.ui),
                'logging': self._dataclass_to_dict(self.logging)
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _update_dataclass(self, dataclass_obj, data: Dict[str, Any]):
        """Update dataclass fields from dictionary."""
        for key, value in data.items():
            if hasattr(dataclass_obj, key):
                setattr(dataclass_obj, key, value)
    
    def _dataclass_to_dict(self, dataclass_obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        result = {}
        for field_name in dataclass_obj.__dataclass_fields__:
            result[field_name] = getattr(dataclass_obj, field_name)
        return result
    
    def _create_directories(self):
        """Create necessary directories."""
        directories = [
            self.chromadb.persist_directory,
            "data/documents",
            "models",
            "logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            format=self.logging.format,
            handlers=[]
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(self.logging.format)
        console_handler.setFormatter(formatter)
        
        # Add file handler if specified
        handlers = [console_handler]
        if self.logging.file_path:
            os.makedirs(os.path.dirname(self.logging.file_path), exist_ok=True)
            file_handler = logging.FileHandler(self.logging.file_path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        
        # Apply to root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        for handler in handlers:
            root_logger.addHandler(handler)
    
    def get_env_var(self, key: str, default: Any = None) -> Any:
        """Get environment variable with fallback to default."""
        return os.getenv(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire configuration to dictionary."""
        return {
            'ollama': self._dataclass_to_dict(self.ollama),
            'chromadb': self._dataclass_to_dict(self.chromadb),
            'rag': self._dataclass_to_dict(self.rag),
            'voice': self._dataclass_to_dict(self.voice),
            'ui': self._dataclass_to_dict(self.ui),
            'logging': self._dataclass_to_dict(self.logging)
        }


# Example usage
if __name__ == "__main__":
    config = Config()
    
    print("Current configuration:")
    for key, value in config.to_dict().items():
        print(f"{key}: {value}")
    
    # Save default configuration
    config.save_config()
    print(f"Configuration saved to {config.config_path}")