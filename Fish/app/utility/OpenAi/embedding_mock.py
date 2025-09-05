# app/utility/OpenAi/embedding_mock.py
from typing import List
import random

def get_chunk_embedding(chunk_text: str) -> List[float]:
    # Return a fake 1536-d vector
    return [random.random() for _ in range(1536)]

def batch_get_chunk_embeddings(chunk_texts: List[str]) -> List[List[float]]:
    return [[random.random() for _ in range(1536)] for _ in chunk_texts]
