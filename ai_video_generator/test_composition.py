import os
import re
import numpy as np
from moviepy.editor import *
from scripts.config import ASSETS_DIR, OUTPUT_DIR

def create_luma_mask(frame):
    """
    Creates a brightness-based (luma) mask from a video frame.
    This is effective for separating a subject from a plain white/light background.
    """
    # Convert frame to grayscale using the luminosity method
    # gray_frame = 0.2989 * R + 0.5870 * G + 0.1140 * B
    gray_frame = frame.mean(axis=2)
    
    # Threshold the grayscale image. Pixels with brightness > 200 will be considered
    # background. Adjust this threshold if the mask isn't clean.
    # The result is a 2D array where background is 1 (or 255) and foreground is 0.
    threshold = 200 
    mask = (gray_frame > threshold).astype(np.uint8) * 255
    
    # In MoviePy masks, the area to *keep* is white (255) and the area to
    # *remove* is black (0). We need to invert our mask.
    inverted_mask = 255 - mask
    
    # Return a 3-channel mask for compatibility
    return np.dstack([inverted_mask] * 3)


def test_video_composition():
    """
    A standalone function to test video composition using existing assets.
    """
    print("--- Starting Standalone Video Composition Test ---")

    # --- 1. Define Paths to Your Existing Assets ---
    # NOTE: Update these filenames if yours are different!
    avatar_video_path = os.path.join(ASSETS_DIR, "avatar_video.mp4")
    # Try to find a chart animation file automatically
    chart_files = [f for f in os.listdir(ASSETS_DIR) if f.startswith("chart_animation_") and f.endswith(".mp4")]
    if not chart_files:
        print("ERROR: No 'chart_animation_*.mp4' file found in assets folder. Exiting.")
        return
    chart_path = os.path.join(ASSETS_DIR, chart_files[0])
    background_image_path = os.path.join(ASSETS_DIR, "podcast_background.jpg")
    music_path = os.path.join(ASSETS_DIR, "music.mp3")
    output_path = os.path.join(OUTPUT_DIR, "TEST_COMPOSITION_OUTPUT.mp4")

    # A dummy script text for subtitle generation
    script_text = "Welcome to our analysis. Let's look at the career highlights. The stats show impressive numbers across the board, proving a legendary status in the sport."

    print(f"Using Avatar: {avatar_video_path}")
    print(f"Using Chart: {chart_path}")
    print(f"Using Background: {background_image_path}")

    # --- 2. Load and Process Assets ---
    FINAL_SIZE = (1280, 720)
    CHART_FADE_IN_TIME = 4.0

    avatar_clip = VideoFileClip(avatar_video_path)
    chart_clip = VideoFileClip(chart_path)

    # Background with Ken Burns Effect (slow zoom-in) for a dynamic feel
    background_clip = (ImageClip(background_image_path)
                       .set_duration(avatar_clip.duration)
                       .resize(height=FINAL_SIZE[1])
                       .resize(lambda t: 1 + 0.02 * t) # Zoom in by 2% over the clip's duration
                       .set_position(("center", "center")))
    # Crop the background to the final size after zooming
    background_clip = vfx.crop(background_clip, width=FINAL_SIZE[0], height=FINAL_SIZE[1], x_center=background_clip.w/2, y_center=background_clip.h/2)


    # --- 3. Isolate the Presenter using Luma Mask ---
    # This is the key change to remove the white/watermarked background.
    avatar_mask = avatar_clip.fl_image(create_luma_mask)
    avatar_masked = avatar_clip.set_mask(VideoFileClip(avatar_mask.filename, has_mask=True))
    
    avatar_processed = (avatar_masked
                        .resize(height=int(FINAL_SIZE[1] * 0.9)) # Slightly larger avatar
                        .set_position(("right", "center"))
                        .margin(right=60, opacity=0)
                        .fadein(1.0)) # Smooth fade-in for the avatar

    # Chart processing
    chart_processed = (chart_clip
                       .resize(width=int(FINAL_SIZE[0] * 0.4))
                       .set_position(("left", "center"))
                       .margin(left=60, opacity=0)
                       .set_start(CHART_FADE_IN_TIME)
                       .fadein(1.0))

    # --- 4. Subtitles with Fade-in Effect ---
    sentences = re.split(r'(?<=[.!?])\s+', script_text.strip())
    sentence_clips = []
    current_time = 0
    for sentence in sentences:
        if not sentence: continue
        words = len(sentence.split())
        duration = max(2.0, words / 3.0)
        
        txt_clip = (TextClip(sentence, fontsize=45, color='white', font='Arial-Bold',
                             bg_color='rgba(0,0,0,0.6)', size=(FINAL_SIZE[0] * 0.9, None), method='caption')
                    .set_position(('center', 0.85), relative=True)
                    .set_duration(duration)
                    .set_start(current_time)
                    .fadein(0.5)) # Smooth fade-in for subtitles
        sentence_clips.append(txt_clip)
        current_time += duration

    # --- 5. Compose Audio ---
    voice_audio = avatar_clip.audio
    music_audio = AudioFileClip(music_path).volumex(0.1).set_duration(avatar_clip.duration)
    final_audio = CompositeAudioClip([voice_audio, music_audio])

    # --- 6. Assemble Final Video ---
    final_video = CompositeVideoClip(
        [background_clip, chart_processed, avatar_processed] + sentence_clips,
        size=FINAL_SIZE
    ).set_duration(avatar_clip.duration).set_audio(final_audio)

    # --- 7. Write to File ---
    print(f"Writing final test video to: {output_path}")
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, threads=4)
    print("--- Test composition finished successfully! ---")

if __name__ == "__main__":
    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    test_video_composition()