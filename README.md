# 🎬 ReelTranscriber (Local)

A clean, local-first video transcription tool that converts any video file into:
- **Transcript** (`.txt`)
- **Subtitles** (`.srt`)
- **Web captions** (`.vtt`)

Built for speed and privacy: **everything runs on your machine** (no uploads, no external services).

---

## ✨ Why this exists

Online tools usually make you:
1) download a video
2) upload it to another site
3) wait for transcription
4) download the result

**ReelTranscriber** combines that into a single, lightweight local app with a simple UI.

---

## ✅ Features

- Local transcription using **Faster-Whisper**
- Audio extraction via **FFmpeg**
- Clean minimal UI (Gradio)
- Optional silence filtering (VAD)
- Multiple Whisper model sizes (`tiny` → `large-v3`)
- Language auto-detection + manual selection
- One-click exports: TXT / SRT / VTT

---

## 🧰 Tech Stack

- Python
- Gradio
- Faster-Whisper (CTranslate2)
- FFmpeg

---

## 🚀 Quick Start (Windows)

### 1) Clone the repo
```bash
git clone https://github.com/deepankshu/ReelTranscriber.git
cd ReelTranscriber
