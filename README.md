---
title: YouTube Video to Text
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# YouTube Video to Text Transcription

A Gradio-based application that converts YouTube videos to text using OpenAI's Whisper speech recognition model.

## Features

- **YouTube URL Input**: Simply paste any YouTube video URL
- **Multiple Model Sizes**: Choose from tiny, base, small, medium, or large Whisper models
- **Download Transcript**: Get your transcript as a downloadable TXT file
- **No Permanent Storage**: Files are processed temporarily and not stored on the server

## How to Use

1. Paste a YouTube video URL into the input field
2. Select a Whisper model size:
   - `tiny`: Fastest, least accurate
   - `base`: Good balance for short videos
   - `small`: Better accuracy
   - `medium`: High accuracy
   - `large`: Best accuracy, slowest
3. Click "Transcribe" and wait for processing
4. View the transcript and download as TXT file

## Technical Details

- **Speech Recognition**: OpenAI Whisper
- **Audio Download**: yt-dlp
- **Interface**: Gradio
- **Hosting**: Hugging Face Spaces

## Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd Video-to-Text-App

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for audio processing)
# On Ubuntu/Debian:
sudo apt install ffmpeg
# On macOS:
brew install ffmpeg
# On Windows:
# Download from https://ffmpeg.org/download.html

# Run the app
python app.py
```

## License

MIT License
