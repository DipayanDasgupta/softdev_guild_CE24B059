import sys
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# Add the parent directory ('ai_video_generator') to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_pipeline
from scripts.config import OUTPUT_DIR, ASSETS_DIR

app = Flask(__name__)
app.config['OUTPUT_FOLDER'] = OUTPUT_DIR
app.config['ASSETS_FOLDER'] = ASSETS_DIR
app.secret_key = "your-secret-key"  # Replace with a secure key for production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    player_id = request.form.get('player_id')
    match_id_str = request.form.get('match_id')
    tone = request.form.get('tone', 'energetic')  # Default to 'energetic' if not provided
    image_file = request.files.get('presenter_image')

    if not player_id:
        flash("Error: Player ID is required.", "error")
        return redirect(url_for('index'))

    custom_presenter = None
    if image_file and image_file.filename:
        # Validate file extension
        valid_extensions = {'.jpg', '.jpeg', '.png'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in valid_extensions:
            flash("Invalid image format. Please upload a JPEG or PNG file.", "error")
            return redirect(url_for('index'))
        # Securely save the uploaded file to the assets directory
        filename = secure_filename(image_file.filename)
        save_path = os.path.join(app.config['ASSETS_FOLDER'], filename)
        try:
            image_file.save(save_path)
            custom_presenter = filename
            print(f"Custom presenter '{custom_presenter}' saved to {save_path}")
        except Exception as e:
            flash(f"Error saving image: {str(e)}", "error")
            return redirect(url_for('index'))

    try:
        player_id_int = int(player_id)
        if player_id_int <= 0:
            raise ValueError("Player ID must be a positive integer.")
        match_id_int = int(match_id_str) if match_id_str else None
        if match_id_int is not None and match_id_int <= 0:
            raise ValueError("Match ID must be a positive integer.")
    except ValueError as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('index'))

    final_video_path = run_pipeline(
        player_id=player_id_int, 
        match_id=match_id_int, 
        tone=tone,
        custom_presenter_filename=custom_presenter
    )

    if final_video_path:
        video_filename = os.path.basename(final_video_path)
        return redirect(url_for('result', filename=video_filename))
    else:
        flash("Error: Video generation failed. Check console for logs.", "error")
        return redirect(url_for('index'))

@app.route('/result/<filename>')
def result(filename):
    video_url = url_for('serve_video', filename=filename)
    return render_template('result.html', video_url=video_url)

@app.route('/output/<filename>')
def serve_video(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ASSETS_FOLDER'], exist_ok=True)
    print("Starting Flask server...")
    print("Ensure the IPL API is running on http://127.0.0.1:8000")
    app.run(debug=True, port=5001)