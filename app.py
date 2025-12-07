import gradio as gr
import whisper
import yt_dlp
import tempfile
import os
from pathlib import Path


def download_audio(youtube_url: str, output_path: str) -> str:
    """Download audio from YouTube URL."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return output_path + '.mp3'


def transcribe_video(youtube_url: str, model_size: str, progress=gr.Progress()):
    """Transcribe YouTube video using Whisper."""
    if not youtube_url:
        return "Please enter a YouTube URL.", None

    try:
        progress(0.1, desc="Loading Whisper model...")
        model = whisper.load_model(model_size)

        progress(0.3, desc="Downloading audio from YouTube...")
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = os.path.join(temp_dir, "audio")
            audio_file = download_audio(youtube_url, audio_path)

            progress(0.5, desc="Transcribing audio...")
            result = model.transcribe(audio_file)
            transcript = result["text"]

            progress(0.9, desc="Preparing download file...")
            # Create a temporary file for download
            txt_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                delete=False,
                encoding='utf-8'
            )
            txt_file.write(transcript)
            txt_file.close()

            progress(1.0, desc="Done!")
            return transcript, txt_file.name

    except Exception as e:
        return f"Error: {str(e)}", None


def create_interface():
    """Create and return the Gradio interface."""
    with gr.Blocks(
        title="YouTube Video to Text",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown(
            """
            # YouTube Video to Text Transcription

            Convert YouTube videos to text using OpenAI's Whisper model.

            **How to use:**
            1. Paste a YouTube URL
            2. Select a Whisper model size (larger = more accurate but slower)
            3. Click "Transcribe" and wait for the result
            4. Download the transcript as a TXT file
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                url_input = gr.Textbox(
                    label="YouTube URL",
                    placeholder="https://www.youtube.com/watch?v=...",
                    lines=1
                )

                model_dropdown = gr.Dropdown(
                    choices=["tiny", "base", "small", "medium", "large"],
                    value="base",
                    label="Whisper Model Size",
                    info="tiny: fastest, large: most accurate"
                )

                transcribe_btn = gr.Button("Transcribe", variant="primary")

        with gr.Row():
            with gr.Column():
                output_text = gr.Textbox(
                    label="Transcript",
                    lines=15,
                    show_copy_button=True
                )

                download_file = gr.File(
                    label="Download Transcript",
                    visible=True
                )

        transcribe_btn.click(
            fn=transcribe_video,
            inputs=[url_input, model_dropdown],
            outputs=[output_text, download_file]
        )

        gr.Markdown(
            """
            ---
            **Note:**
            - Files are not stored permanently on the server
            - Processing time depends on video length and model size
            - For best results on longer videos, use "small" or "medium" model
            """
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
