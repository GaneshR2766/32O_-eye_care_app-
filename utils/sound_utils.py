import os
from pydub import AudioSegment

def list_user_sounds():
    path = "sounds/user"
    return [f for f in os.listdir(path) if f.endswith(".wav")]

def get_audio_duration(filepath):
    try:
        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000  # seconds
    except:
        return 0

def trim_audio(filepath, start_sec, duration_sec=60):
    try:
        audio = AudioSegment.from_file(filepath)
        end = start_sec * 1000 + duration_sec * 1000
        trimmed = audio[start_sec * 1000:end]
        filename = os.path.basename(filepath)
        dest_path = os.path.join("sounds/user", filename)
        trimmed.export(dest_path, format="wav")
        return True
    except Exception as e:
        print("Trimming error:", e)
        return False
