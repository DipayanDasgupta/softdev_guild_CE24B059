# ai_video_generator/main.py
import time
import os
from scripts.step_01_generate_script import generate_commentary_script
from scripts.step_02_create_visuals import create_player_stat_chart
from scripts.step_03_generate_audio import generate_audio
from scripts.step_03b_generate_avatar_video import generate_avatar_video
from scripts.step_04_compose_final_video import compose_final_video
from scripts.config import ASSETS_DIR # Import config to get audio path

def run_pipeline(player_id: int, match_id: int = None, tone: str = "energetic", custom_presenter_filename: str = None) -> str:
    """
    Runs the full AI video pipeline for a given player and optional match.
    """
    print(f"--- STARTING V2 AI VIDEO PIPELINE FOR PLAYER ID: {player_id}, MATCH ID: {match_id}, TONE: {tone}, CUSTOM PRESENTER: {custom_presenter_filename or 'default'} ---")
    start_time = time.time()
    
    # Step 1: Generate commentary script
    script = generate_commentary_script(player_id, match_id, tone)
    if not script:
        print("Pipeline failed at Step 1: Script Generation.")
        return None
    
    # Step 2: Generate audio using ElevenLabs (high-quality)
    # The path will be used in step 4. If it fails, audio_path will be None.
    audio_path = generate_audio(script)
    # Note: We no longer fail the pipeline if audio generation fails,
    # as step_03b now has a fallback mechanism.
    
    # Step 3: Create animated chart video
    chart_path = create_player_stat_chart(player_id, match_id)
    if not chart_path:
        print("Pipeline failed at Step 2: Visual Generation.")
        return None
    
    # Step 4: Generate avatar video
    # --- MODIFICATION: Pass the generated audio_path to the avatar function ---
    avatar_video_path = generate_avatar_video(
        script_text=script, 
        audio_path=audio_path, # This is the crucial change
        custom_presenter_filename=custom_presenter_filename
    )
    if not avatar_video_path:
        print("Pipeline failed at Step 3b: Avatar Video Generation.")
        return None

    # Step 5: Compose final professional video
    output_filename = f"player_{player_id}_{match_id or 'career'}_commentary.mp4"
    final_video_path = compose_final_video(chart_path, avatar_video_path, script, output_filename)
    if not final_video_path:
        print("Pipeline failed at Step 4: Final Video Composition.")
        return None
    
    end_time = time.time()
    print(f"\n--- PIPELINE COMPLETED SUCCESSFULLY IN {end_time - start_time:.2f} SECONDS ---")
    print(f"Find your final video at: {final_video_path}")
    return final_video_path

if __name__ == "__main__":
    # Example usage:
    # Ensure you have 'podcast_background.jpg' in your assets folder.
    run_pipeline(player_id=139) # Example: Brendon McCullum