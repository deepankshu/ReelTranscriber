import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Optional

import gradio as gr
from faster_whisper import WhisperModel


# ------------------ Utils ------------------
def run_ffmpeg_extract_audio(video_path: str, wav_path: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        wav_path,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{p.stderr}")


def clean_text(t: str) -> str:
    t = t.strip()
    t = re.sub(r"\s+", " ", t)
    return t


def ts_srt(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    hh = ms // 3600000
    ms %= 3600000
    mm = ms // 60000
    ms %= 60000
    ss = ms // 1000
    ms %= 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def ts_vtt(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    ms = int(round(seconds * 1000))
    hh = ms // 3600000
    ms %= 3600000
    mm = ms // 60000
    ms %= 60000
    ss = ms // 1000
    ms %= 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d}.{ms:03d}"


@dataclass
class Seg:
    start: float
    end: float
    text: str


def to_srt(segs: List[Seg]) -> str:
    out = []
    i = 1
    for s in segs:
        text = clean_text(s.text)
        if not text:
            continue
        out.append(str(i))
        out.append(f"{ts_srt(s.start)} --> {ts_srt(s.end)}")
        out.append(text)
        out.append("")
        i += 1
    return "\n".join(out).strip() + "\n"


def to_vtt(segs: List[Seg]) -> str:
    out = ["WEBVTT", ""]
    for s in segs:
        text = clean_text(s.text)
        if not text:
            continue
        out.append(f"{ts_vtt(s.start)} --> {ts_vtt(s.end)}")
        out.append(text)
        out.append("")
    return "\n".join(out).strip() + "\n"


# ------------------ Model ------------------
MODEL_SIZE_DEFAULT = "small"
_model: Optional[WhisperModel] = None
_model_size_loaded: Optional[str] = None


def get_model(size: str) -> WhisperModel:
    global _model, _model_size_loaded
    if _model is None or _model_size_loaded != size:
        _model = WhisperModel(size, device="cpu", compute_type="int8")
        _model_size_loaded = size
    return _model


# ------------------ Transcription ------------------
def transcribe(video_file, model_size: str, language: str, vad_filter: bool):
    if video_file is None:
        raise gr.Error("Please upload a video first.")

    video_path = video_file.name

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "audio.wav")
        run_ffmpeg_extract_audio(video_path, wav_path)

        model = get_model(model_size)
        lang = None if language == "auto" else language

        segments, info = model.transcribe(
            wav_path,
            language=lang,
            vad_filter=vad_filter,
            vad_parameters={"min_silence_duration_ms": 500} if vad_filter else None,
            beam_size=5,
        )

        segs: List[Seg] = []
        parts = []
        for s in segments:
            segs.append(Seg(float(s.start), float(s.end), s.text))
            parts.append(s.text)

        transcript = clean_text(" ".join(parts))
        srt = to_srt(segs)
        vtt = to_vtt(segs)

        exports_dir = os.path.join(os.getcwd(), "_exports")
        os.makedirs(exports_dir, exist_ok=True)

        txt_path = os.path.join(exports_dir, "transcript.txt")
        srt_path = os.path.join(exports_dir, "captions.srt")
        vtt_path = os.path.join(exports_dir, "captions.vtt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcript + "\n")
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt)
        with open(vtt_path, "w", encoding="utf-8") as f:
            f.write(vtt)

        detected = getattr(info, "language", None)
        meta = f"Detected language: {detected or 'unknown'}  |  Model: {model_size}"

        return transcript, meta, txt_path, srt_path, vtt_path


# ------------------ UI ------------------
CUSTOM_CSS = """
.gradio-container {
  max-width: 980px !important;
  margin: 0 auto !important;
  padding-top: 32px !important;
}
h1 {
  font-size: 28px !important;
  font-weight: 600 !important;
}
#subtitle {
  margin-top: -6px;
  opacity: 0.7;
}
.card {
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 16px;
  padding: 18px;
}
"""

theme = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    radius_size="lg",
    text_size="md",
)

with gr.Blocks(title="Reel Transcriber (Local)", theme=theme, css=CUSTOM_CSS) as demo:
    gr.Markdown("# 🎬 Reel Transcriber")
    gr.Markdown(
        "Upload any video file and get transcript + subtitle files instantly.",
        elem_id="subtitle",
    )

    with gr.Row():
        with gr.Column(scale=5):
            with gr.Group(elem_classes=["card"]):
                video = gr.File(
                    label="Upload video (mp4/mov/mkv/webm)",
                    file_types=[".mp4", ".mov", ".mkv", ".webm"],
                )

                with gr.Row():
                    model_size = gr.Dropdown(
                        choices=["tiny", "base", "small", "medium", "large-v3"],
                        value=MODEL_SIZE_DEFAULT,
                        label="Whisper model",
                    )
                    language = gr.Dropdown(
                        choices=["auto", "en", "hi"],
                        value="auto",
                        label="Language",
                    )

                vad = gr.Checkbox(value=True, label="Remove silence")

                btn = gr.Button("✨ Transcribe", variant="primary")

        with gr.Column(scale=6):
            with gr.Group(elem_classes=["card"]):
                meta = gr.Textbox(label="Info", interactive=False)
                transcript = gr.Textbox(label="Transcript", lines=14)

    with gr.Group(elem_classes=["card"]):
        gr.Markdown("### Downloads")
        with gr.Row():
            out_txt = gr.File(label="Transcript (.txt)")
            out_srt = gr.File(label="Captions (.srt)")
            out_vtt = gr.File(label="Captions (.vtt)")

    btn.click(
        fn=transcribe,
        inputs=[video, model_size, language, vad],
        outputs=[transcript, meta, out_txt, out_srt, out_vtt],
    )

demo.launch(inbrowser=True, server_port=7860)
