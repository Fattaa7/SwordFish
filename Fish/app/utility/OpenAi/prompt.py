from openai import OpenAI
from app.core.config import settings

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def ask_openai(query: str, context: list[str]) -> dict:
    context_with_ids = [f"chunk_id={i} | {c}" for i, c in enumerate(context)]
    system_messages = [{"role": "system", "content": c} for c in context_with_ids]
    system_messages.insert(0, {
        "role": "system",
        "content": (
            "You are a retrieval QA assistant. "
            "Answer ONLY using the provided chunks. "
            "you can use logical reasoning but do not make up facts. "
            "When you use information from a chunk, add an inline citation like [chunk_id]. chunk_id is the number after 'chunk_id=' in the chunk. "
            "At the end of the answer, provide a References section listing each citation in the format:\n"
            "- {title} (Page {page_number}) [chunk_id]\n"
            "DO NOT cite chunk_ids that were not used in the answer. "
            "DO not write chunk_id, just the number in brackets. "
            "After your answer, output JSON in the format:\n"
            "{\"used_chunk_ids\": [list of chunk_ids you used]}"
        )
    })

    messages = system_messages + [{"role": "user", "content": query}]
    with client.responses.stream(model="gpt-4.1", input=messages) as stream:
        final_response = stream.get_final_response()
        full_text = final_response.output[0].content[0].text

    import re, json
    match = re.search(r"\{.*\}", full_text, re.DOTALL)
    used_ids = []
    if match:
        try:
            used_ids = json.loads(match.group(0)).get("used_chunk_ids", [])
        except json.JSONDecodeError:
            pass

    answer_text = full_text[:match.start()].strip() if match else full_text
    return {"answer": answer_text, "used_chunk_ids": used_ids}


def ask_openai_simple(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content