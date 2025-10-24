"""
Text-to-speech processing using pyttsx3 (system TTS).
"""

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import pyttsx3
    import soundfile as sf
    import numpy as np
except ImportError as e:
    logging.warning(f"TTS dependencies not available: {e}")

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech processor using pyttsx3 (system TTS)."""
    
    def __init__(
        self,
        voice_id: Optional[str] = None,
        rate: int = 200,
        volume: float = 0.9
    ):
        """
        Initialize text-to-speech processor.
        
        Args:
            voice_id: Voice ID to use (None for default)
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        
        self.engine = None
        self._initialized = False
        self._voices = []
    
    async def initialize(self):
        """Initialize the TTS engine."""
        if self._initialized:
            return
        
        try:
            logger.info("Initializing TTS engine...")
            
            # Initialize pyttsx3 in a separate thread
            loop = asyncio.get_event_loop()
            self.engine = await loop.run_in_executor(None, pyttsx3.init)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            self._voices = []
            
            if voices:
                for i, voice in enumerate(voices):
                    voice_info = {
                        'id': voice.id,
                        'name': voice.name,
                        'index': i,
                        'gender': getattr(voice, 'gender', 'unknown'),
                        'age': getattr(voice, 'age', 'unknown')
                    }
                    self._voices.append(voice_info)
                
                logger.info(f"Found {len(self._voices)} available voices")
                
                # Set voice if specified
                if self.voice_id:
                    await self.set_voice(self.voice_id)
                
            # Set properties
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            self._initialized = True
            logger.info("Text-to-speech engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            raise
    
    async def synthesize(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text and save to file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            voice_id: Voice ID to use (overrides default)
            
        Returns:
            Path to generated audio file
        """
        if not self._initialized:
            await self.initialize()
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            logger.info(f"Synthesizing speech: '{text[:50]}...'")
            
            # Set voice if specified
            if voice_id:
                await self.set_voice(voice_id)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Synthesize in a separate thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._synthesize_sync(text, output_path)
            )
            
            if os.path.exists(output_path):
                logger.info(f"Speech synthesis complete: {output_path}")
                return output_path
            else:
                raise RuntimeError("Audio file was not created")
                
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise
    
    def _synthesize_sync(self, text: str, output_path: str):
        """Synchronous synthesis method."""
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
    
    async def synthesize_to_memory(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> bytes:
        """
        Synthesize speech to memory (returns audio data).
        
        Args:
            text: Text to synthesize
            voice_id: Voice ID to use
            
        Returns:
            Audio data as bytes
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Synthesize to temporary file
            await self.synthesize(text, temp_path, voice_id)
            
            # Read audio data
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            return audio_data
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def speak(self, text: str, voice_id: Optional[str] = None):
        """
        Speak text directly (no file output).
        
        Args:
            text: Text to speak
            voice_id: Voice ID to use
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Speaking: '{text[:50]}...'")
            
            # Set voice if specified
            if voice_id:
                await self.set_voice(voice_id)
            
            # Speak in a separate thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._speak_sync(text)
            )
            
        except Exception as e:
            logger.error(f"Speech failed: {e}")
            raise
    
    def _speak_sync(self, text: str):
        """Synchronous speak method."""
        self.engine.say(text)
        self.engine.runAndWait()
    
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        if not self._initialized:
            await self.initialize()
        
        return self._voices.copy()
    
    async def set_voice(self, voice_id: str) -> bool:
        """
        Set voice for synthesis.
        
        Args:
            voice_id: Voice ID, name, or index
            
        Returns:
            True if voice is valid
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            # Try to find voice by ID, name, or index
            target_voice = None
            
            # Try by index first
            try:
                voice_index = int(voice_id)
                if 0 <= voice_index < len(self._voices):
                    target_voice = self._voices[voice_index]['id']
            except ValueError:
                pass
            
            # Try by ID or name
            if not target_voice:
                for voice in self._voices:
                    if voice_id in [voice['id'], voice['name']]:
                        target_voice = voice['id']
                        break
            
            if target_voice:
                self.engine.setProperty('voice', target_voice)
                self.voice_id = target_voice
                logger.info(f"Voice set to: {target_voice}")
                return True
            else:
                logger.error(f"Voice '{voice_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    async def set_rate(self, rate: int):
        """Set speech rate."""
        if not self._initialized:
            await self.initialize()
        
        self.rate = rate
        self.engine.setProperty('rate', rate)
        logger.info(f"Speech rate set to: {rate}")
    
    async def set_volume(self, volume: float):
        """Set speech volume."""
        if not self._initialized:
            await self.initialize()
        
        self.volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', self.volume)
        logger.info(f"Speech volume set to: {self.volume}")
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the TTS engine."""
        if not self._initialized:
            await self.initialize()
        
        return {
            "engine": "pyttsx3",
            "current_voice": self.voice_id,
            "rate": self.rate,
            "volume": self.volume,
            "available_voices": len(self._voices),
            "initialized": self._initialized
        }
    
    async def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
            del self.engine
            self.engine = None
        
        self._initialized = False
        logger.info("Text-to-speech cleanup complete")


# Example usage
if __name__ == "__main__":
    async def main():
        tts = TextToSpeech()
        
        try:
            await tts.initialize()
            
            # Test synthesis
            test_text = "Hello, this is a test of the text-to-speech system."
            output_file = "test_output.wav"
            
            await tts.synthesize(test_text, output_file)
            print(f"Audio saved to: {output_file}")
            
            # Get model info
            info = await tts.get_model_info()
            print(f"Model info: {info}")
            
            # Test available speakers
            speakers = await tts.get_available_speakers()
            if speakers:
                print(f"Available speakers: {speakers[:5]}")  # Show first 5
            
            # Test available languages
            languages = await tts.get_available_languages()
            if languages:
                print(f"Available languages: {languages}")
            
            # List models
            models = await TextToSpeech.list_available_models()
            print(f"Available models: {len(models)} models found")
            
        finally:
            await tts.cleanup()
    
    asyncio.run(main())