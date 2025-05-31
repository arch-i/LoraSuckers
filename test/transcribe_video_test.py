from pathlib import Path
import sys

from src.transcription.key_moments import generate_key_moments
from src.transcription.summarize_transcript import generate_summary
from src.transcription.transcribe_video import extract_audio, transcribe_audio

video_path = f"./resources/1748606202871805.mp4"
video_name = Path(video_path).stem
audio_path = f"{sys.path[0]}/{video_name}_audio.wav"
print(f"extracting audio to {audio_path}")
transcription_path = f"{sys.path[0]}/words.json"
print(f"extracting transcription to {transcription_path}")
extract_audio(video_path, audio_path)

transcription = transcribe_audio(audio_path)
print(transcription.text)
words_ = [(x.start, x.end, x.word) for x in transcription.words]
print(words_)
print(generate_summary(transcription.text))
print(generate_key_moments(transcription.text, words_))
