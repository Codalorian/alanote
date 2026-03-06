<<<<<<< HEAD
import tkinter as tk
from ui import ui

def main():
    root = tk.Tk()
    root.title("Alanote")
    root.geometry("400x300")
    
    label = tk.Label(root, text="Welcome to Alanote!")
    label.pack(pady=20)

    # Create the record audio window in the same event loop
    ui.record_audio(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
=======

>>>>>>> 21633174a4a34392b29db9d7ab4684c53aa0cf73
