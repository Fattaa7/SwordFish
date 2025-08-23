from chonkie import SlumberChunker
from text_extractor import extract_md_from_pdf
from chonkie import SemanticChunker

# Basic initialization with default parameters
chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-8M",  # Default model
    threshold=0.5,                               # Similarity threshold (0-1) or (1-100) or "auto"
    chunk_size=2048,                              # Maximum tokens per chunk
    min_sentences=1                              # Initial sentences per chunk
)
# Extract text from PDF
text = extract_md_from_pdf("fastApi.pdf")

# Chunk the text
chunks = chunker.chunk(text)

# Save chunks to file
with open("chunks_output.txt", "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks, start=1):
        f.write(f"--- Chunk {i} ---\n")
        f.write(chunk.text.strip() + "\n\n")
        f.write(f"(Tokens: {chunk.token_count}, Start: {chunk.start_index}, End: {chunk.end_index})\n\n")
