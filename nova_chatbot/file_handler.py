"""
File handling for various file types.
"""

import os
from PIL import Image
import fitz  # PyMuPDF
from .object_recognition import object_recognizer


def handle_file_upload(filepath):
    """
    Handle file upload and processing.
    
    Args:
        filepath: Path to the file to process
        
    Returns:
        String result of file processing
    """
    if not os.path.exists(filepath):
        return f"[ERROR] File not found at '{filepath}'."

    _, extension = os.path.splitext(filepath)
    extension = extension.lower()

    if extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
        return handle_image_file(filepath)
    elif extension == '.txt':
        return handle_text_file(filepath)
    elif extension == '.pdf':
        return handle_pdf_file(filepath)
    else:
        return f"[WARN] Unsupported file type: {extension}\nSupported types: .jpg, .png, .bmp, .gif, .txt, .pdf"


def handle_image_file(filepath):
    """Process an image file with object recognition."""
    try:
        # First verify the image can be opened
        img = Image.open(filepath)
        img.verify()
        
        # Now run object recognition
        results = object_recognizer.recognize_objects(image_path=filepath)
        return "\n".join(results)
    except Exception as e:
        return f"[ERROR] Error processing image: {str(e)}"


def handle_text_file(filepath):
    """Read and return contents of a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Limit output length
            if len(content) > 5000:
                return content[:5000] + "\n\n... (truncated)"
            return content
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"[ERROR] Error reading text file: {e}"
    except Exception as e:
        return f"[ERROR] Error reading text file: {e}"


def handle_pdf_file(filepath):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page_num, page in enumerate(doc):
            text += page.get_text()
            
        if not text.strip():
            return "[WARN] No text found in PDF. It may be image-based (scanned)."
        
        # Limit output length
        if len(text) > 5000:
            return text[:5000] + "\n\n... (truncated)"
        return text
        
    except Exception as e:
        return f"[ERROR] Error reading PDF file: {e}"
