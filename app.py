import streamlit as st
import os
import ssl
import whisper
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
import yt_dlp
import tempfile

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

ssl._create_default_https_context = ssl._create_unverified_context

st.title("🎬 Viral Script Generator")

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

input_mode = st.radio("📥 Choose input type:", ["Upload Video", "Paste Reel Link"])
video_file_path = None
temp_audio_file = "audio.wav"

if input_mode == "Upload Video":
    uploaded_file = st.file_uploader("📁 Upload a video", type=["mp4", "mov", "mkv"])
    if uploaded_file:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        video_file_path = "temp_video.mp4"
        st.video("temp_video.mp4")

elif input_mode == "Paste Reel Link":
    reel_link = st.text_input("🔗 Paste Instagram Reel URL")
    if reel_link:
        st.info("🔄 Downloading Reel...")
        with st.spinner("Fetching reel from Instagram..."):
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    output_template = os.path.join(tmpdir, "reel.%(ext)s")
                    ydl_opts = {
                        'format': 'mp4',
                        'outtmpl': output_template,
                        'quiet': True,
                        'noplaylist': True
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([reel_link])

                    for file in os.listdir(tmpdir):
                        if file.endswith(".mp4"):
                            video_file_path = os.path.join(tmpdir, file)
                            break

                if not video_file_path or not os.path.exists(video_file_path):
                    st.error("❌ Video download failed. Could not process the reel.")
                    st.stop()

                st.video(video_file_path)

            except Exception as e:
                st.error(f"❌ Failed to download reel: {e}")
                st.stop()

language_option = st.selectbox("🌐 Select Audio Language", ["Auto", "English", "Hindi", "Urdu"])
lang_code = None if language_option == "Auto" else language_option

if video_file_path:
    try:
        st.write("🎧 Extracting audio...")
        with st.spinner("Extracting audio from video..."):
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", video_file_path,
                "-ar", "16000", "-ac", "1", "-acodec", "pcm_s16le", temp_audio_file
            ]
            result = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0 or not os.path.exists(temp_audio_file):
                st.error("❌ Audio extraction failed.")
                st.stop()

        if os.path.getsize(temp_audio_file) == 0:
            st.error("❌ Extracted audio is empty. Try another video.")
            st.stop()

        st.audio(temp_audio_file)

        st.write("📝 Transcribing with Whisper...")
        with st.spinner("Transcribing..."):
            result = whisper_model.transcribe(
                temp_audio_file,
                language=lang_code if lang_code else None,
                task="translate"
            )
            transcript = result["text"].strip()

        if not transcript:
            st.error("❌ Transcription returned no text.")
            st.stop()

        st.success("✅ Transcription complete")
        st.text_area("📄 Transcript:", transcript, height=150)

        st.write("🧠 Generating fresh, viral-ready script...")

        prompt = f"""
You're a creative director and viral scriptwriter for Gen-Z Instagram Reels in the Indian subcontinent.

Your job is to transform the transcript below into a **completely new, reimagined video script** that:

- Keeps the **emotional vibe, tone, and intent** of the original
- Tells a **visually and narratively different story**
- Is designed for a **40–45 second Instagram Reel**
- Sounds **authentic and unscripted**
- Uses **chaotic desi relatability**, funny breakdowns, street moments, sarcastic voiceovers
- Includes a **strong hook**, and ends with a **funny or emotional CTA**

---

🎬 REEL FORMAT:
- CAMERA:
- VISUAL:
- AUDIO:
- TEXT OVERLAY:
- VOICEOVER:

---

🎤 Transcript:
{transcript}

Now reimagine it completely and write a new Instagram Reel script. Respond with only the script.
"""

        with st.spinner("✨ Generating new script..."):
            gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            response = gemini_model.generate_content(prompt)

        new_script = response.text.strip().replace("**", "")
        st.text_area("📢 Final Script:", new_script, height=200)
        st.download_button("📥 Download Script", new_script, file_name="new_script.txt")

        voiceover_lines = []
        for line in new_script.splitlines():
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

        if os.path.exists("temp_video.mp4"):
            os.remove("temp_video.mp4")
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        try:
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
        except:
            pass
