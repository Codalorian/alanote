import tkinter as tk
from ui import ui
import os
import subprocess
import easygui


def save_model_choice(choice: str):
    try:
        with open("model.txt", "w") as f:
            f.write(choice)
    except OSError as e:
        print("Failed to save model selection:", e)


def load_model_choice() -> str:
    try:
        with open("model.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "claude"


def get_ollama_models() -> list:
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            return [line.split()[0] for line in lines[1:] if line.strip()]
        return []
    except Exception as e:
        print("Error getting ollama models:", e)
        return []


def ensure_key(file_name, prompt_title):
    """Prompt user only if key file does not exist."""
    if not os.path.exists(file_name):
        key = easygui.enterbox(f"Enter your {prompt_title} API key:", prompt_title)
        if key:
            with open(file_name, "w") as f:
                f.write(key)
        else:
            print(f"No {prompt_title} API key entered.")


def main():
    root = tk.Tk()
    root.title("Alanote")
    root.geometry("400x300")

    tk.Label(root, text="Welcome to Alanote!").pack(pady=20)

    options = ["claude", "chatgpt", "grok", "ollama"]

    selected = tk.StringVar()
    selected_ollama = tk.StringVar()

    # Load saved model
    full_model = load_model_choice()

    if full_model in options:
        selected.set(full_model)
    else:
        selected.set("ollama")
        selected_ollama.set(full_model)

    initializing = True  # 🔑 prevents popup on startup

    def on_model_change(choice):
        nonlocal initializing

        # 🚫 Skip popup logic during initialization
        if initializing:
            return

        if choice == "ollama":
            models = get_ollama_models()

            if models:
                if selected_ollama.get() not in models:
                    selected_ollama.set(models[0])

                ollama_dropdown["menu"].delete(0, "end")
                for model in models:
                    ollama_dropdown["menu"].add_command(
                        label=model,
                        command=tk._setit(selected_ollama, model, on_ollama_model_change)
                    )

                ollama_dropdown.pack(pady=10)
                current_model_label.config(
                    text=f"Selected model: {selected_ollama.get()}"
                )
                current_model_label.pack(pady=5)

                save_model_choice(selected_ollama.get())
            else:
                ollama_dropdown.pack_forget()
                current_model_label.pack_forget()

        elif choice == "chatgpt":
            ensure_key("chatgpt_key.txt", "ChatGPT")
            save_model_choice("chatgpt")

        elif choice == "claude":
            ensure_key("claude_key.txt", "Claude")
            save_model_choice("claude")

        elif choice == "grok":
            ensure_key("grok_key.txt", "Grok")
            save_model_choice("grok")

    def on_ollama_model_change(model):
        save_model_choice(model)
        current_model_label.config(text=f"Selected model: {model}")

    dropdown = tk.OptionMenu(root, selected, *options, command=on_model_change)
    dropdown.pack(pady=10)

    ollama_dropdown = tk.OptionMenu(root, selected_ollama, "")
    ollama_dropdown.pack_forget()

    current_model_label = tk.Label(root, text="")
    current_model_label.pack_forget()

    # ✅ Manual UI setup (NO popups)
    if selected.get() == "ollama":
        models = get_ollama_models()
        if models:
            if selected_ollama.get() not in models:
                selected_ollama.set(models[0])

            for model in models:
                ollama_dropdown["menu"].add_command(
                    label=model,
                    command=tk._setit(selected_ollama, model, on_ollama_model_change)
                )

            ollama_dropdown.pack(pady=10)
            current_model_label.config(
                text=f"Selected model: {selected_ollama.get()}"
            )
            current_model_label.pack(pady=5)

    initializing = False  # ✅ now allow user-triggered actions

    # Audio UI
    ui.record_audio(root)

    def on_generate():
        from audio import recording as rec

        if not os.path.exists("temp.wav"):
            print("No recording available")
            return

        transcription = rec.transcribe_audio("temp.wav")
        print("Transcription:\n", transcription)

        provider_map = {
            "claude": "claude",
            "chatgpt": "gpt-4o",
            "grok": "grok-1.0",
            "ollama": "llama2",
        }

        sel = load_model_choice()
        model = provider_map.get(sel, sel)

        prompt = (
            "You are an academic assistant. "
            "Based on the following transcript, produce concise study notes:\n"
            + transcription
        )

        try:
            from ollama import chat

            print(f"Using ollama API with model {model}")

            stream = chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            notes = ""
            for chunk in stream:
                if hasattr(chunk, "message") and hasattr(chunk.message, "content"):
                    notes += chunk.message.content

            print("Generated notes:\n", notes)

        except ImportError:
            try:
                result = subprocess.run(
                    ["ollama", "run", model, "--prompt", prompt],
                    capture_output=True,
                    text=True
                )
                print("Generated notes:\n", result.stdout.strip())

            except Exception as e:
                print("Error running ollama CLI:", e)

        except Exception as e:
            print("Error:", e)

    tk.Button(root, text="Generate Notes", command=on_generate).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
