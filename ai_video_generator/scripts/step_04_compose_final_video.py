import os
import re
from moviepy.editor import *

ASSETS_DIR = "assets"
OUTPUT_DIR = "output"

def compose_final_video(chart_path: str, avatar_video_path: str, script_text: str, output_filename: str) -> str:
    print("Composing final video with MoviePy...")
    music_path = os.path.join(ASSETS_DIR, "music.mp3")
    if not os.path.exists(music_path):
        print("Error: music.mp3 not found in assets folder.")
        return None
    if chart_path.endswith('.mp4'):
        chart_clip = VideoFileClip(chart_path).set_duration(5).resize(width=1280)
    else:
        chart_clip = ImageClip(chart_path).set_duration(5).resize(width=1280)
    presenter_clip = VideoFileClip(avatar_video_path).resize(height=720)
    sentences = re.split(r'(?<=[.!?])\s+', script_text)
    sentence_clips = []
    current_time = 0
    for sentence in sentences:
        if not sentence:
            continue
        words = len(sentence.split())
        duration = max(2.0, words / 3.0)
        txt_clip = (TextClip(sentence, fontsize=45, color='white', font='Arial-Bold',
                             bg_color='rgba(0,0,0,0.5)', size=(chart_clip.w * 0.8, None))
                    .set_position(('center', 0.8), relative=True)
                    .set_duration(duration)
                    .set_start(current_time))
        sentence_clips.append(txt_clip)
        current_time += duration
    presenter_with_text = CompositeVideoClip([presenter_clip] + sentence_clips)
    final_video_no_audio = concatenate_videoclips([chart_clip, presenter_with_text], method="compose")
    voice_audio = presenter_clip.audio.set_start(chart_clip.duration)
    music_audio = AudioFileClip(music_path).volumex(0.15)
    final_audio = CompositeAudioClip([voice_audio, music_audio]).set_duration(final_video_no_audio.duration)
    final_video = final_video_no_audio.set_audio(final_audio)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
    print(f"Final video composed successfully with MoviePy: {output_path}")
    return output_path