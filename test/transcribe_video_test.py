from pathlib import Path
import sys
import base64
from PIL import Image
from io import BytesIO
import json
import os

sys.path.append(str(Path(__file__).parent.parent))

from src.transcription.key_moments import generate_key_moments
from src.transcription.summarize_transcript import generate_summary
from src.transcription.transcribe_video import extract_audio, transcribe_audio
from src.generation.image.generate_image import generate_image, generate_prompt_for_text_to_image

video_path = f"test/resources/1748606202871805.mp4"
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
summary = generate_summary(transcription.text)
print(summary)
key_moments = generate_key_moments(transcription.text, words_)
print(key_moments)

# Parse the JSON string to get Python objects
# Extract JSON from markdown code block
key_moments_json = key_moments.split('```json\n')[1].split('\n```')[0]
key_moments_parsed = json.loads(key_moments_json)
first_key_moment = key_moments_parsed[0]

print(f"First key moment: {first_key_moment}")
print(f"First key moment visual idea: {first_key_moment['visual_idea']}")

prompt_for_first_key_moment_image = generate_prompt_for_text_to_image(summary=summary["content"], transcript_segment=first_key_moment["visual_idea"])
print(f"Prompt for first key moment image: {prompt_for_first_key_moment_image}")

image_for_first_key_moment = generate_image(prompt=prompt_for_first_key_moment_image)
print(f"Image generation success: {image_for_first_key_moment['success']}")

if image_for_first_key_moment['success']:
    # Save the image to view it
    image_base64 = image_for_first_key_moment['image_base64']
    image_bytes = base64.b64decode(image_base64)
    image = Image.open(BytesIO(image_bytes))
    
    output_path = "test/generated_image.png"
    image.save(output_path)
    print(f"✅ Image saved to: {output_path}")
else:
    print(f"❌ Image generation failed: {image_for_first_key_moment['error']}")


def generate_images_for_all_key_moments(summary_content, key_moments_parsed, output_dir="test/generated_images"):
    """
    Generate images for all key moments and return organized data.
    
    Args:
        summary_content: The summary content string
        key_moments_parsed: List of parsed key moment dictionaries
        output_dir: Directory to save generated images
        
    Returns:
        List of dictionaries with timestamp, visual_idea, and image_path
    """
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for i, key_moment in enumerate(key_moments_parsed):
        print(f"\n🎨 Processing key moment {i+1}/{len(key_moments_parsed)}")
        print(f"📅 Timestamp: {key_moment['timestamp']}")
        print(f"💡 Visual idea: {key_moment['visual_idea']}")
        
        # Generate prompt for this key moment
        prompt = generate_prompt_for_text_to_image(
            summary=summary_content, 
            transcript_segment=key_moment["visual_idea"]
        )
        print(f"📝 Generated prompt: {prompt[:100]}...")
        
        # Generate image
        image_result = generate_image(prompt=prompt)
        
        # Prepare result dictionary
        result = {
            "timestamp": key_moment["timestamp"],
            "visual_idea": key_moment["visual_idea"],
            "image_path": None,
            "success": image_result["success"]
        }
        
        if image_result["success"]:
            # Save the image
            image_base64 = image_result['image_base64']
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            
            # Create filename based on timestamp and index
            safe_timestamp = key_moment["timestamp"].replace(":", "-")
            filename = f"key_moment_{i+1}_{safe_timestamp}.png"
            image_path = os.path.join(output_dir, filename)
            
            image.save(image_path)
            result["image_path"] = image_path
            print(f"✅ Image saved: {image_path}")
        else:
            result["error"] = image_result.get("error", "Unknown error")
            print(f"❌ Image generation failed: {result['error']}")
        
        results.append(result)
    
    return results


# Generate images for all key moments
print(f"\n🚀 Generating images for all {len(key_moments_parsed)} key moments...")
all_key_moment_images = generate_images_for_all_key_moments(
    summary_content=summary["content"],
    key_moments_parsed=key_moments_parsed
)

# Display results
print(f"\n📊 Results Summary:")
successful_generations = sum(1 for result in all_key_moment_images if result["success"])
print(f"✅ Successfully generated: {successful_generations}/{len(all_key_moment_images)} images")

for i, result in enumerate(all_key_moment_images):
    print(f"\nKey Moment {i+1}:")
    print(f"  📅 Timestamp: {result['timestamp']}")
    print(f"  💡 Visual Idea: {result['visual_idea']}")
    if result["success"]:
        print(f"  🖼️  Image Path: {result['image_path']}")
    else:
        print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

print(f"\n🎯 Pipeline complete! Check the 'test/generated_images/' directory for all B-roll images.")