# Scripttt

Scripttt is a Python web application that enables content creators to repurpose long-form video content into concise, engaging scripts for short-form platforms such as Instagram Reels and YouTube Shorts. Built with Gradio, Scripttt combines state-of-the-art transcription, speaker diarization, and script generation to deliver production-ready outputs that reflect the tone and style of the original conversation.

[![Open in Hugging Face Spaces](https://img.shields.io/badge/Open%20in-Hugging%20Face%20Spaces-blue?logo=huggingface&logoColor=white)](https://vanshikaa11-scripttt.hf.space)

## Features

- **Video File Uploads Only**  
  Accepts direct uploads of video files (`.mp4`, `.mkv`, and other common formats). Audio-only files and external links are not supported.

- **Accurate Transcription**  
  Utilizes OpenAI Whisper for high-quality speech-to-text conversion.

- **Speaker Diarization**  
  Employs pyannote.audio to automatically identify and label speakers within the transcript.

- **Speaker-Tagged Transcript**  
  Generates a clean, speaker-attributed transcript of the input video.

- **Short-Form Script Generation**  
  Produces a concise, human-like script optimized for viral, short-form video content.

- **Privacy by Design**  
  All processing occurs locally; no external URLs or remote media are accepted.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/scripttt.git
   cd scripttt
   ```

2. **Set Up a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Create a `.env` file in the project root.
   - Add your Hugging Face and Google API credentials as environment variables.  
     Example:
     ```
     HUGGINGFACE_TOKEN=your_huggingface_token
     GOOGLE_API_KEY=your_google_api_key
     ```

## Usage

1. **Run the Application**
   ```bash
   python app.py
   ```

2. **Access the Interface**
   - Open the local URL provided by Gradio in your browser.
   - Upload a supported video file and follow the on-screen instructions.

## Output

- **Speaker-Tagged Transcript:**  
  A clean, readable transcript with speaker labels.

- **Short-Form Script:**  
  A new, concise script based on the original video, ready for use in short-form content production.

