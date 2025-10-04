# scripts/step_04_compose_final_video.py
import ffmpeg
import os

ASSETS_DIR = "assets"
OUTPUT_DIR = "output"

def compose_final_video(audio_path: str, chart_image_path: str, output_filename: str) -> str:
    """
    Creates a video by showing a chart, then a presenter image with AI audio.
    """
    print("Composing final video with AI audio...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    presenter_image_path = os.path.join(ASSETS_DIR, "presenter.jpg")
    if not os.path.exists(presenter_image_path):
        print(f"Error: Presenter image not found at {presenter_image_path}")
        return None

    try:
        # --- Get the duration of the generated audio file ---
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe['format']['duration'])

        # --- Define video segments ---
        # Segment 1: The chart, shown for 5 seconds
        chart_segment = (
            ffmpeg
            .input(chart_image_path, t=5, loop=1, framerate=25)
            .filter('scale', size='1280:720', force_original_aspect_ratio='decrease')
            .filter('pad', w=1280, h=720, x='(ow-iw)/2', y='(oh-ih)/2', color='black')
        )
        
        # Segment 2: The presenter image, looped for the duration of the audio
        presenter_segment = (
            ffmpeg
            .input(presenter_image_path, t=audio_duration, loop=1, framerate=25)
            .filter('scale', '1280', '720')
        )

        # --- Define the single audio input ---
        audio_input = ffmpeg.input(audio_path)

        # --- Concatenate video segments and map the final audio ---
        final_video = (
            ffmpeg
            .concat(chart_segment, presenter_segment, v=1, a=0)
            .output(audio_input.audio, os.path.join(OUTPUT_DIR, output_filename), pix_fmt='yuv420p', shortest=None)
        )

        final_video.run(overwrite_output=True)
        final_path = os.path.join(OUTPUT_DIR, output_filename)
        print(f"Final video composed successfully: {final_path}")
        return final_path
        
    except ffmpeg.Error as e:
        print("FFmpeg error occurred.")
        if e.stderr:
            print("FFmpeg stderr:", e.stderr.decode())
        return None