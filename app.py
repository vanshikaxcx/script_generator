import streamlit as st
import os
import ssl
import whisper
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

st.title("🎬 Viral Script Generator")

# Warn if Gemini API key is missing
if not api_key:
    st.warning("⚠️ Gemini API key not found! Please set GOOGLE_API_KEY in your .env file.")
else:
    genai.configure(api_key=api_key)

# SSL fix for Whisper model download
ssl._create_default_https_context = ssl._create_unverified_context

# Load Whisper model (cache for performance)
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# Upload video
uploaded_file = st.file_uploader("📁 Upload a video", type=["mp4", "mov", "mkv"])

if uploaded_file:
    temp_video_path = "temp_video.mp4"
    audio_path = "audio.wav"
    try:
        # Save uploaded video
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.read())
        st.video(temp_video_path)

        # 🔄 Extract audio using ffmpeg
        st.write("🎧 Extracting audio...")
        with st.spinner("Extracting audio from video..."):
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-i", temp_video_path, "-q:a", "0", "-map", "a", audio_path, "-y"
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                st.error("❌ ffmpeg is not installed or not found in the system PATH. Please ensure ffmpeg is available.")
                st.stop()
            except subprocess.CalledProcessError:
                st.error("❌ Audio extraction failed. Please upload a valid video file.")
                st.stop()

        # 📝 Transcribe using Whisper
        st.write("📝 Transcribing with Whisper...")
        with st.spinner("Transcribing audio..."):
            try:
                result = whisper_model.transcribe(audio_path, fp16=False)  # Suppress FP16 warning
                transcript = result["text"]
            except Exception as e:
                st.error(f"❌ Whisper transcription failed: {str(e)}")
                st.stop()

        st.success("✅ Transcription complete")
        st.text_area("📄 Transcript:", transcript, height=150)

        # 🤖 Generate new script using Gemini
        st.write("🧠 Generating fresh, viral-ready script...")

        prompt = f"""
        You're a creative director and viral scriptwriter for Gen-Z Instagram Reels in the Indian subcontinent.

        Your job is to transform the transcript below into a **completely new, reimagined video script** that:

        - Keeps the **emotional vibe, tone, and intent** of the original
        - Tells a **visually and narratively different story** (NO reuse of plot, characters, or locations)
        - Is designed for a **40–45 second Instagram Reel** (tight, crisp, scroll-stopping)
        - Sounds **authentic and unscripted** — like something an actual creator would say
        - Uses **chaotic desi relatability**, funny breakdowns, street moments, sarcastic voiceovers, or quirky interruptions
        - Includes a **strong hook in the first 5 seconds** that makes people stop scrolling
        - Ends with a **high-impact, funny, or emotional CTA** that encourages tagging, sharing, or commenting

        ---

        🎬 REEL FORMAT:
        Structure your response scene-by-scene, like this:

        - CAMERA: (e.g., Close-up, montage, slow pan, handheld, etc.)
        - VISUAL: What’s happening in the frame
        - AUDIO: Music or sound effects
        - TEXT OVERLAY: On-screen Instagram-style captions
        - VOICEOVER: Natural, expressive line creator would speak

        ---

        📌 KEY STYLE RULES:
        - Use **spoken desi Gen-Z lingo**, not AI-polished narration
        - Prioritize **fast pacing**, **momentum**, and **humorous chaos**
        - Include 1 unexpected **twist or real-life desi interruption**
        - Feel free to break the 4th wall, or add sarcasm
        - Limit total script to 40–45 seconds of screen time
        - Avoid using **"Pure therapy"**, "emotional support drink", "serotonin boost" unless rephrased in funny or raw ways

        ---

        🎤 Transcript:
        {transcript}


        --

        Now reimagine it completely and write a **new viral-ready Instagram Reel script**. New context, new characters, same vibe — but crafted to **hit harder, feel real**, and work for Indian Gen-Z viewers in 2025.

        Respond with only the full formatted script below.

        """

        with st.spinner("✨ Generating new script..."):
            try:
                gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
                response = gemini_model.generate_content(prompt)
                new_script = response.text.strip()
            except Exception as e:
                st.error(f"❌ Gemini API request failed: {str(e)}")
                st.stop()

        cleaned_output = new_script.replace("**", "")
        st.text_area("📢 Final Script:", cleaned_output, height=200)
        st.download_button("📥 Download Script", cleaned_output, file_name="new_script.txt")

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
    finally:
        # 🧹 Clean up files
        for path in [temp_video_path, audio_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass
