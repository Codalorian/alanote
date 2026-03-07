
import tkinter as tk
from ui import ui
import os

def save_model_choice(choice: str):
    """Write the selected model name to model.txt."""
    try:
        with open("model.txt", "w") as f:
            f.write(choice)
    except OSError as e:
        print("Failed to save model selection:", e)


def load_model_choice() -> str:
    """Return previously saved model or default to 'claude'."""
    try:
        with open("model.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "claude"


def main():
    root = tk.Tk()
    root.title("Alanote")
    root.geometry("400x300")
    
    label = tk.Label(root, text="Welcome to Alanote!")
    label.pack(pady=20)

    # dropdown for model selection
    options = ["claude", "chatgpt", "grok", "ollama"]
    selected = tk.StringVar(value=load_model_choice())
    dropdown = tk.OptionMenu(root, selected, *options,
                              command=lambda v: save_model_choice(v))
    dropdown.pack(pady=10)

    # Create the record audio window in the same event loop
    ui.record_audio(root)
    
    # generate notes button
    def on_generate():
        # ensure recording module available
        from audio import recording as rec
        if not os.path.exists("temp.wav"):
            print("No recording available to transcribe")
            return
        transcription = rec.transcribe_audio("temp.wav")
        print("Transcription:\n", transcription)
        # map dropdown choice to real Ollama model identifiers
        provider_map = {
            "claude": "claude",
            "chatgpt": "gpt-4o",
            "grok": "grok-1.0",
            "ollama": "llama2",
        }
        sel = load_model_choice()
        model = provider_map.get(sel, sel)
        # build prompt for notes
        prompt = (
            "You are an academic assistant. "
            "Based on the following transcript, produce concise study notes:\n" + transcription
        )
        # try using Python ollama package first
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
            print("Generated notes:\n", notes)
        except ImportError:
            # fallback to CLI
            try:
                import subprocess
                result = subprocess.run([
                    "ollama", "run", model, "--prompt", prompt
                ], capture_output=True, text=True)
                notes = result.stdout.strip() or result.stderr.strip()
                print("Generated notes:\n", notes)
            except FileNotFoundError:
                print("ollama not installed; please install the CLI or python package")
            except Exception as e:
                print("Error running ollama CLI:", e)
        except Exception as e:
            print("Error invoking ollama python API:", e)

    gen_button = tk.Button(root, text="Generate Notes", command=on_generate)
    gen_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
