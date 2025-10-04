# main.py (Corrected Version)
import time
from scripts.step_01_generate_script import generate_commentary_script
from scripts.step_02_create_visuals import create_player_stat_chart
from scripts.step_03_generate_avatar_video import generate_avatar_video
from scripts.step_04_compose_final_video import compose_final_video

def run_pipeline(player_id: int):
    """
    Executes the full video generation pipeline for a given player ID.
    """
    print(f"--- STARTING VIDEO GENERATION PIPELINE FOR PLAYER ID: {player_id} ---")
    start_time = time.time()
    
    # --- Step 1: Generate commentary script ---
    script = generate_commentary_script(player_id)
    if not script:
        print("Pipeline failed at Step 1: Script Generation.")
        return
    print("\n--- SCRIPT ---")
    print(script)
    print("-" * 15)
    
    # --- Step 2: Create statistics visual ---
    chart_path = create_player_stat_chart(player_id)
    if not chart_path:
        print("Pipeline failed at Step 2: Visual Generation.")
        return
    
    # --- Step 3: Generate AI avatar video ---
    # NOTE: This step is a placeholder and will likely fail without a real API key
    # and correct endpoint configuration. Replace with a real URL for testing.
    # avatar_video_url = generate_avatar_video(script)
    # Using a placeholder URL for demonstration:
    avatar_video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
    print(f"\nUsing placeholder video URL for demonstration: {avatar_video_url}")

    if not avatar_video_url:
        print("Pipeline failed at Step 3: Avatar Video Generation.")
        return

    # --- Step 4: Compose the final video ---
    final_video_path = compose_final_video(avatar_video_url, chart_path, f"player_{player_id}_commentary.mp4")
    if not final_video_path:
        print("Pipeline failed at Step 4: Final Video Composition.")
        return
        
    end_time = time.time()
    print(f"\n--- PIPELINE COMPLETED SUCCESSFULLY IN {end_time - start_time:.2f} SECONDS ---")
    print(f"Find your final video at: {final_video_path}")


if __name__ == "__main__":
    # Specify the ID of the player you want to generate a video for
    TARGET_PLAYER_ID = 2  # Example: Use player ID 2
    
    run_pipeline(TARGET_PLAYER_ID)
