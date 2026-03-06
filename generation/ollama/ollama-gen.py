#name to ollama-gen.py to avoid circular input
from ollama import chat

stream = chat(
    model='falcon3:3b', #change so user can pick the model
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)

