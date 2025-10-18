import time
from scripts.step_01_generate_script import generate_commentary_script
from scripts.step_02_create_visuals import create_player_stat_chart
from scripts.step_03_generate_audio import generate_audio
from scripts.step_03b_generate_avatar_video import generate_avatar_video
from scripts.step_04_compose_final_video import compose_final_video

def run_pipeline(player_id: int, match_id: int = None, tone: str = "energetic", custom_presenter_filename: str = None) -> str:
    """
    Runs the full AI video pipeline for a given player and optional match.
    """
    print(f"--- STARTING AI VIDEO PIPELINE FOR PLAYER ID: {player_id}, MATCH ID: {match_id}, TONE: {tone}, CUSTOM PRESENTER: {custom_presenter_filename or 'default'} ---")
    start_time = time.time()
    
    # Step 1: Generate commentary script
    script = generate_commentary_script(player_id, match_id, tone)
    if not script:
        print("Pipeline failed at Step 1: Script Generation.")
        return None
    
    # Step 2: Generate audio
    audio_path = generate_audio(script)
    if not audio_path:
        print("Pipeline failed at Step 3: Audio Generation.")
        return None
    
    # Step 3: Create animated chart video
    chart_path = create_player_stat_chart(player_id, match_id)
    if not chart_path:
        print("Pipeline failed at Step 2: Visual Generation.")
        return None
    
    # Step 4: Generate avatar video with custom presenter
    avatar_video_path = generate_avatar_video(script, custom_presenter_filename=custom_presenter_filename)
    if not avatar_video_path:
        print("Pipeline failed at Step 3b: Avatar Video Generation.")
        return None

    # Step 5: Compose final video
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
    run_pipeline(player_id=2)