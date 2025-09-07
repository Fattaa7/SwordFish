from pathlib import Path
import re
import pymupdf4llm
import pymupdf
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF
    """
    try:
        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
    

def clean_text(text: str) -> str:
    """
    Remove all non-printable characters including null bytes (0x00), 
    while preserving newlines and tabs.
    """
    if not text:
        return ""
        
    # First remove null bytes
    text = text.replace('\x00', '')
    
    # Then remove other non-printable characters except newline and tab
    cleaned = []
    for c in text:
        if c == '\n' or c == '\t':
            cleaned.append(c)
        elif c.isprintable():
            cleaned.append(c)
    
    return ''.join(cleaned)

def convert_file_to_markdown(source_path: str, destination_path: str = None, min_text_length: int = 50, max_workers: int = 4) -> str:
    """
    Convert a PDF file to Markdown format with optional threaded OCR.
    """
    def ocr_page(page_num, page):
        """Perform OCR on a single page."""
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        return page_num, clean_text(text)

    try:
        doc = fitz.open(source_path)
        md_pages = [None] * len(doc)  # Preallocate list

        ocr_tasks = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for page_num, page in enumerate(doc, start=1):
                try:
                    # Try direct text extraction first
                    text = page.get_text("text") or ""
                    text = clean_text(text)
                    
                    if len(text) < min_text_length:
                        # Submit OCR for pages with insufficient text
                        ocr_tasks[executor.submit(ocr_page, page_num, page)] = page_num
                    else:
                        md_pages[page_num - 1] = f"{text}\n\n--- Page {page_num} ---"
                except Exception as page_error:
                    print(f"Error processing page {page_num}: {page_error}")
                    continue

            # Collect OCR results
            for future in as_completed(ocr_tasks):
                page_num, text = future.result()
                if text.strip():
                    md_pages[page_num - 1] = f"{text}\n\n--- Page {page_num} ---"

        # Filter out empty pages
        md_pages = [p for p in md_pages if p]
        if not md_pages:
            raise ValueError("No valid content could be extracted from the document")

        md_text = clean_text("\n\n".join(md_pages))
        if not md_text.strip():
            raise ValueError("Extracted text is empty after cleaning")

        if destination_path:
            Path(destination_path).write_text(md_text, encoding="utf-8")

        print(f"Conversion complete: {len(md_text)} characters extracted")
        return md_text

    except Exception as e:
        raise ValueError(f"Failed to convert file to markdown: {e}") from e


def extract_md_from_pdf(file_path: str) -> str:
    """
    Extract Markdown text from a PDF file using pymupdf4llm
    """
    try:
        md_text = pymupdf4llm.to_markdown(file_path)
        return md_text
    except Exception as e:
        print(f"Error extracting Markdown from PDF: {e}")
        return ""
    


def split_markdown_into_pages(file_path: str) -> list[str]:
    text = Path(file_path).read_text(encoding="utf-8")
    # Assume page markers like "--- Page N ---" exist
    pages = text.split("\n--- Page ")
    # Clean up and return
    return [p.strip() for p in pages if p.strip()]



