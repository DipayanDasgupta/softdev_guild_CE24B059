
# AI Cricket Commentary Video Generator

This project is a full-stack AI application that automatically generates professional, broadcast-quality video segments analyzing cricket player performances. Using a web interface, users can select a player and a specific match or their entire career, and the pipeline will generate a complete video with an AI presenter, animated statistics, and analytical commentary.

 <!-- You can replace this with a screenshot of your final video output -->

## Key Features

*   **Dynamic Web Interface:** An intuitive frontend built with Flask allows users to select a player through two distinct paths:
    *   **Match Performance:** Cascading dropdowns to select Year, Match, and Player for a deep dive into a specific performance.
    *   **Career Summary:** A search bar to find any player and generate a video about their overall career statistics.
*   **Intelligent Script Generation:** Utilizes Google's Gemini AI to generate engaging and analytical commentary. For match-specific videos, a custom analysis module provides deeper insights (e.g., top scorer, scoring pace) that are woven into the script.
*   **AI-Powered Presenter:** Integrates with D-ID's API to create a lip-synced video of a presenter (either default or a custom user-uploaded image) speaking the generated script.
*   **High-Quality Voice Cloning:** Prioritizes ElevenLabs for generating realistic, high-quality audio, with a fallback to D-ID's built-in TTS.
*   **Automated Visuals & Composition:**
    *   Generates animated bar charts of player statistics using Playwright.
    *   Uses **AI background removal** (`rembg`) to perfectly isolate the presenter from their original background.
    *   Composes the final video in a professional podcast/news layout using MoviePy, layering the background, presenter, and animated charts.
*   **RESTful Data API:** A separate FastAPI backend serves all the cricket data, sourced from a local SQLite database.

## Tech Stack

*   **AI Video Generation (`ai_video_generator/`)**
    *   **Web Framework:** Flask
    *   **Video Composition:** MoviePy
    *   **AI Presenter:** D-ID API
    *   **AI Scripting:** Google Gemini API
    *   **AI Audio:** ElevenLabs API
    *   **Visuals Automation:** Playwright
    *   **AI Background Removal:** `rembg` & `onnxruntime`
*   **Data API (`ipl-api/`)**
    *   **Web Framework:** FastAPI
    *   **Database:** SQLite
    *   **ORM:** SQLAlchemy
*   **Frontend**
    *   **Markup/Styling:** HTML5, CSS3
    *   **Interactivity:** Vanilla JavaScript

## Project Structure

```
.
├── ai_video_generator/
│   ├── flask_app/         # Flask web server and templates
│   ├── assets/            # Static files: images, music, video components
│   ├── output/            # Where final rendered videos are saved
│   ├── scripts/           # Core Python scripts for each step of the pipeline
│   │   ├── step_01_generate_script.py
│   │   ├── step_02_create_visuals.py
│   │   ├── step_03_generate_audio.py
│   │   ├── step_03b_generate_avatar_video.py
│   │   ├── step_04_compose_final_video.py
│   │   ├── perform_analysis.py  # New analysis module
│   │   └── video_utils.py       # AI background removal utility
│   └── main.py              # Main orchestrator for the video pipeline
│
├── ipl-api/
│   ├── data/              # Raw data files (JSON)
│   ├── api.py               # FastAPI application
│   ├── ingest.py            # Script to populate the database (run once)
│   └── ipl_data.db        # SQLite database file
│
├── .env                   # Local environment variables (you must create this)
└── README.md
```

## Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

*   Git
*   Python 3.10+
*   A virtual environment manager (like `venv`)

### 1. Clone the Repository

```bash
git clone https://github.com/DipayanDasgupta/softdev_guild_CE24B059.git 
cd softdev_guild_CE24B059
```

### 2. Set Up Environment Variables

This is a critical step. The project requires API keys for several AI services.

1.  Create a file named `.env` in the **root directory** of the project.
2.  Copy the content of `.env.example` below into your new `.env` file.
3.  Replace the placeholder values with your actual API keys.

**.env.example**
```env
# Get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Get from https://elevenlabs.io/
ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY"

# Get from https://www.d-id.com/
# Format is "user:password" which you get from the API key section
D_ID_API_KEY="YOUR_D-ID_USERNAME:YOUR_D-ID_PASSWORD"
```

### 3. Set Up and Run the IPL Data API

This service provides the cricket data to the entire application.

1.  **Open your first terminal window.**
2.  Navigate to the API directory:
    ```bash
    cd ipl-api
    ```
3.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Important:** Populate the database. This is a **one-time step** that reads the JSON data and creates the `ipl_data.db` file.
    ```bash
    python ingest.py
    ```
6.  Run the FastAPI server:
    ```bash
    uvicorn api:app --reload
    ```
    The API should now be running at `http://127.0.0.1:8000`. Keep this terminal running.

### 4. Set Up and Run the AI Video Generator App

This is the main application that serves the frontend and runs the video creation pipeline.

1.  **Open a second, new terminal window.** (Do not close the API terminal).
2.  Navigate to the AI video generator directory from the project root:
    ```bash
    cd ai_video_generator
    ```
3.  Create and activate a separate virtual environment for this part of the project:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  Install its dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run the Flask web application:
    ```bash
    python flask_app/app.py
    ```
    The web app should now be running.

## How to Use the Application

1.  Open your web browser and navigate to **`http://127.0.0.1:5001`**.
2.  You have two options to generate a video:
    *   **Select by Match Performance**:
        1.  Use the "Select Year" dropdown.
        2.  Once a year is chosen, the "Select Match" dropdown will populate. Choose a match.
        3.  The "Select Player" dropdown will then show all players who batted in that match, grouped by team. Select one.
    *   **Search by Player Career**:
        1.  Ignore the dropdowns above.
        2.  Type a player's name in the search box. A list of matching players will appear.
        3.  Click on a player to select them. This will generate a video about their career highlights.
3.  (Optional) Choose a commentary tone.
4.  (Optional) Upload a custom presenter image (must be a clear, forward-facing portrait).
5.  Click **"Generate Video"**.
6.  Be patient! The process can take several minutes, as it involves multiple API calls, AI processing, and video rendering.
7.  Once complete, you will be redirected to a results page where you can watch and download your video.

## Future Improvements

*   **Include Bowling Stats:** Expand the data models and analysis to generate videos about bowler performances.
*   **Visual Variety:** Create multiple video composition templates (e.g., different layouts, backgrounds, transitions).
*   **Advanced Animations:** Use a tool like Remotion or After Effects for more complex and dynamic data visualizations.
*   **Cloud Deployment:** Containerize the applications with Docker and deploy them to a cloud service for public access.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.