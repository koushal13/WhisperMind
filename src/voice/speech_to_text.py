"""
Speech-to-text processing using OpenAI Whisper.
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import whisper
    import torch
except ImportError as e:
    logging.warning(f"Whisper or torch not available: {e}")

logger = logging.getLogger(__name__)


class SpeechToText:
    """Speech-to-text processor using OpenAI Whisper."""
    
    SUPPORTED_MODELS = [
        "tiny",      # ~39 MB, fastest
        "base",      # ~74 MB, good balance
        "small",     # ~244 MB, better accuracy
        "medium",    # ~769 MB, high accuracy
        "large",     # ~1550 MB, best accuracy
    ]
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize speech-to-text processor.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda, auto)
        """
        if model_size not in self.SUPPORTED_MODELS:
            logger.warning(f"Unknown model size '{model_size}', using 'base'")
            model_size = "base"
        
        self.model_size = model_size
        self.device = device or self._get_optimal_device()
        self.model = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the Whisper model."""
        if self._initialized:
            return
        
        try:
            logger.info(f"Loading Whisper model '{self.model_size}' on device '{self.device}'")
            
            # Load model in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None,
                lambda: whisper.load_model(self.model_size, device=self.device)
            )
            
            self._initialized = True
            logger.info("Speech-to-text model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize speech-to-text: {e}")
            raise
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (auto-detect if None)
            task: Either 'transcribe' or 'translate'
            
        Returns:
            Transcribed text
        """
        if not self._initialized:
            await self.initialize()
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            
            # Transcribe in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_path,
                    language=language,
                    task=task,
                    fp16=torch.cuda.is_available()
                )
            )
            
            transcribed_text = result["text"].strip()
            detected_language = result.get("language", "unknown")
            
            logger.info(f"Transcription complete (language: {detected_language})")
            logger.debug(f"Transcribed text: {transcribed_text}")
            
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"Error during transcription: {str(e)}"
    
    async def transcribe_with_timestamps(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe with word-level timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Language code (auto-detect if None)
            
        Returns:
            Dictionary with text, segments, and timing information
        """
        if not self._initialized:
            await self.initialize()
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            logger.info(f"Transcribing with timestamps: {audio_path}")
            
            # Transcribe in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_path,
                    language=language,
                    word_timestamps=True,
                    fp16=torch.cuda.is_available()
                )
            )
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": result.get("duration", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Timestamped transcription failed: {e}")
            return {
                "text": f"Error during transcription: {str(e)}",
                "language": "unknown",
                "segments": [],
                "duration": 0.0
            }
    
    async def transcribe_realtime(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio data from memory (for real-time processing).
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate
            language: Language code
            
        Returns:
            Transcribed text
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribe the temporary file
                result = await self.transcribe(temp_path, language=language)
                return result
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Real-time transcription failed: {e}")
            return f"Error during real-time transcription: {str(e)}"
    
    def _get_optimal_device(self) -> str:
        """Determine the optimal device for processing."""
        try:
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon
            else:
                return "cpu"
        except:
            return "cpu"
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "initialized": self._initialized,
            "supported_models": self.SUPPORTED_MODELS
        }
    
    async def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
            self.model = None
        
        # Clear CUDA cache if using GPU
        if self.device == "cuda" and torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self._initialized = False
        logger.info("Speech-to-text cleanup complete")


# Example usage
if __name__ == "__main__":
    async def main():
        stt = SpeechToText(model_size="base")
        
        try:
            await stt.initialize()
            
            # Test with a sample audio file (if available)
            audio_file = "test_audio.wav"  # Replace with actual audio file
            
            if os.path.exists(audio_file):
                # Basic transcription
                text = await stt.transcribe(audio_file)
                print(f"Transcribed text: {text}")
                
                # Transcription with timestamps
                detailed = await stt.transcribe_with_timestamps(audio_file)
                print(f"Language: {detailed['language']}")
                print(f"Duration: {detailed['duration']:.2f}s")
                print(f"Segments: {len(detailed['segments'])}")
            else:
                print(f"Audio file {audio_file} not found. Skipping transcription test.")
            
            # Model info
            info = await stt.get_model_info()
            print(f"Model info: {info}")
            
        finally:
            await stt.cleanup()
    
    asyncio.run(main())