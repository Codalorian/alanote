import tkinter as tk
from ui import ui
import os
import subprocess

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


def get_ollama_models() -> list:
    """Return list of installed Ollama models."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            models = [line.split()[0] for line in lines[1:] if line.strip()]
            return models
        return []
    except Exception as e:
        print("Error getting ollama models:", e)
        return []


def main():
    root = tk.Tk()
    root.title("Alanote")
    root.geometry("400x300")
    
    label = tk.Label(root, text="Welcome to Alanote!")
    label.pack(pady=20)

    # dropdown for model selection
    options = ["claude", "chatgpt", "grok", "ollama"]
    selected = tk.StringVar()
    selected_ollama = tk.StringVar()
    
    # Load the saved model
    full_model = load_model_choice()
    if full_model in options:
        selected.set(full_model)
    else:
        selected.set('ollama')
        selected_ollama.set(full_model)
    
    def on_model_change(choice):
        if choice == 'ollama':
            models = get_ollama_models()
            if models:
                if not selected_ollama.get() or selected_ollama.get() not in models:
                    selected_ollama.set(models[0])
                ollama_dropdown['menu'].delete(0, 'end')
                for model in models:
                    ollama_dropdown['menu'].add_command(label=model, command=tk._setit(selected_ollama, model))
                ollama_dropdown.pack(pady=10)
                current_model_label.config(text=f"Selected model: {selected_ollama.get()}")
                current_model_label.pack(pady=5)
            else:
                ollama_dropdown.pack_forget()
                current_model_label.pack_forget()
        else:
            selected_ollama.set('')
            ollama_dropdown.pack_forget()
            current_model_label.pack_forget()
        save_model_choice(choice if choice != 'ollama' else selected_ollama.get())
    
    def on_ollama_model_change(model):
        save_model_choice(model)
        current_model_label.config(text=f"Selected model: {model}")
    
    dropdown = tk.OptionMenu(root, selected, *options, command=on_model_change)
    dropdown.pack(pady=10)
    
    ollama_dropdown = tk.OptionMenu(root, selected_ollama, "", command=on_ollama_model_change)
    ollama_dropdown.pack_forget()  # hide initially
    
    current_model_label = tk.Label(root, text="")
    current_model_label.pack_forget()
    
    # Trigger initial setup
    on_model_change(selected.get())

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

