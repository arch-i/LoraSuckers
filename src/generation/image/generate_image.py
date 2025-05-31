#!/usr/bin/env python3
"""
Image Generation Script using OpenAI GPT Image 1
Generates images from transcript segments and prompts
"""

import argparse
import base64
import json
import os
from io import BytesIO
from typing import Dict, Any

from openai import OpenAI
from PIL import Image

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-image-1"

# Get the directory of this script to find the prompt file
script_dir = os.path.dirname(os.path.abspath(__file__))
prompt_file_path = os.path.join(script_dir, "..", "prompts", "prompt_for_text_to_image.txt")

with open(prompt_file_path, "r") as f:
    prompt_for_text_to_image = f.read()

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_image(
    prompt: str = "",
    size: str = "1024x1024",
    quality: str = "auto",
    output_format: str = "png",
    output_compression: int = None
    ) -> Dict[str, Any]:

    """
    Generate an image using OpenAI GPT Image 1.
    
    Args:
        prompt: The image generation prompt
        size: Image size ("1024x1024", "1536x1024", "1024x1536", "auto")
        quality: Image quality ("low", "medium", "high", "auto")
        output_format: Output format ("png", "jpeg", "webp")
        output_compression: Compression level 0-100 for JPEG/WEBP
    
    Returns:
        Dictionary with image data, metadata, and generation info
    """
    try:
        # Prepare API parameters
        params = {
            "model": MODEL,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "output_format": output_format
        }
        
        # Add compression if specified for JPEG/WEBP
        if output_compression is not None and output_format in ["jpeg", "webp"]:
            params["output_compression"] = output_compression
        
        response = client.images.generate(**params)
        
        image_base64 = response.data[0].b64_json
        revised_prompt = getattr(response.data[0], 'revised_prompt', None)
        
        return {
            "success": True,
            "image_base64": image_base64,
            "original_prompt": prompt,
            "model": MODEL,
            "size": size,
            "quality": quality,
            "output_format": output_format,
            "output_compression": output_compression
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "original_prompt": prompt,
        }
    
def generate_prompt_for_text_to_image(
    summary: str = "",
    transcript_segment: str = "",
) -> str:
    """
    Generate a prompt for text-to-image using OpenAI GPT Image 1.
    """
    prompt = f"""{prompt_for_text_to_image}
    The summary of the transcript of the video is: {summary}
    The segment of the transcript for which a prompt needs to be generated is: {transcript_segment}"""

    generated_prompt = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Generate a prompt for the shared summary and transcript segment."}
        ]
    )

    generated_prompt = generated_prompt.choices[0].message.content

    return generated_prompt