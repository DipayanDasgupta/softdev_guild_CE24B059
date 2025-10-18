# ai_video_generator/scripts/config.py
import os

# This gets the absolute path of the directory containing this config file (the 'scripts' directory)
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# This goes one level up to get the main 'ai_video_generator' project directory
BASE_DIR = os.path.dirname(_SCRIPTS_DIR)

# Define all other paths based on this absolute BASE_DIR
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
API_BASE_URL = "http://127.0.0.1:8000"