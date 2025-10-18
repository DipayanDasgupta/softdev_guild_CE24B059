# ai_video_generator/flask_app/app.py
import sys
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_pipeline
from scripts.config import OUTPUT_DIR, ASSETS_DIR

app = Flask(__name__)
app.config['OUTPUT_FOLDER'] = OUTPUT_DIR
app.config['ASSETS_FOLDER'] = ASSETS_DIR
app.secret_key = "your-secret-key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # --- NEW LOGIC: Correctly handle the two user paths from the form ---
    player_id_match = request.form.get('player_id')
    player_id_career = request.form.get('player_id_career')
    
    # Prioritize the "match performance" path if a player is selected there
    if player_id_match:
        player_id = player_id_match
        match_id = request.form.get('match_id')
    # Otherwise, use the "career search" path
    else:
        player_id = player_id_career
        match_id = None
        
    tone = request.form.get('tone', 'energetic')
    image_file = request.files.get('presenter_image')

    if not player_id:
        flash("Error: No player selected. Please choose a player from one of the sections.", "error")
        return redirect(url_for('index'))

    custom_presenter = None
    if image_file and image_file.filename:
        valid_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in valid_extensions:
            flash("Invalid image format. Please upload a JPEG or PNG file.", "error")
            return redirect(url_for('index'))
        filename = secure_filename(image_file.filename)
        save_path = os.path.join(app.config['ASSETS_FOLDER'], filename)
        try:
            image_file.save(save_path)
            custom_presenter = filename
        except Exception as e:
            flash(f"Error saving image: {str(e)}", "error")
            return redirect(url_for('index'))

    try:
        player_id_int = int(player_id)
        match_id_int = int(match_id) if match_id else None
    except (ValueError, TypeError):
        flash("Error: Invalid Player ID or Match ID.", "error")
        return redirect(url_for('index'))

    # Call the main pipeline with the correctly determined IDs
    final_video_path = run_pipeline(
        player_id=player_id_int, 
        match_id=match_id_int, # <-- FIX: Corrected parameter name
        tone=tone,
        custom_presenter_filename=custom_presenter
    )

    if final_video_path:
        video_filename = os.path.basename(final_video_path)
        return redirect(url_for('result', filename=video_filename))
    else:
        flash("Error: Video generation failed. Check the console for logs.", "error")
        return redirect(url_for('index'))

@app.route('/result/<filename>')
def result(filename):
    video_url = url_for('serve_video', filename=filename)
    return render_template('result.html', video_url=video_url)

@app.route('/output/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ASSETS_FOLDER'], exist_ok=True)
    print("Starting Flask server...")
    print("Ensure the IPL API is running on http://127.0.0.1:8000")
    app.run(debug=True, port=5001)