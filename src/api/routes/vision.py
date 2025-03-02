from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel
from pathlib import Path
import os
import shutil
import tempfile
import uuid

from src.vision.ocr import OCRProcessor
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Create a temp directory for uploaded files if it doesn't exist
UPLOAD_DIR = Path("./uploads/temp")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class OCRRequest(BaseModel):
    """Request model for OCR processing with existing file path."""
    image_path: str
    use_enhanced_mode: Optional[bool] = True

class OCRResponse(BaseModel):
    """Response model for OCR processing."""
    text: str
    language: str
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

@router.post("/ocr/upload", response_model=OCRResponse)
async def ocr_upload(
    file: UploadFile = File(...),
    use_enhanced_mode: bool = Form(True)
):
    """
    Upload an image and perform OCR on it.
    
    Parameters:
    - file: The image file to process
    - use_enhanced_mode: Whether to use enhanced OCR mode with multiple engines
    
    Returns:
    - Extracted text and metadata
    """
    # Save the uploaded file to a temporary location
    temp_file_path = UPLOAD_DIR / f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image with OCR
        ocr_processor = OCRProcessor(use_gpu=False)  # Set to True if GPU is available
        result = await ocr_processor.process_image(
            image_path=str(temp_file_path),
            use_enhanced_mode=use_enhanced_mode
        )
        
        # Check for errors
        if "error" in result:
            return OCRResponse(text="", language="", error=result["error"])
        
        return OCRResponse(
            text=result["text"],
            language=result["language"],
            bounding_boxes=result.get("bounding_boxes", [])
        )
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        return OCRResponse(
            text="",
            language="",
            error=f"OCR processing failed: {str(e)}"
        )
    finally:
        # Clean up the temporary file
        if temp_file_path.exists():
            os.remove(temp_file_path)

@router.post("/ocr/process", response_model=OCRResponse)
async def ocr_process(request: OCRRequest):
    """
    Process an existing image file with OCR.
    
    Parameters:
    - request: OCR request with image path and options
    
    Returns:
    - Extracted text and metadata
    """
    try:
        # Process the image with OCR
        ocr_processor = OCRProcessor(use_gpu=False)  # Set to True if GPU is available
        result = await ocr_processor.process_image(
            image_path=request.image_path,
            use_enhanced_mode=request.use_enhanced_mode
        )
        
        # Check for errors
        if "error" in result:
            return OCRResponse(text="", language="", error=result["error"])
        
        return OCRResponse(
            text=result["text"],
            language=result["language"],
            bounding_boxes=result.get("bounding_boxes", [])
        )
    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        return OCRResponse(
            text="",
            language="",
            error=f"OCR processing failed: {str(e)}"
        ) 