from pathlib import Path
import pymupdf4llm


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF
    """
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def convert_file_to_markdown(source_path: str, destination_path: str = []) -> str:
    """
    Convert a file to Markdown format using pymupdf4llm
    """
    try:
        md_text = pymupdf4llm.to_markdown(source_path)
        if destination_path:
            Path(destination_path).write_bytes(md_text.encode())
        return md_text
    except Exception as e:
        print(f"Error converting PDF to Markdown: {e}")
        return ""
