This is Alanote, an open source audio note taking application. Simply record your teacher's lecture during class, or your own voice, and have the AI convert from text to audio and create personal notes based on the lecture for you.

- Available for Linux, Windows, MacOS, and Android (phones+computer)
- Tkinter w/ Python
- Choice of Ollama (PC/Mac only), ChatGPT, Grok, and potentially Claude
- Simple UI 
- Open Source
- MIT License

There should be an installer for Windows, as things can get cluttered fast with these types of projects in Windows. For Android, the APK already auto-installs on startup, so there is no need to work with that.
For Linux and MacOS, we could potentially have an installer via the APT/brew package manager. Maybe this too will be supported by the major distributions like Fedora (rpm package manager), openSUSE (zypper), Arch linux (pacman or yay)

-Project structure
                         |------design.py
alanote_base-----|----ui/|
                 |       |------other files will probably be needed.
                 |
                 |
                 |               |-------claude/-----claude.py
                 |----generation/|-------chatgpt/-----chatgpt.py
                 |               |-------grok/-----grok.py
                 |               |-------ollama-----ollama.py
                 |               |-------generate-notes.py
                 |
                 |          |-------recording.py
                 |----audio/|-------stt.py
                 |          |-------read-notes-custom-voice.py
                 |
                 |
                 |
                 |----main.py
                 
