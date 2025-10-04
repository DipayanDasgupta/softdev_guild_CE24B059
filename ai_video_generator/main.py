# main.py
import time
from scripts.step_01_generate_script import generate_commentary_script
from scripts.step_02_create_visuals import create_player_stat_chart
from scripts.step_03_generate_audio import generate_audio
from scripts.step_04_compose_final_video import compose_final_video

def run_pipeline(player_id: int):
    """
    Executes the full video generation pipeline for a given player ID.
    """
    print(f"--- STARTING AI VIDEO PIPELINE FOR PLAYER ID: {player_id} ---")
    start_time = time.time()
    
    # Step 1: Generate commentary script
    script = generate_commentary_script(player_id)
    if not script:
        print("Pipeline failed at Step 1: Script Generation.")
        return

    # Step 2: Create statistics visual
    chart_path = create_player_stat_chart(player_id)
    if not chart_path:
        print("Pipeline failed at Step 2: Visual Generation.")
        return
    
    # --- CHANGE: Generate a real AI audio file ---
    audio_path = generate_audio(script)
    if not audio_path:
        print("Pipeline failed at Step 3: Audio Generation.")
        return

    # --- CHANGE: Compose the final video using the new components ---
    final_video_path = compose_final_video(audio_path, chart_path, f"player_{player_id}_commentary.mp4")
    if not final_video_path:
        print("Pipeline failed at Step 4: Final Video Composition.")
        return
        
    end_time = time.time()
    print(f"\n--- PIPELINE COMPLETED SUCCESSFULLY IN {end_time - start_time:.2f} SECONDS ---")
    print(f"Find your final video at: {final_video_path}")


if __name__ == "__main__":
    TARGET_PLAYER_ID = 2
    run_pipeline(TARGET_PLAYER_ID)