from openai import OpenAI
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
