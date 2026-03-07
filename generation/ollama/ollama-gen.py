
#!/usr/bin/env python3
"""Generate study notes from a recorded audio file using Ollama.

Usage:
    python generation/ollama/ollama-gen.py [audio_file]

If no audio file is given the script will look for "temp.wav" in the
project root. The audio is transcribed using the existing
`audio.recording.transcribe_audio` helper, then sent to Ollama via the
Python API (falling back to the CLI if the package isn't installed).
"""

import sys
import os
from pathlib import Path

# try to import transcription helper; if the package structure isn't
# on sys.path you may need to adjust relative imports
try:
    from audio import recording
except ImportError:
    # if running from project root make sure PYTHONPATH includes it
    sys.path.append(str(Path(__file__).parents[1]))
    from audio import recording

# determine source file
audio_path = sys.argv[1] if len(sys.argv) > 1 else "temp.wav"

if not os.path.exists(audio_path):
    print(f"Audio file {audio_path} does not exist")
    sys.exit(1)

print(f"Transcribing {audio_path}...")
transcription = recording.transcribe_audio(audio_path)
print("Transcript:\n", transcription)

prompt = (
    "You are an academic assistant. "
    "Based on the following transcript, produce concise study notes:\n" + transcription
)

model = None
# if a model file exists in project root, respect it
try:
    with open("model.txt","r") as mf:
        sel = mf.read().strip()
        provider_map = {"claude":"claude","chatgpt":"gpt-4o","grok":"grok-1.0","ollama":"llama2"}
        model = provider_map.get(sel, sel)
except FileNotFoundError:
    pass
# default if still none
model = model or "llama2"
# try python ollama API first
try:
    from ollama import chat
    print(f"Using ollama python API with model {model}")
    stream = chat(model=model, messages=[{"role":"user","content":prompt}], stream=True)
    # stream=True returns a generator of message chunks
    notes = ""
    for chunk in stream:
        if hasattr(chunk, 'message') and hasattr(chunk.message, 'content'):
            notes += chunk.message.content
        else:
            # handle error or unexpected response
            print(f"Unexpected response chunk: {chunk}")
            break
    print("\nGenerated notes:\n", notes)
except ImportError:
    # fallback to CLI
    model = model or "llama2"
    print("ollama python package not available; falling back to CLI")
    try:
        import subprocess
        res = subprocess.run(["ollama", "run", model, "--prompt", prompt], capture_output=True, text=True)
        notes = res.stdout.strip() or res.stderr.strip()
        print("\nGenerated notes:\n", notes)
    except FileNotFoundError:
        print("Ollama CLI not found; please install ollama or the python package")
    except Exception as e:
        print("Error running ollama CLI:", e)
except Exception as e:
    print("Error invoking ollama python API:", e)
