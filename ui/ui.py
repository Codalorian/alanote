import tkinter as tk
from PIL import Image, ImageTk
import os

def test():
    print("This works!")

def record_audio(parent):
    record_window = tk.Toplevel(parent)
    record_window.title("Alanote - Record Audio")
    record_window.geometry("400x200")
    tk.Label(record_window, text="Press the red button to start recording").pack(pady=10)
    
    # Load and resize image
    image_path = os.path.join(os.path.dirname(__file__), "images/button.png")
    image = Image.open(image_path)
    image.thumbnail((80, 80))  # Resize to 80x80 pixels
    record_button_image = ImageTk.PhotoImage(image)
    
    record_button = tk.Button(record_window, image=record_button_image, command=test)
    record_button.pack()
    
    # Keep reference to prevent garbage collection
    record_window.image = record_button_image
    
    return record_window