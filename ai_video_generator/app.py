# ai_video_generator/app.py
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import run_pipeline

app = Flask(__name__)
app.config["OUTPUT_FOLDER"] = "output"
app.config["UPLOAD_FOLDER"] = "assets"
app.config["ALLOWED_EXTENSIONS"] = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    player_id = request.form.get("player_id")
    match_id = request.form.get("match_id")
    tone = request.form.get("tone", "energetic")
    if not player_id:
        return "Error: Please provide a Player ID.", 400

    # Handle presenter image upload
    if 'presenter' in request.files:
        file = request.files['presenter']
        if file and allowed_file(file.filename):
            filename = "presenter.jpg"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            print(f"Uploaded presenter image to: {os.path.join(app.config['UPLOAD_FOLDER'], filename)}")

    try:
        # Try running pipeline with match_id, fall back to career stats if 404
        try:
            video_path = run_pipeline(
                int(player_id),
                match_id=int(match_id) if match_id else None,
                tone=tone
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 and match_id:
                print(f"Match ID {match_id} not found, falling back to career stats.")
                video_path = run_pipeline(int(player_id), match_id=None, tone=tone)
            else:
                raise e

        if video_path:
            return redirect(url_for("serve_video", filename=os.path.basename(video_path)))
        else:
            return "Error: Pipeline failed to generate video.", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500

@app.route("/output/<filename>")
def serve_video(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True, port=5001)