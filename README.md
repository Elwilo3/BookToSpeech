# BTS (BookToSpeech)


BTS (BookToSpeech) is an tool designed to assist individuals with dyslexia or those who have difficulty following books through reading. It automatically converts images of book pages into audio using a realistic voice, making literature more accessible to everyone.

## Features

- **OCR and Transcription**: Utilizes advanced AI to accurately transcribe text and images.
- **Visual Element Description**: Provides detailed descriptions of graphs, charts, and images for a complete audio experience.
- **Text-to-Speech**: Converts transcribed text into high-quality, natural-sounding audio.
- **Batch Processing**: Handles multiple book pages efficiently through ZIP file processing.

## Installation

1. Clone the repository:
git clone https://github.com/Elwilo3/BookToSpeech.git
Copy
2. Install the required dependencies:
pip install -r requirements.txt
Copy
3. Set up your API keys as environment variables:
- `ANTHROPIC_API_KEY` for Claude AI
- `ELEVENLABS_API_KEY` for ElevenLabs text-to-speech

## Usage

1. Place your ZIP file(s) containing book page images in the `BTS` folder.

2. Run the main script:
python bts.py
Copy
3. The program will process the images, transcribe the text, and generate audio files.

4. Find the output in:
- `BTS/transcripts`: Text transcriptions
- `BTS/audio`: Generated audio files

## Configuration

You can customize the following in the script:

- `IMAGE_EXTENSIONS`: Supported image file types (only a few types work with Claude 3.5 sonnet)
- `TARGET_IMAGE_SIZE`: Desired image dimensions for processing
- `MAX_IMAGES_BEFORE_PROMPT`: Number of images to process before asking for continuation
- `VOICE_ID`: ElevenLabs voice ID for text-to-speech
- `SYSTEM_PROMPT`: The system prompt for the ai transcription
- `MESSAGE_PROMPT`: The message the ai gets with the image


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Claude](https://claude.ai) for writing half the code
- [Chatgpt](https://chatgpt.com) for writing the other half

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.

---

Made with ❤️ for accessibility in reading