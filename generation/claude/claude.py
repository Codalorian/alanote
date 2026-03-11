import anthropic

client = anthropic.Anthropic(
    api_key="YOUR_ANTHROPIC_API_KEY"
)

response = client.messages.create(
    model="claude-3-5-sonnet-latest",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Explain black holes in one sentence."}
    ]
)

print(response.content[0].text)
