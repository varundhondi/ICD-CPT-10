import torch
import whisper
import json
import os
import tkinter as tk
from tkinter import filedialog
from pyannote.audio import Pipeline
from dotenv import load_dotenv

# ---- Step 0: Load Hugging Face Token from .env file ----
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

if not HF_TOKEN:
    print("❌ Hugging Face token not found. Please set HUGGINGFACE_TOKEN in your .env file.")
    exit()

# ---- Step 1: GUI file picker for selecting audio ----
try:
    root = tk.Tk()
    root.withdraw()
    audio_path = filedialog.askopenfilename(
        title="Select Audio File", filetypes=[("Audio Files", "*.wav *.mp3 *.m4a")]
    )
except Exception as e:
    print("⚠️ Tkinter file dialog failed. Make sure you're not in a headless terminal.")
    exit()

if not audio_path:
    print("❌ No audio file selected. Exiting.")
    exit()

print(f"✅ Uploaded: {audio_path}")

# ---- Step 2: Load pyannote diarization model ----
print("🔄 Loading speaker diarization model...")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_TOKEN
)

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pipeline.to(device)

# ---- Step 3: Run diarization ----
print("🔍 Running speaker diarization...")
diarization = pipeline(audio_path)

# ---- Step 4: Transcribe audio using Whisper ----
print("🧠 Transcribing with Whisper...")
model = whisper.load_model("base")
result = model.transcribe(audio_path)

print("\n--- Full Transcription ---")
print(result["text"])

segments = result["segments"]

# ---- Step 5: Manual Speaker Alternation (fallback labeling) ----
print("\n--- Manual Alternating Speakers ---")
speaker_turn = 0
for segment in segments:
    start = segment['start']
    end = segment['end']
    text = segment['text'].strip()
    speaker_label = "doctor" if speaker_turn % 2 == 0 else "patient"
    speaker_turn += 1
    print(f"[{start:.1f}s - {end:.1f}s] ({speaker_label}): {text}")

# ---- Step 6: Diarization-Based Labeling ----
def find_speaker(segment_start, segment_end, diarization_result):
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        if max(segment_start, turn.start) < min(segment_end, turn.end):
            return speaker
    return "Unknown Speaker"

print("\n--- Diarization-Based Transcription ---")
transcript_lines = []
for segment in segments:
    start = segment['start']
    end = segment['end']
    text = segment['text'].strip()
    speaker_label = find_speaker(start, end, diarization)
    line = f"[{start:.1f}s - {end:.1f}s] ({speaker_label}): {text}"
    transcript_lines.append(line)
    print(line)

# ---- Step 7: Save to text file ----
output_file = "final_transcription.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(transcript_lines))

print(f"\n💾 Saved diarized transcription to: {output_file}")