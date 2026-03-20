"""
EffOCR-Word (Small) Integration for Local Offline OCR
No internet connection required - runs completely offline
"""

from typing import Dict, Any, List, Optional, Union
import os
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import transformers for EffOCR-Word
try:
    from transformers import AutoProcessor, AutoModelForVision2Seq
    import torch
    EFFOCR_AVAILABLE = True
except ImportError:
    EFFOCR_AVAILABLE = False

# Try to import easyocr as alternative
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class EffOCRProcessor:
    """
    Local offline OCR using EffOCR-Word (Small) model
    """

    def __init__(self, model_name: str = "microsoft/trocr-small-printed"):
        """
        Initialize EffOCR processor

        Args:
            model_name: Hugging Face model name for OCR
                       Default: TrOCR small (similar to EffOCR-Word)
        """
        self.model = None
        self.processor = None
        self.model_name = model_name
        # Only check CUDA if torch is available
        if EFFOCR_AVAILABLE:
            import torch as torch_module
            self.device = "cuda" if torch_module.cuda.is_available() else "cpu"
        else:
            self.device = "cpu"

    def load_model(self) -> bool:
        """Load the OCR model"""
        try:
            if not EFFOCR_AVAILABLE:
                return False

            print(f"Loading OCR model: {self.model_name} on {self.device}...")
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForVision2Seq.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()

            print("✓ OCR model loaded successfully")
            return True

        except Exception as e:
            print(f"✗ Failed to load OCR model: {e}")
            return False

    def ocr_image(self, image_path: str) -> str:
        """
        Perform OCR on a single image

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        if self.model is None:
            if not self.load_model():
                return ""

        try:
            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")

            # Process image
            pixel_values = self.processor(image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(self.device)

            # Generate text
            with torch.no_grad():
                generated_ids = self.model.generate(pixel_values)

            # Decode
            text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return text

        except Exception as e:
            print(f"OCR error: {e}")
            return ""


class EasyOCRProcessor:
    """
    Alternative local OCR using EasyOCR (more robust)
    """

    def __init__(self, languages: List[str] = ['en']):
        """
        Initialize EasyOCR processor

        Args:
            languages: List of language codes (e.g., ['en', 'fr'])
        """
        self.reader = None
        self.languages = languages

    def load_model(self) -> bool:
        """Load the OCR model"""
        try:
            if not EASYOCR_AVAILABLE:
                return False

            print(f"Loading EasyOCR with languages: {self.languages}...")
            # Check for GPU availability
            try:
                import torch as torch_module
                use_gpu = torch_module.cuda.is_available()
            except:
                use_gpu = False

            self.reader = easyocr.Reader(self.languages, gpu=use_gpu)
            print("✓ EasyOCR loaded successfully")
            return True

        except Exception as e:
            print(f"✗ Failed to load EasyOCR: {e}")
            return False

    def ocr_image(self, image_path: str, detail: int = 0) -> str:
        """
        Perform OCR on image

        Args:
            image_path: Path to image
            detail: 0=text only, 1=text with confidence

        Returns:
            Extracted text
        """
        if self.reader is None:
            if not self.load_model():
                return ""

        try:
            # Perform OCR
            results = self.reader.readtext(image_path, detail=detail)

            # Extract text
            if detail == 0:
                text = ' '.join(results)
            else:
                # results is list of (bbox, text, confidence)
                text = ' '.join([result[1] for result in results])

            return text

        except Exception as e:
            print(f"OCR error: {e}")
            return ""


def ocr_image_local(
    image_path: str,
    engine: str = "easyocr",
    languages: List[str] = ['en']
) -> Dict[str, Any]:
    """
    Perform OCR on image using local offline models

    Args:
        image_path: Path to image file
        engine: OCR engine - 'easyocr' (recommended) or 'effocr'
        languages: List of language codes

    Returns:
        OCR result with extracted text
    """
    if not PIL_AVAILABLE:
        return {
            "success": False,
            "error": "PIL (Pillow) not available"
        }

    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"Image not found: {image_path}"
        }

    try:
        if engine == "easyocr":
            if not EASYOCR_AVAILABLE:
                return {
                    "success": False,
                    "error": "EasyOCR not available - install with: pip install easyocr",
                    "note": "EasyOCR is recommended for offline OCR"
                }

            processor = EasyOCRProcessor(languages=languages)
            text = processor.ocr_image(image_path)

            return {
                "success": True,
                "text": text,
                "engine": "easyocr",
                "languages": languages,
                "message": "OCR completed using EasyOCR"
            }

        elif engine == "effocr":
            if not EFFOCR_AVAILABLE:
                return {
                    "success": False,
                    "error": "EffOCR (transformers) not available - install with: pip install transformers torch",
                    "note": "You can use 'easyocr' engine as an alternative"
                }

            processor = EffOCRProcessor()
            text = processor.ocr_image(image_path)

            return {
                "success": True,
                "text": text,
                "engine": "effocr",
                "message": "OCR completed using EffOCR"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown OCR engine: {engine}",
                "available_engines": ["easyocr", "effocr"]
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"OCR failed: {str(e)}"
        }


def ocr_pdf_local(
    pdf_path: str,
    output_format: str = "text",
    engine: str = "easyocr",
    languages: List[str] = ['en']
) -> Dict[str, Any]:
    """
    Perform OCR on PDF using local offline models

    Args:
        pdf_path: Path to PDF file
        output_format: 'text' or 'json'
        engine: OCR engine to use
        languages: Languages for OCR

    Returns:
        OCR results
    """
    try:
        import pdfplumber
        from pdf2image import convert_from_path
    except ImportError as e:
        return {
            "success": False,
            "error": f"Required libraries not available: {str(e)}",
            "note": "Install with: pip install pdfplumber pdf2image"
        }

    try:
        # Convert PDF pages to images
        print(f"Converting PDF to images: {pdf_path}")
        images = convert_from_path(pdf_path)

        results = {}
        processor = EasyOCRProcessor(languages=languages) if engine == "easyocr" else EffOCRProcessor()

        # Process each page
        for i, image in enumerate(images):
            print(f"Processing page {i + 1}/{len(images)}...")

            # Save temporary image
            temp_path = f"temp_page_{i}.png"
            image.save(temp_path, 'PNG')

            # Perform OCR
            text = processor.ocr_image(temp_path)
            results[f"page_{i + 1}"] = text

            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return {
            "success": True,
            "pages": results,
            "total_pages": len(results),
            "engine": engine,
            "languages": languages,
            "message": f"OCR completed for {len(results)} pages"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"PDF OCR failed: {str(e)}"
        }


def get_ocr_info() -> Dict[str, Any]:
    """
    Get information about available OCR engines

    Returns:
        Available OCR engines and their status
    """
    return {
        "available_engines": {
            "easyocr": {
                "available": EASYOCR_AVAILABLE,
                "description": "Robust offline OCR supporting 80+ languages",
                "install": "pip install easyocr",
                "recommended": True,
                "features": ["Multi-language", "High accuracy", "GPU support"]
            },
            "effocr": {
                "available": EFFOCR_AVAILABLE,
                "description": "Transformer-based OCR (TrOCR)",
                "install": "pip install transformers torch",
                "recommended": False,
                "features": ["Transformer-based", "Modern architecture"]
            }
        },
        "dependencies": {
            "PIL": PIL_AVAILABLE,
            "transformers": EFFOCR_AVAILABLE,
            "easyocr": EASYOCR_AVAILABLE
        }
    }
