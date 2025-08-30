import cohere


co = cohere.ClientV2(
    "vALKOZKXHDxhAmkK8HUqogQIu4Z17CibDiVhnHMq"
)  # Get your free API key here: https://dashboard.cohere.com/api-keys


def rerank(query, documents):
    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=documents,
        top_n=len(documents),
    )
    return response