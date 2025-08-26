from chonkie import SemanticChunker

# Initialize chunker
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-8M",
    threshold=0.5,       # Similarity threshold
    chunk_size=2048,     # Max tokens per chunk
    min_sentences=1
)


def chunk_file(file_path: str):
    """Read a .md file and return semantic chunks."""
    if not file_path.endswith('.md'):
        raise ValueError(f"Invalid file type: {file_path}. Expected a .md file.")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

    if not text.strip():
        print(f"No text found in {file_path}")
        return []

    # Chunk the text
    chunks = chunker.chunk(text)
    print(f"Chunked into {len(chunks)} chunks.")

    return chunks


def chunk_markdown_text(md_text: str):
    """Chunk markdown text into semantic chunks."""
    if not md_text.strip():
        print("No text provided for chunking.")
        return []

    # Chunk the text
    chunks = chunker.chunk(md_text)

    return chunks