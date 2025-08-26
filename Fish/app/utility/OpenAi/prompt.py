from openai import OpenAI
import os

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(query: str, context: list[str]) -> str:
    """
    Sends a query to OpenAI with a given context.

    Args:
        query (str): The user query.
        context (list[str]): A list of context strings that will be set as system messages.

    Returns:
        str: The LLM's reply as plain text.
    """
    # Build system messages from context
    system_messages = [{"role": "system", "content": c} for c in context]
    system_messages.insert(0, {
        "role": "system",
        "content": "Only use the context as reference and don't get any data from outside of it, though you can use logic to explain it using the info shared with you. provide citations for everything you use."
    })

    # Add user query
    messages = system_messages + [{"role": "user", "content": query}]
    print("Messages sent to OpenAI:", messages)

       # Stream response
    with client.responses.stream(
        model="gpt-4.1",
        input=messages,
    ) as stream:
        print("\nAssistant:\n")
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.error":
                print("\n[Error]", event.error)

        print("\n\n--- Completed ---\n")

        # Get structured entities
        final_response = stream.get_final_response()
        entities = final_response.output[0].content[0].parsed
        return entities
