from typing import Dict, Any, List, Optional, BinaryIO
import os
import asyncio
import tempfile
from pathlib import Path
import aiohttp

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class SpeechToTextProcessor:
    """
    Processor for converting speech to text.
    
    This class provides methods for transcribing audio files in
    various formats, with special support for Vietnamese.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        service: str = "openai",  # Options: openai, google, local
        default_language: str = "vi"  # Default to Vietnamese
    ):
        """
        Initialize the speech-to-text processor.
        
        Args:
            api_key: API key for the STT service (defaults to settings)
            service: STT service to use
            default_language: Default language code
        """
        self.api_key = api_key or self._get_api_key(service)
        self.service = service
        self.default_language = default_language
        
        # Log configuration
        logger.info(f"Initialized Speech-to-Text processor using {service} service")
    
    def _get_api_key(self, service: str) -> str:
        """Get the appropriate API key from settings."""
        if service == "openai":
            return settings.OPENAI_API_KEY
        elif service == "google":
            return settings.GOOGLE_API_KEY
        else:
            return ""  # No API key needed for local service
    
    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        enhanced_model: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file to text.
        
        Args:
            file_path: Path to the audio file
            language: Language code (e.g., 'vi' for Vietnamese)
            prompt: Optional prompt to guide transcription
            enhanced_model: Whether to use an enhanced model
            
        Returns:
            Dictionary with transcription results
        """
        language = language or self.default_language
        
        if self.service == "openai":
            return await self._transcribe_with_openai(file_path, language, prompt, enhanced_model)
        elif self.service == "google":
            return await self._transcribe_with_google(file_path, language, prompt)
        else:
            return await self._transcribe_locally(file_path, language)
    
    async def _transcribe_with_openai(
        self,
        file_path: str,
        language: str,
        prompt: Optional[str] = None,
        enhanced_model: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI's Whisper API.
        
        Args:
            file_path: Path to the audio file
            language: Language code
            prompt: Optional prompt
            enhanced_model: Whether to use enhanced model
            
        Returns:
            Transcription results
        """
        try:
            model = "whisper-1"
            
            # Prepare form data
            form_data = aiohttp.FormData()
            with open(file_path, "rb") as f:
                form_data.add_field(
                    name="file",
                    value=f,
                    filename=os.path.basename(file_path),
                    content_type="audio/mpeg"  # Adjust based on file type
                )
            
            form_data.add_field(name="model", value=model)
            
            if language:
                form_data.add_field(name="language", value=language)
            
            if prompt:
                form_data.add_field(name="prompt", value=prompt)
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    data=form_data,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI transcription failed: {error_text}")
                        return {
                            "text": "",
                            "language": language,
                            "error": f"API error: {error_text}"
                        }
                    
                    result = await response.json()
                    
                    return {
                        "text": result.get("text", ""),
                        "language": language,
                        "confidence": 0.9,  # OpenAI doesn't provide confidence scores
                        "segments": []  # OpenAI doesn't provide segments by default
                    }
        except Exception as e:
            logger.error(f"OpenAI transcription error: {str(e)}")
            return {
                "text": "",
                "language": language,
                "error": f"Transcription failed: {str(e)}"
            }
    
    async def _transcribe_with_google(
        self,
        file_path: str,
        language: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio using Google's Speech-to-Text API.
        
        Args:
            file_path: Path to the audio file
            language: Language code
            prompt: Optional prompt
            
        Returns:
            Transcription results
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the Google Speech-to-Text API
        return {
            "text": "This is a placeholder for Google Speech-to-Text transcription.",
            "language": language,
            "confidence": 0.8,
            "segments": []
        }
    
    async def _transcribe_locally(
        self,
        file_path: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Transcribe audio using local models.
        
        Args:
            file_path: Path to the audio file
            language: Language code
            
        Returns:
            Transcription results
        """
        # This is a placeholder implementation
        # In a real implementation, you would use local STT libraries like Vosk
        return {
            "text": "This is a placeholder for local speech-to-text transcription.",
            "language": language,
            "confidence": 0.7,
            "segments": []
        }
    
    async def transcribe_bytes(
        self,
        audio_bytes: bytes,
        file_format: str = "mp3",
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio data as bytes
            file_format: Audio format (e.g., 'mp3', 'wav')
            language: Language code
            prompt: Optional prompt
            
        Returns:
            Transcription results
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_format}") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(audio_bytes)
        
        try:
            # Transcribe the temporary file
            return await self.transcribe_file(
                temp_file_path,
                language=language,
                prompt=prompt
            )
        finally:
            # Clean up temporary file
            os.remove(temp_file_path)
