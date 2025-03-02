from typing import Dict, Any, List, Optional, Union, Tuple
import os
import tempfile
from pathlib import Path
import asyncio
import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class OCRProcessor:
    """
    Processor for optical character recognition (OCR).
    
    This class provides methods for extracting text from images
    with special support for Vietnamese text.
    """
    
    def __init__(
        self, 
        use_gpu: bool = False,
        tesseract_path: Optional[str] = None,
        supported_languages: List[str] = ["en", "vi"]
    ):
        """
        Initialize the OCR processor.
        
        Args:
            use_gpu: Whether to use GPU acceleration
            tesseract_path: Path to tesseract executable
            supported_languages: List of supported language codes
        """
        self.use_gpu = use_gpu and settings.USE_GPU
        self.supported_languages = supported_languages
        
        # Configure tesseract
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Initialize EasyOCR reader
        self.reader = None  # Lazy initialization
        
        logger.info(f"Initialized OCR processor (GPU: {self.use_gpu})")
    
    def _get_easyocr_reader(self, languages: List[str]) -> Any:
        """Get or initialize EasyOCR reader."""
        if self.reader is None:
            logger.info(f"Initializing EasyOCR reader for languages: {languages}")
            import easyocr
            self.reader = easyocr.Reader(
                languages,
                gpu=self.use_gpu,
                quantize=not self.use_gpu  # Optimize for CPU if not using GPU
            )
        return self.reader
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Processed image as numpy array
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return opening
    
    def _detect_language(self, text: str) -> str:
        """
        Detect language of the extracted text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'vi')
        """
        # This is a simplified implementation
        # In a real application, use a language detection library
        
        # Check for Vietnamese-specific characters
        vietnamese_chars = set("ăâậđêơưôừểỉạáàảãạẹéèẻẽẹíìỉĩịọóòỏõọụúùủũụ")
        text_chars = set(text.lower())
        
        if any(char in vietnamese_chars for char in text_chars):
            return "vi"
        
        # Default to English
        return "en"
    
    async def process_image(
        self,
        image_path: str,
        use_enhanced_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Process an image to extract text.
        
        Args:
            image_path: Path to the image file
            use_enhanced_mode: Whether to use multiple OCR engines for better results
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}"}
            
            # Basic mode: just use Tesseract
            if not use_enhanced_mode:
                text = pytesseract.image_to_string(Image.open(image_path))
                language = self._detect_language(text)
                
                return {
                    "text": text,
                    "language": language,
                    "engine": "tesseract"
                }
            
            # Enhanced mode: combine multiple engines
            # 1. First, try EasyOCR which handles Vietnamese well
            reader = self._get_easyocr_reader(["en", "vi"])
            result = reader.readtext(image_path)
            
            text_blocks = []
            bounding_boxes = []
            
            for box, text, conf in result:
                text_blocks.append(text)
                bounding_boxes.append({
                    "text": text,
                    "confidence": float(conf),
                    "bbox": box
                })
            
            easyocr_text = "\n".join(text_blocks)
            
            # 2. As a backup, also use Tesseract
            preprocessed_image = self._preprocess_image(image_path)
            tesseract_text = pytesseract.image_to_string(
                Image.fromarray(preprocessed_image),
                lang="eng+vie"
            )
            
            # Choose the better result or combine them
            final_text = easyocr_text if len(easyocr_text) > len(tesseract_text) else tesseract_text
            
            # Detect language
            language = self._detect_language(final_text)
            
            return {
                "text": final_text,
                "language": language,
                "bounding_boxes": bounding_boxes,
                "engines": ["easyocr", "tesseract"]
            }
            
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return {"error": f"OCR processing failed: {str(e)}"}
