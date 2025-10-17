# main.py
import time
from scripts.step_01_generate_script import generate_commentary_script
from scripts.step_02_create_visuals import create_player_stat_chart
from scripts.step_03b_generate_avatar_video import generate_avatar_video
from scripts.step_04_compose_final_video import compose_final_video

def run_pipeline(player_id: int):
    """
    Executes the full video generation pipeline using D-ID's built-in TTS.
    """
    print(f"--- STARTING FINAL AI VIDEO PIPELINE FOR PLAYER ID: {player_id} ---")
    start_time = time.time()
    
    # Step 1: Generate commentary script
    script = generate_commentary_script(player_id)
    if not script:
        print("Pipeline failed at Step 1: Script Generation.")
        return

    # Step 2: Create static chart image
    chart_image_path = create_player_stat_chart(player_id)
    if not chart_image_path:
        print("Pipeline failed at Step 2: Visual Generation.")
        return
    
    # Step 3: Generate the D-ID avatar video using the script text
    avatar_video_path = generate_avatar_video(script)
    if not avatar_video_path:
        print("Pipeline failed at Step 3b: Avatar Video Generation.")
        return

    # Step 4: Compose final video with chart, avatar, and text overlays
    final_video_path = compose_final_video(chart_image_path, avatar_video_path, script, f"player_{player_id}_commentary.mp4")
    if not final_video_path:
        print("Pipeline failed at Step 4: Final Video Composition.")
        return
        
    end_time = time.time()
    print(f"\n--- PIPELINE COMPLETED SUCCESSFULLY IN {end_time - start_time:.2f} SECONDS ---")
    print(f"Find your final video at: {final_video_path}")

if __name__ == "__main__":
    TARGET_PLAYER_ID = 2
    run_pipeline(TARGET_PLAYER_ID)