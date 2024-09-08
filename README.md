# BTS (BookToSpeech)

BTS is a tool designed to assist dyslexic individuals or those who have difficulty following books through reading. It automatically converts images of book pages into audio using a realistic voice.

## Features
- Converts images of book pages to audio
- Supports multiple images in a ZIP file
- Uses ElevenLabs API for speech synthesis
- Translates and transcribes text using Anthropic's API

## Prerequisites
- Python 3.x
- `Pillow`, `anthropic`, `requests` libraries

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/BTS.git
   cd BTS
   ```

2. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   ```sh
   export ANTHROPIC_API_KEY='your_anthropic_api_key'
   export ELEVENLABS_API_KEY='your_elevenlabs_api_key'
   export ELEVENLABS_VOICE_ID='desired_voice_id'
   ```

## Usage

1. Place your ZIP files containing images in the `BTS` directory.
2. Run the script:
   ```sh
   python BTS/main.py
   ```

## License
Apache License Version 2.0,