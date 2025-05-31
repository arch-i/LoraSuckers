import os
from openai import OpenAI
import subprocess


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "whisper-1")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def extract_audio(video_path, output_audio_path=None):
    """Extract audio from video file and convert to 16kHz WAV format"""
    if output_audio_path is None:
        output_audio_path = video_path.rsplit('.', 1)[0] + '.wav'
    
    print(f"Extracting audio from {video_path} to {output_audio_path}...")
    
    # Using ffmpeg to extract audio and convert to 16kHz WAV
    command = [
        'ffmpeg', '-i', video_path, 
        '-vn',                      # No video
        '-acodec', 'pcm_s16le',     # PCM 16-bit encoding
        '-ar', '16000',             # 16kHz sample rate (best for the Sarvam API)
        '-ac', '1',                 # Convert to mono
        output_audio_path
    ]
    
    subprocess.run(command, check=True)
    return output_audio_path



def transcribe_audio(audio_path, response_format="verbose_json", timestamp_granularities=["word"], model: str = MODEL):
    """Transcribe audio using Whisper with timestamps"""
    print("Transcribing audio with Whisper...")
    
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format=response_format,
                timestamp_granularities=timestamp_granularities
            )
        
        print("Transcription successful with timestamps")
        return response
    
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        return None
