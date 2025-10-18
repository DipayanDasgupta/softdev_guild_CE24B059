# ai_video_generator/scripts/step_04_compose_final_video.py
import os
import re
from moviepy.editor import *
from moviepy.video.fx.all import mask_color

from .config import ASSETS_DIR, OUTPUT_DIR

# --- V2 Goal Implemented: Create a dynamic, layered 'podcast' style video ---

def compose_final_video(chart_path: str, avatar_video_path: str, script_text: str, output_filename: str) -> str:
    print("Composing final professional video with MoviePy...")
    
    # --- 1. Load all video and audio assets ---
    
    # Background Image: A static image that will be the base layer.
    background_image_path = os.path.join(ASSETS_DIR, "podcast_background.jpg")
    if not os.path.exists(background_image_path):
        print(f"Error: Background image not found at {background_image_path}")
        return None

    # Avatar Video: The lip-synced video from D-ID.
    # We assume it has a green screen background because we used "stitch": True.
    avatar_clip = VideoFileClip(avatar_video_path)
    
    # Chart Video: The animated stats chart.
    chart_clip = VideoFileClip(chart_path)

    # Background Music
    music_path = os.path.join(ASSETS_DIR, "music.mp3")
    if not os.path.exists(music_path):
        print("Warning: music.mp3 not found, proceeding without background music.")
        music_audio = None
    else:
        music_audio = AudioFileClip(music_path).volumex(0.1) # Reduced volume for professional feel
        
    # --- 2. Define video properties and layout ---
    
    FINAL_SIZE = (1280, 720)
    CHART_FADE_IN_TIME = 4.0 # Time in seconds when the chart starts to appear
    
    # Set the background clip's duration to match the main avatar video
    background_clip = ImageClip(background_image_path).set_duration(avatar_clip.duration).resize(FINAL_SIZE)
    
    # --- 3. Process and position the layers ---
    
    # Avatar processing:
    # - Remove the green screen background from the D-ID video.
    #   Note: You may need to adjust the color=[0,255,0] if D-ID uses a different key color.
    # - Resize and position the avatar on the right side.
    avatar_processed = (
        avatar_clip.fx(mask_color, color=[0, 255, 0], thr=120, s=5)
        .resize(height=int(FINAL_SIZE[1] * 0.85)) # Make avatar 85% of video height
        .set_position(("right", "center"))
        .margin(right=50, opacity=0) # Add 50px padding from the right edge
    )

    # Chart processing:
    # - Resize and position the chart on the left side.
    # - Set its start time to appear mid-conversation and fade it in.
    chart_processed = (
        chart_clip.resize(width=int(FINAL_SIZE[0] * 0.4)) # Make chart 40% of video width
        .set_position(("left", "center"))
        .margin(left=50, opacity=0) # Add 50px padding from the left edge
        .set_start(CHART_FADE_IN_TIME)
        .fadein(1.0) # Fade in over 1 second
    )
    
    # --- 4. Create dynamic text overlays (subtitles) ---
    
    sentences = re.split(r'(?<=[.!?])\s+', script_text.strip())
    sentence_clips = []
    current_time = 0
    for sentence in sentences:
        if not sentence: continue
        words = len(sentence.split())
        duration = max(2.0, words / 3.0) # Estimate duration based on word count
        
        txt_clip = (
            TextClip(
                sentence, 
                fontsize=45, 
                color='white', 
                font='Arial-Bold',
                bg_color='rgba(0,0,0,0.6)', 
                size=(FINAL_SIZE[0] * 0.9, None), # 90% width
                method='caption'
            )
            .set_position(('center', 0.85), relative=True)
            .set_duration(duration)
            .set_start(current_time)
        )
        sentence_clips.append(txt_clip)
        current_time += duration
        
    # --- 5. Compose audio tracks ---
    
    # The primary voice audio comes directly from the avatar clip
    voice_audio = avatar_clip.audio
    
    final_audio_clips = [voice_audio]
    if music_audio:
        # Ensure music plays for the entire duration of the video
        final_audio_clips.append(music_audio.set_duration(avatar_clip.duration))
        
    final_audio = CompositeAudioClip(final_audio_clips)

    # --- 6. Assemble the final video ---
    
    # Layer everything together. Order matters: bottom layer first.
    final_video = CompositeVideoClip(
        [background_clip, avatar_processed, chart_processed] + sentence_clips,
        size=FINAL_SIZE
    ).set_duration(avatar_clip.duration)
    
    # Set the combined audio to the final video
    final_video = final_video.set_audio(final_audio)

    # Write the final output file
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    try:
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, threads=4)
        print(f"Final video composed successfully: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error writing final video file: {e}")
        return None