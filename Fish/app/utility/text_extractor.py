from pathlib import Path
import pymupdf4llm
import pymupdf
import fitz  # PyMuPDF


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
    

def convert_file_to_markdown(source_path: str, destination_path: str = None) -> str:
    """
    Convert a file to Markdown format using pymupdf4llm
    """
    doc = fitz.open(source_path)
    md_pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        md_pages.append(f"{text}\n\n--- Page {page_num} ---")
    md_text = "\n\n".join(md_pages)
    
    if destination_path:
        Path(destination_path).write_text(md_text, encoding="utf-8")
    return md_text


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
