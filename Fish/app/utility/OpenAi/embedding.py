from openai import OpenAI
from app.core.config import settings
from typing import List

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_chunk_embedding(chunk_text: str) -> list[float]:
    """
    Generates an embedding vector for a given text chunk.

    Args:
        chunk_text (str): The text chunk to embed.

    Returns:
        list[float]: The embedding vector as a list of floats.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",  # or "text-embedding-3-large"
        input=chunk_text
    )
    return response.data[0].embedding


def batch_get_chunk_embeddings(chunk_texts: List[str]) -> List[List[float]]:
    """
    Generates embedding vectors for a list of text chunks in one API call.

    Args:
        chunk_texts (List[str]): List of text chunks to embed.

    Returns:
        List[List[float]]: List of embedding vectors.
    """
    if not chunk_texts:
        return []

    response = client.embeddings.create(
        model="text-embedding-3-small",  # or "text-embedding-3-large"
        input=chunk_texts  # batch input
    )

    # Each response.data[i] corresponds to chunk_texts[i]
    embeddings = [item.embedding for item in response.data]
    return embeddings
