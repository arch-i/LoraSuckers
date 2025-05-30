import argparse
import json
import logging
import os
from typing import Dict, Any

from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# System prompt for short-form video summarization
SYSTEM_PROMPT = """
You are a summarization agent designed for short-form videos (under 90 seconds) that deliver dense, engaging information. Your job is to:
1. Summarize the core message concisely.
2. Identify and describe the tone and vibe (e.g., humorous, sarcastic, intense, inspiring, casual).
3. Extract a hook line or punchy quote if available (great for captions or intros).
Keep your style sharp and audience-focused. Prioritize clarity, energy, and relevance over formality.
"""

# Few-shot examples for better output consistency
FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Transcript:\nSo here's what nobody tells you about renting in Mumbai. You're not just paying for the space — you're paying for location, power backup, and a silent agreement that your landlord won't bother you too much. That's worth the 10k extra sometimes."
    },
    {
        "role": "assistant",
        "content": "Tone: Relatable, urban, slightly sarcastic\nSummary: Renting in Mumbai isn't just about square feet — it's about peace, power, and location. Sometimes, that extra 10k buys your sanity.\nHook line: \"You're not just paying for the space — you're buying peace.\""
    },
    {
        "role": "user",
        "content": "Transcript:\nHere's a crazy fact — in 2010, Blockbuster could've bought Netflix for $50 million. They laughed in the room. Today, Netflix is worth $200 billion and Blockbuster has one store left. Timing and vision are everything."
    },
    {
        "role": "assistant",
        "content": "Tone: Surprising, punchy, informative\nSummary: Blockbuster had the chance to buy Netflix for $50M in 2010. They passed. Now Netflix is worth billions — and Blockbuster is history.\nHook line: \"They laughed at Netflix — now they're gone.\""
    }
]

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def chat_completion(messages, temperature=0.3, model: str = MODEL) -> str:
    """Wrapper for OpenAI chat completion with retries."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()


def generate_summary(transcript: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
    """
    Generate different types of summaries from a transcript.
    
    Args:
        transcript: The full transcript text
        summary_type: Type of summary - "brief", "comprehensive", or "structured"
    
    Returns:
        Dictionary containing the summary and metadata
    """
    
    # Define different summary prompts based on type
    if summary_type == "brief":
        # Brief version - just the core summary
        user_prompt = f"Transcript:\n{transcript}"
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *FEW_SHOT_EXAMPLES,
            {"role": "user", "content": user_prompt}
        ]
        
    elif summary_type == "comprehensive":
        # Comprehensive version with additional context
        extended_prompt = SYSTEM_PROMPT + "\n\nFor longer content, also include:\n4. Key topics/themes covered\n5. Target audience insights\n6. Content category (Technology, Business, Lifestyle, etc.)"
        user_prompt = f"Transcript:\n{transcript}"
        messages = [
            {"role": "system", "content": extended_prompt},
            *FEW_SHOT_EXAMPLES,
            {"role": "user", "content": user_prompt}
        ]
        
    elif summary_type == "structured":
        # Structured JSON format
        json_prompt = """
You are a summarization agent for short-form videos. Analyze the transcript and return a JSON object with:
- "tone": The tone and vibe (e.g., humorous, sarcastic, intense, inspiring)
- "summary": Core message summarized concisely 
- "hook_line": A punchy quote or hook line for captions
- "category": Content category (Technology, Business, Lifestyle, etc.)
- "target_audience": Who this content is for
- "key_themes": Array of 2-3 main themes/topics
- "engagement_potential": High/Medium/Low based on content appeal

Return only valid JSON.
"""
        user_prompt = f"Transcript:\n{transcript}"
        messages = [
            {"role": "system", "content": json_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
    else:
        raise ValueError(f"Invalid summary_type. Choose from: brief, comprehensive, structured")
    
    logging.info(f"Generating {summary_type} summary...")
    
    summary_text = chat_completion(messages)
    
    # For structured summaries, try to parse as JSON
    if summary_type == "structured":
        try:
            summary_data = json.loads(summary_text)
            return {
                "type": summary_type,
                "content": summary_data,
                "raw_text": summary_text,
                "word_count": len(transcript.split()),
                "char_count": len(transcript)
            }
        except json.JSONDecodeError:
            logging.warning("Failed to parse structured summary as JSON, returning as text")
    
    return {
        "type": summary_type,
        "content": summary_text,
        "word_count": len(transcript.split()),
        "char_count": len(transcript)
    }


def run_transcript_summarization(
    transcript_file: str, 
    output_file: str = "summary.json", 
    summary_type: str = "comprehensive"
) -> None:
    """
    Summarize a transcript file and save results.
    
    Args:
        transcript_file: Path to input transcript file
        output_file: Path to output summary file
        summary_type: Type of summary to generate
    """
    try:
        # Read transcript
        with open(transcript_file, encoding="utf-8") as f:
            transcript = f.read().strip()
        
        if not transcript:
            raise ValueError("Transcript file is empty")
        
        print(f"📄 Loaded transcript ({len(transcript)} characters, ~{len(transcript.split())} words)")
        
        # Generate summary
        summary_result = generate_summary(transcript, summary_type)
        
        # Add metadata
        summary_result.update({
            "input_file": transcript_file,
            "timestamp": "2025-01-30T00:00:00Z",  # You could use datetime.now().isoformat()
            "model": MODEL,
            "version": "1.0.0"
        })
        
        # Save output
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary_result, f, ensure_ascii=False, indent=2)
        
        print(f"✔︎  Generated {summary_type} summary → {output_file}")
        
        # Display preview
        if summary_type == "structured" and isinstance(summary_result["content"], dict):
            print(f"\n🎯 Tone: {summary_result['content'].get('tone', 'N/A')}")
            print(f"📝 Summary: {summary_result['content'].get('summary', 'N/A')[:150]}...")
            print(f"🪝 Hook: {summary_result['content'].get('hook_line', 'N/A')}")
        else:
            print(f"\n📝 Summary preview: {str(summary_result['content'])[:200]}...")
        
    except Exception as e:
        print(f"❌ Summarization failed: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    # CLI interface
    parser = argparse.ArgumentParser(description="Generate summaries from video transcripts using OpenAI GPT-4o")
    parser.add_argument("--transcript_file", required=True, help="Path to transcript file")
    parser.add_argument("--output_file", default="summary.json", help="Output summary file")
    parser.add_argument("--summary_type", choices=["brief", "comprehensive", "structured"], 
                       default="comprehensive", help="Type of summary to generate")
    
    args = parser.parse_args()
    
    run_transcript_summarization(
        args.transcript_file, 
        args.output_file, 
        args.summary_type
    )