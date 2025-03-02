from typing import Dict, Any, List, Optional, BinaryIO, Union
import os
import asyncio
import tempfile
from pathlib import Path
import aiohttp
import io

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class TextToSpeechProcessor:
    """
    Processor for converting text to speech.
    
    This class provides methods for synthesizing speech from text,
    with special support for Vietnamese.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        service: str = "openai",  # Options: openai, elevenlabs, google, local
        default_language: str = "vi",  # Default to Vietnamese
        default_voice: Optional[str] = None
    ):
        """
        Initialize the text-to-speech processor.
        
        Args:
            api_key: API key for the TTS service (defaults to settings)
            service: TTS service to use
            default_language: Default language code
            default_voice: Default voice ID
        """
        self.api_key = api_key or self._get_api_key(service)
        self.service = service
        self.default_language = default_language
        self.default_voice = default_voice or self._get_default_voice(service, default_language)
        
        # Log configuration
        logger.info(f"Initialized Text-to-Speech processor using {service} service")
    
    def _get_api_key(self, service: str) -> Optional[str]:
        """Get the appropriate API key for the selected service."""
        if service == "openai":
            return settings.OPENAI_API_KEY
        elif service == "elevenlabs":
            return settings.ELEVENLABS_API_KEY
        elif service == "google":
            return settings.GOOGLE_API_KEY
        return None
    
    def _get_default_voice(self, service: str, language: str) -> str:
        """Get the default voice for the selected service and language."""
        # Vietnamese voices for different services
        if language == "vi":
            if service == "openai":
                return "nova"  # OpenAI TTS voice that works for Vietnamese
            elif service == "elevenlabs":
                return "vi-VN-Standard-A"  # ElevenLabs Vietnamese voice
            elif service == "google":
                return "vi-VN-Standard-A"  # Google TTS Vietnamese voice
        
        # Default English voices
        if service == "openai":
            return "alloy"
        elif service == "elevenlabs":
            return "Adam"
        elif service == "google":
            return "en-US-Standard-D"
        
        return "default"
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
        output_format: str = "mp3",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech using the configured service.
        
        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use
            language: Language code
            output_format: Output audio format
            speed: Speech speed (1.0 = normal)
            
        Returns:
            Dictionary with audio data and metadata
        """
        # Set defaults
        voice_id = voice_id or self.default_voice
        language = language or self.default_language
        
        # Select the appropriate service
        if self.service == "openai":
            return await self._synthesize_with_openai(text, voice_id, output_format, speed)
        elif self.service == "elevenlabs":
            return await self._synthesize_with_elevenlabs(text, voice_id, output_format, speed)
        elif self.service == "google":
            return await self._synthesize_with_google(text, voice_id, language, output_format, speed)
        else:
            return await self._synthesize_with_local(text, voice_id, language, output_format, speed)
    
    async def _synthesize_with_openai(
        self,
        text: str,
        voice_id: str,
        output_format: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using OpenAI's TTS API."""
        try:
            import openai
            client = openai.AsyncClient(api_key=self.api_key)
            
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice_id,
                input=text,
                response_format=output_format,
                speed=speed
            )
            
            # Get audio data
            audio_data = await response.read()
            
            return {
                "audio_data": audio_data,
                "format": output_format,
                "voice_id": voice_id
            }
        except Exception as e:
            logger.error(f"OpenAI TTS synthesis failed: {str(e)}")
            return {"error": f"OpenAI TTS synthesis failed: {str(e)}"}
    
    async def _synthesize_with_elevenlabs(
        self,
        text: str,
        voice_id: str,
        output_format: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using ElevenLabs TTS API."""
        try:
            # Construct API URL
            api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            # Prepare headers and payload
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": f"audio/{output_format}"
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "speaking_rate": speed
                }
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"ElevenLabs TTS failed with status {response.status}: {error_text}")
                        return {"error": f"ElevenLabs TTS failed: {error_text}"}
                    
                    # Read audio data
                    audio_data = await response.read()
                    
                    return {
                        "audio_data": audio_data,
                        "format": output_format,
                        "voice_id": voice_id
                    }
        except Exception as e:
            logger.error(f"ElevenLabs TTS synthesis failed: {str(e)}")
            return {"error": f"ElevenLabs TTS synthesis failed: {str(e)}"}
    
    async def _synthesize_with_google(
        self,
        text: str,
        voice_id: str,
        language: str,
        output_format: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using Google Cloud TTS API."""
        try:
            from google.cloud import texttospeech
            
            # Initialize client
            client = texttospeech.TextToSpeechClient()
            
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build the voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice_id
            )
            
            # Select the audio file type
            if output_format == "mp3":
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speed
                )
            else:
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    speaking_rate=speed
                )
            
            # Perform the synthesis request
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return {
                "audio_data": response.audio_content,
                "format": output_format,
                "voice_id": voice_id
            }
        except Exception as e:
            logger.error(f"Google TTS synthesis failed: {str(e)}")
            return {"error": f"Google TTS synthesis failed: {str(e)}"}
    
    async def _synthesize_with_local(
        self,
        text: str,
        voice_id: str,
        language: str,
        output_format: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using local TTS engine (pyttsx3 or similar)."""
        # This is a placeholder implementation
        # In a real application, this would use a local TTS engine
        logger.warning("Local TTS is not fully implemented, returning dummy audio")
        
        # Return a dummy audio file
        dummy_audio = b"Dummy audio data"
        
        return {
            "audio_data": dummy_audio,
            "format": output_format,
            "voice_id": voice_id
        }
    
    async def save_to_file(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech and save to a file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice_id: Voice ID to use
            language: Language code
            speed: Speech speed
            
        Returns:
            Dictionary with result information
        """
        # Determine output format from file extension
        output_format = os.path.splitext(output_path)[1].lstrip(".")
        if not output_format:
            output_format = "mp3"  # Default
            output_path += f".{output_format}"
        
        # Synthesize speech
        result = await self.synthesize_speech(
            text=text,
            voice_id=voice_id,
            language=language,
            output_format=output_format,
            speed=speed
        )
        
        # Check for errors
        if "error" in result or not result.get("audio_data"):
            return {
                "success": False,
                "error": result.get("error", "Failed to synthesize speech"),
                "file_path": None
            }
        
        # Save audio data to file
        try:
            with open(output_path, "wb") as f:
                f.write(result["audio_data"])
            
            return {
                "success": True,
                "file_path": output_path,
                "format": output_format,
                "voice_id": result.get("voice_id"),
                "duration": None  # Would need audio processing to determine
            }
        except Exception as e:
            logger.error(f"Failed to save audio file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to save audio file: {str(e)}",
                "file_path": None
            }
