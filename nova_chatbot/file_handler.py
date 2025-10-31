import os
import fitz  # PyMuPDF
from .object_recognition import object_recognizer

def handle_file_upload(filepath):
    if not os.path.exists(filepath):
        return f"❌ File not found at '{filepath}'."

    _, extension = os.path.splitext(filepath)
    extension = extension.lower()

    if extension in ['.jpg', '.jpeg', '.png', '.bmp']:
        return handle_image_file(filepath)
    elif extension == '.txt':
        return handle_text_file(filepath)
    elif extension == '.pdf':
        return handle_pdf_file(filepath)
    else:
        return f"Unsupported file type: {extension}"

def handle_image_file(filepath):
    results = object_recognizer.recognize_objects(image_path=filepath)
    return "\n".join(results)

def handle_text_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading text file: {e}"

def handle_pdf_file(filepath):
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"❌ Error reading PDF file: {e}"
