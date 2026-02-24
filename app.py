import gradio as gr
import whisper
import tempfile
import os


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
        title="Audio/Video to Text",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown(
            """
            # Audio/Video to Text Transcription

            Convert audio or video files to text using OpenAI's Whisper model.

            **Supported formats:** MP3, WAV, M4A, MP4, WebM, and more

            **How to use:**
            1. Upload an audio or video file
            2. Select a Whisper model size (larger = more accurate but slower)
            3. Click "Transcribe" and wait for the result
            4. Download the transcript as a TXT file
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                audio_input = gr.File(
                    label="Upload Audio/Video File",
                    file_types=[".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg", ".flac", ".aac"],
                    type="filepath"
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
            fn=transcribe_audio,
            inputs=[audio_input, model_dropdown],
            outputs=[output_text, download_file]
        )

        gr.Markdown(
            """
            ---
            **Note:**
            - Files are processed temporarily and not stored permanently
            - Processing time depends on file length and model size
            - For best results on longer files, use "small" or "medium" model
            """
        )

    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
