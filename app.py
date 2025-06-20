import streamlit as st
import os
import ssl
import whisper
import subprocess
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()  # load from .env

st.title("🎬 Viral Script Generator")

# Set Gemini API key
api_key = os.getenv("GOOGLE_API_KEY")

# SSL fix for Whisper model download
ssl._create_default_https_context = ssl._create_unverified_context

# Load Whisper model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# Upload video
uploaded_file = st.file_uploader("📁 Upload a video", type=["mp4", "mov", "mkv"])

# Language selector
language_option = st.selectbox("🌐 Select Audio Language", ["Auto", "English", "Hindi", "Urdu"])
lang_code = None if language_option == "Auto" else language_option

if uploaded_file:
    try:
        # Save uploaded video
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        st.video("temp_video.mp4")

        # 🔄 Extract audio using ffmpeg
        st.write("🎧 Extracting audio...")
        with st.spinner("Extracting audio from video..."):
            subprocess.run([
                "ffmpeg", "-i", "temp_video.mp4", "-q:a", "0", "-map", "a", "audio.wav", "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 📝 Transcribe using Whisper with language selection
        st.write("📝 Transcribing with Whisper...")
        with st.spinner("Transcribing audio..."):
            if lang_code:
                result = whisper_model.transcribe("audio.wav", language=lang_code)
            else:
                result = whisper_model.transcribe("audio.wav")
            transcript = result["text"]

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
            gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            response = gemini_model.generate_content(prompt)

        new_script = response.text.strip()
        cleaned_output = new_script.replace("**", "")
        st.text_area("📢 Final Script:", cleaned_output, height=200)
        st.download_button("📥 Download Script", cleaned_output, file_name="new_script.txt")

        # 📤 Extract only VOICEOVER lines
        voiceover_lines = []
        for line in cleaned_output.splitlines():
            if line.strip().lower().startswith("voiceover:"):
                voice_line = line.split(":", 1)[1].strip()
                if voice_line:
                    voiceover_lines.append(voice_line)

        voiceover_script = "\n".join(voiceover_lines)

        if voiceover_script:
            st.text_area("🎤 Voiceover Script Only:", voiceover_script, height=150)
            st.download_button("🔊 Download Voiceover Script", voiceover_script, file_name="voiceover_script.txt")
        else:
            st.info("No VOICEOVER lines found in the script.")

        # 🧹 Clean up files
        os.remove("temp_video.mp4")
        os.remove("audio.wav")

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        try:
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
            if os.path.exists("audio.wav"):
                os.remove("audio.wav")
        except:
            pass
