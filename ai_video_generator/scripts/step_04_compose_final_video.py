# scripts/step_04_compose_final_video.py (Corrected Version)
import ffmpeg
import requests
import os

ASSETS_DIR = "assets"
OUTPUT_DIR = "output"

def download_video(url: str, filename: str) -> str:
    """Downloads a file from a URL to a local path."""
    print(f"Downloading video from {url}...")
    local_path = os.path.join(ASSETS_DIR, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Video downloaded to {local_path}")
    return local_path

def compose_final_video(avatar_video_url: str, chart_image_path: str, output_filename: str) -> str:
    """
    Composes the final video by sequencing the chart image and the avatar video.
    """
    print("Composing final video...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    avatar_video_path = download_video(avatar_video_url, "avatar_video.mp4")
    
    # Define inputs for FFmpeg
    avatar_input = ffmpeg.input(avatar_video_path)
    
    # --- FIX: Scale the chart image to match the video resolution (1280x720) ---
    # We also add a black background in case the aspect ratio differs, preventing stretching.
    chart_input = (
        ffmpeg
        .input(chart_image_path, t=5, loop=1, framerate=25)
        .filter('scale', size='1280:720', force_original_aspect_ratio='decrease')
        .filter('pad', w=1280, h=720, x='(ow-iw)/2', y='(oh-ih)/2', color='black')
    )

    # Concatenate the scaled chart video and the avatar video
    final_video = ffmpeg.concat(chart_input, avatar_input, v=1, a=0).output(
        avatar_input.audio,
        os.path.join(OUTPUT_DIR, output_filename),
        pix_fmt='yuv420p'
    )
    
    try:
        final_video.run(overwrite_output=True)
        final_path = os.path.join(OUTPUT_DIR, output_filename)
        print(f"Final video composed successfully: {final_path}")
        return final_path
    except ffmpeg.Error as e:
        # --- FIX: More robust error printing ---
        print("FFmpeg error occurred.")
        # The error details are often in stdout for filter initialization errors
        if e.stdout:
            print("FFmpeg stdout:", e.stdout.decode())
        if e.stderr:
            print("FFmpeg stderr:", e.stderr.decode())
        return None

if __name__ == '__main__':
    TEST_VIDEO_URL = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    TEST_CHART_PATH = "assets/Test_Player_stats.png"
    
    if not os.path.exists(TEST_CHART_PATH):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Test Chart', ha='center', va='center')
        plt.savefig(TEST_CHART_PATH)
        plt.close()
        
    compose_final_video(TEST_VIDEO_URL, TEST_CHART_PATH, "final_video.mp4")