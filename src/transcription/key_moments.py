from src.transcription.summarize_transcript import chat_completion
from src.resource.prompts.prompts import prompts


def generate_key_moments(transcription_summary, word_time_stamps):
    key_moments_prompt = f"<prompt>{prompts['key-moment']}</prompt>\n<summary>{transcription_summary}</summary>\n</wordTimeStamps>{word_time_stamps}<wordTimestamps>\n"
    return chat_completion( [{"role": "user", "content": key_moments_prompt}]
        )
