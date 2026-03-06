import tkinter as tk
from PIL import Image, ImageTk
import os
from audio import recording

# keep track of recording state and button image
_recording_state = False

def toggle_record(btn, label):
    global _recording_state
    result = recording.toggle_recording()
    if result == "started":
        _recording_state = True
        label.config(text="Recording... press again to stop")
    else:
        _recording_state = False
        label.config(text="Press the red button to start recording")
        # optionally transcribe immediately or leave for main
        print(f"Finished recording, file saved to temp.wav")


def record_audio(parent):
    record_window = tk.Toplevel(parent)
    record_window.title("Alanote - Record Audio")
    record_window.geometry("400x200")
    status_label = tk.Label(record_window, text="Press the red button to start recording")
    status_label.pack(pady=10)
    
    # Load and resize image
    image_path = os.path.join(os.path.dirname(__file__), "images/button.png")
    image = Image.open(image_path)
    image.thumbnail((80, 80))  # Resize to 80x80 pixels
    record_button_image = ImageTk.PhotoImage(image)
    
    record_button = tk.Button(record_window, image=record_button_image,
                              command=lambda: toggle_record(record_button, status_label))
    record_button.pack()
    
    # Keep reference to prevent garbage collection
    record_window.image = record_button_image
    
    return record_window