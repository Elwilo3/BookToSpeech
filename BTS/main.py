import os
import zipfile
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import tempfile
import base64
import anthropic
import sys
import requests
import json
from pathlib import Path

# Constants
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
TARGET_IMAGE_SIZE = (951, 1268)
MAX_IMAGES_BEFORE_PROMPT = 20
TRANSCRIPT_DIR = Path("BTS/transcripts")
AUDIO_DIR = Path("BTS/audio")
ZIP_FOLDER = Path("BTS")

# ElevenLabs API Constants
VOICE_ID = "G17SuINrv2H9FC6nvetn"  # Christopher
YOUR_XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Image Processing Functions
def get_image_date(image_path):
    try:
        with Image.open(image_path) as image:
            exif_data = image._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(image_path.stat().st_mtime)

def resize_image(image_path, output_path):
    with Image.open(image_path) as img:
        img_ratio = img.width / img.height
        target_ratio = TARGET_IMAGE_SIZE[0] / TARGET_IMAGE_SIZE[1]

        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) / 2
            img = img.crop((left, 0, left + new_width, img.height))
        elif img_ratio < target_ratio:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) / 2
            img = img.crop((0, top, img.width, top + new_height))

        img = img.resize(TARGET_IMAGE_SIZE, Image.LANCZOS)
        img.save(output_path, quality=95)

# ZIP Processing Function
def process_zip(zip_path, temp_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    temp_dir_path = Path(temp_dir)
    image_files = [f for f in temp_dir_path.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
    image_dates = [(f, get_image_date(f)) for f in image_files]
    sorted_images = sorted(image_dates, key=lambda x: x[1], reverse=True)
    
    processed_images = []
    for i, (old_path, _) in enumerate(sorted_images, start=1):
        new_name = f"photo{i}{old_path.suffix}"
        new_path = temp_dir_path / new_name
        resize_image(old_path, new_path)
        processed_images.append(new_path)
        print(f"Processed {i}/{len(sorted_images)}: {old_path.name} -> {new_name}")
    
    return processed_images

# Transcription Functions
def transcribe_images(api_key, image_paths):
    def encode_image(file_path):
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    client = anthropic.Client(api_key=api_key)
    transcriptions = []

    for i, image_path in enumerate(image_paths, start=1):
        print(f"Transcribing image {i}/{len(image_paths)}")
        image_base64 = encode_image(image_path)

        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            system="Respond only in English only.",
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Image {i}:"},
                        {
                            "type": "image",
                            "source": {"type": "base64", 
                                       "media_type": "image/jpeg", 
                                       "data": image_base64},
                        },
                        {
                            "type": "text",
                            "text": """
                            You are to transcribe a scanned page from a book to make it available to a blind person as an audiobook. 
                            Your task is to provide a detailed transcription of the page without altering the actual text content your answer will be read directly without modification so do not write syntax or descriptions that are not in the book things like instead of 'Body text: I am lingren.....' Start reading the text verbatim 'I am lingren....'
                            Please include the following:
                            Text content: Transcribe all text on the page exactly as it appears, without editing or rewriting or adding testimonials.
                            Descriptions of visual elements: This is the only exception where you can create your own text you should create detailed descriptions of any visual elements on the page, such as graphs, images or charts. Describe what they represent, how they are designed, and any relevant information that may be important to someone who cannot see them.
                            YOU SHOULD ONLY DESCRIBE THINGS THAT ARE NECESSARY LIKE GRAPHS OR IMAGES. DO NOT DESCRIBE THINGS LIKE PAGE NUMBERS, LAYOUT OF THE PAGE ETC.
                            Make sure the transcript is comprehensive and provides all the necessary context to convey the content as accurately and accessibly as possible.
                            """
                        }
                    ],
                }
            ],
        )
        
        if message and message.content:
            transcription = "".join(block.text for block in message.content if block.type == 'text')
            transcriptions.append(transcription)
        else:
            transcriptions.append("[No transcription available]")

        if i % MAX_IMAGES_BEFORE_PROMPT == 0:
            confirm = input(f"Do you want to continue after processing {i} images (Y/N)? ")
            if confirm.lower() != 'y':
                break

    return transcriptions

def save_transcriptions(transcriptions):
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%d.%m_%H-%M")
    transcript_file = TRANSCRIPT_DIR / f"script_{timestamp}.txt"
    
    with open(transcript_file, "w", encoding='utf-8') as f:
        for trans in transcriptions:
            f.write(trans + '\n\n')
    
    print(f"Transcriptions saved to {transcript_file}")

def synthesize_speech(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    
    headers = {
      "Content-Type": "application/json",
      "xi-api-key": YOUR_XI_API_KEY
    }

    data = {
      "text": text,
      "model_id": "eleven_turbo_v2_5",
      "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
      }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(f"Error encountered, status: {response.status_code}, content: {response.text}")
        return None

    json_string = response.content.decode("utf-8")
    response_dict = json.loads(json_string)
    audio_bytes = base64.b64decode(response_dict["audio_base64"])

    AUDIO_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%d.%m_%H-%M")
    output_file = AUDIO_DIR / f"audio_{timestamp}.mp3"
    with open(output_file, 'wb') as f:
        f.write(audio_bytes)

    return output_file

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("API Key for Anthropic not found. Make sure it's set in the environment variables.")
        sys.exit(1)

    print("Starting ZIP processing...")
    all_processed_images = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for zip_file in ZIP_FOLDER.glob("*.zip"):
            print(f"Processing ZIP: {zip_file}")
            processed_images = process_zip(zip_file, temp_dir)
            all_processed_images.extend(processed_images)
        
        print("ZIP processing completed.")

        if all_processed_images:
            print("Starting transcription...")
            transcriptions = transcribe_images(api_key, all_processed_images)
            save_transcriptions(transcriptions)
            print("Transcription completed.")
            
            if transcriptions:
                print("Starting speech synthesis...")
                full_text = "\n\n".join(transcriptions)
                audio_file = synthesize_speech(full_text)
                if audio_file:
                    print(f"Speech synthesis completed. Audio saved to {audio_file}")
                else:
                    print("Speech synthesis failed.")
        else:
            print("No images found to transcribe.")
            
if __name__ == "__main__":
    main()