# AI Cricket Commentary Video Generator

This project contains two main components that work together to automatically generate AI-powered video commentary for IPL players.

## 1. IPL Data Scraper & API (`ipl-api/`)

A FastAPI application that scrapes, cleans, and serves IPL match and player statistics from JSON files.

- **Tech Stack:** Python, FastAPI, SQLAlchemy, SQLite.
- **Functionality:** Provides RESTful API endpoints to query player career stats, team information, and match data.
- **Setup:**
  ```bash
  # Navigate to the API directory
  cd ipl-api

  # Install dependencies
  pip install -r requirements.txt
  
  # Create the database and populate it with data from the JSON files
  python ingest.py
  
  # Run the live API server
  uvicorn api:app --reload
  ```

## 2. AI Avatar Video Generation System (`ai_video_generator/`)

A Python-based pipeline that consumes the IPL Data API to generate dynamic commentary videos.

- **Tech Stack:** Python, Google Gemini API, FFmpeg, Matplotlib, Requests.
- **Pipeline Steps:**
  1.  Fetches player stats from the running IPL API.
  2.  Uses the Gemini API to generate a dynamic, engaging commentary script based on the stats.
  3.  Creates a visual bar chart of the player's key statistics using Matplotlib.
  4.  Downloads a placeholder avatar video.
  5.  Composes the final video using FFmpeg, combining the chart and avatar video into a single MP4 file.

- **Setup:**
  ```bash
  # Navigate to the video generator directory
  cd ai_video_generator

  # Install dependencies
  pip install -r requirements.txt
  
  # Create a .env file and add your GEMINI_API_KEY
  echo "GEMINI_API_KEY='YOUR_API_KEY'" > .env
  
  # Run the full pipeline
  python main.py
  ```

