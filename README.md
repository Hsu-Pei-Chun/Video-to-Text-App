---
title: Audio Video to Text
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# Audio/Video to Text Transcription

A Gradio-based application that converts audio and video files to text using OpenAI's Whisper speech recognition model.

url : https://huggingface.co/spaces/HsuPeiChun/Video-to-Text-App

## Features

- **File Upload**: Upload audio or video files directly
- **Multiple Formats**: Supports MP3, WAV, M4A, MP4, WebM, and more
- **Multiple Model Sizes**: Choose from tiny, base, small, medium, or large Whisper models
- **Download Transcript**: Get your transcript as a downloadable TXT file
- **No Permanent Storage**: Files are processed temporarily and not stored on the server

## How to Use

1. Upload an audio or video file
2. Select a Whisper model size:
   - `tiny`: Fastest, least accurate
   - `base`: Good balance for short files
   - `small`: Better accuracy
   - `medium`: High accuracy
   - `large`: Best accuracy, slowest
3. Click "Transcribe" and wait for processing
4. View the transcript and download as TXT file

## Technical Details

- **Speech Recognition**: OpenAI Whisper
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
