# tests/mocks/mock_openai.py
def mock_ask_openai(query: str, context: list[str]) -> str:
    # You can make it dynamic based on query if needed
    return f"[MOCK RESPONSE] Answer to: {query}"
