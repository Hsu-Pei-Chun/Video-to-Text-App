import gradio as gr
import whisper
import requests
import tempfile
import time
import os

# YouTube to MP3 API endpoint (deployed on Zeabur)
YT_MP3_API_URL = os.getenv("YT_MP3_API_URL", "http://localhost:8000")


def download_youtube_audio(youtube_url, progress=gr.Progress()):
    """Download YouTube video as MP3 via external API."""
    api_url = YT_MP3_API_URL.rstrip("/")

    # Step 1: Submit conversion task
    progress(0.1, desc="Submitting YouTube conversion task...")
    resp = requests.post(
        f"{api_url}/api/convert",
        json={"url": youtube_url, "quality": "192"},
        timeout=30,
    )
    if resp.status_code != 202:
        error = resp.json().get("detail", {})
        msg = error.get("message", "Unknown error") if isinstance(error, dict) else str(error)
        raise gr.Error(f"Conversion failed: {msg}")

    task_id = resp.json()["task_id"]

    # Step 2: Poll for completion
    for i in range(120):  # max ~4 minutes
        time.sleep(2)
        status_resp = requests.get(f"{api_url}/api/status/{task_id}", timeout=10)
        status_data = status_resp.json()
        status = status_data["status"]
        task_progress = status_data.get("progress", 0)

        progress(0.1 + 0.6 * (task_progress / 100), desc=f"Converting... {task_progress}%")

        if status == "completed":
            break
        elif status == "failed":
            raise gr.Error(f"Conversion failed: {status_data.get('error', 'Unknown error')}")
    else:
        raise gr.Error("Conversion timed out. Please try a shorter video.")

    # Step 3: Download MP3 file
    progress(0.75, desc="Downloading MP3...")
    download_resp = requests.get(f"{api_url}/api/download/{task_id}", timeout=120)
    if download_resp.status_code != 200:
        raise gr.Error("Failed to download MP3 file.")

    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp_file.write(download_resp.content)
    tmp_file.close()

    return tmp_file.name


def transcribe_audio(audio_file, model_size: str, progress=gr.Progress()):
    """Transcribe audio/video file using Whisper."""
    if audio_file is None:
        return "Please upload an audio or video file.", None

    try:
        progress(0.2, desc="Loading Whisper model...")
        model = whisper.load_model(model_size)

        progress(0.5, desc="Transcribing audio...")
        result = model.transcribe(audio_file)
        transcript = result["text"]

        progress(0.9, desc="Preparing download file...")
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


def transcribe_youtube(youtube_url, model_size, progress=gr.Progress()):
    """Download YouTube audio and transcribe it."""
    if not youtube_url or not youtube_url.strip():
        return "Please enter a YouTube URL.", None

    try:
        # Download MP3 from YouTube via API
        mp3_path = download_youtube_audio(youtube_url, progress)

        # Transcribe the downloaded MP3
        progress(0.8, desc="Loading Whisper model...")
        model = whisper.load_model(model_size)

        progress(0.9, desc="Transcribing audio...")
        result = model.transcribe(mp3_path)
        transcript = result["text"]

        # Cleanup temp MP3
        os.unlink(mp3_path)

        progress(0.95, desc="Preparing download file...")
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

    except gr.Error:
        raise
    except Exception as e:
        return f"Error: {str(e)}", None


def create_interface():
    """Create and return the Gradio interface."""
    with gr.Blocks(
        title="Audio/Video to Text",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown(
            """
            # Audio/Video to Text Transcription

            Convert audio, video files, or YouTube videos to text using OpenAI's Whisper model.
            """
        )

        input_mode = gr.Radio(
            choices=["Upload File", "YouTube URL"],
            value="Upload File",
            label="Input Mode"
        )

        model_dropdown = gr.Dropdown(
            choices=["tiny", "base", "small", "medium", "large"],
            value="base",
            label="Whisper Model Size",
            info="tiny: fastest, large: most accurate"
        )

        # File upload input
        audio_input = gr.File(
            label="Upload Audio/Video File",
            file_types=[".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac", ".aac"],
            type="filepath",
            visible=True
        )

        # YouTube URL input
        youtube_input = gr.Textbox(
            label="YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            visible=False
        )

        transcribe_btn = gr.Button("Transcribe", variant="primary")

        def toggle_input(mode):
            return (
                gr.update(visible=(mode == "Upload File")),
                gr.update(visible=(mode == "YouTube URL")),
            )

        input_mode.change(
            fn=toggle_input,
            inputs=[input_mode],
            outputs=[audio_input, youtube_input]
        )

        output_text = gr.Textbox(
            label="Transcript",
            lines=15,
            show_copy_button=True
        )
        download_file = gr.File(
            label="Download Transcript",
            visible=True
        )

        def transcribe_dispatch(mode, audio_file, youtube_url, model_size, progress=gr.Progress()):
            if mode == "YouTube URL":
                return transcribe_youtube(youtube_url, model_size, progress)
            else:
                return transcribe_audio(audio_file, model_size, progress)

        transcribe_btn.click(
            fn=transcribe_dispatch,
            inputs=[input_mode, audio_input, youtube_input, model_dropdown],
            outputs=[output_text, download_file]
        )

        gr.Markdown(
            """
            ---
            **Note:**
            - Files are processed temporarily and not stored permanently
            - Processing time depends on file length and model size
            - For best results on longer files, use "small" or "medium" model
            - YouTube videos are limited to 30 minutes
            """
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(server_name="0.0.0.0", share=False)
