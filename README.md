# 🎬 ReelTranscriber

A local-first video transcription tool that converts video files into:

- Clean transcript (`.txt`)
- Subtitle file (`.srt`)
- Web subtitle file (`.vtt`)

All processing runs entirely on your machine using Faster-Whisper, no uploads, no external APIs.

---

## 🚀 Why This Project?

Most online transcription tools require:

1. Uploading your video  
2. Waiting for server processing  
3. Downloading the transcript  

ReelTranscriber simplifies that into a single local app that keeps your files private and processes everything directly on your system.

---

## ✨ Features

- Local transcription using Faster-Whisper
- Automatic audio extraction with FFmpeg
- Whisper model selection (`tiny` → `large-v3`)
- Language auto-detection or manual selection
- Optional silence removal (VAD filter)
- Export formats:
  - TXT (plain transcript)
  - SRT (subtitle format)
  - VTT (web subtitle format)
- Clean and minimal UI

---

## 🛠 Tech Stack

- Python
- Gradio
- Faster-Whisper (CTranslate2 backend)
- FFmpeg

---

## 📦 Installation (Windows)

Clone the repository:

```powershell
git clone https://github.com/deepankshu/ReelTranscriber.git
cd ReelTranscriber
Create a virtual environment: python -m venv .venv
.\.venv\Scripts\Activate.ps1
Install dependencies: pip install -r requirements.txt
Run the app: python app.py
The application will automatically open in your browser.

▶️ Usage
Upload a video file (mp4, mov, mkv, webm)
Select Whisper model (default: small)
Choose language (or keep auto)
Click Transcribe
Download transcript or subtitle files
Exports are saved locally inside the _exports/ folder.

🔒 Privacy
All transcription processing happens locally on your computer.
No files are uploaded to any external server.

📄 License
MIT License

- Add GitHub repo “About” description + tags  
- Make this look stronger for recruiters  
- Or package it into a Windows `.exe` so it looks like real software 👀
