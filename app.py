import streamlit as st
import os
import ssl
import whisper
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
from pyannote.audio import Pipeline

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
hf_token = os.getenv("HF_TOKEN")  # Hugging Face token for pyannote.audio

# SSL workaround for Whisper
ssl._create_default_https_context = ssl._create_unverified_context

st.title("🎬 Viral Script Generator with Speaker Diarization")

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

@st.cache_resource
def load_diarization_pipeline():
    if not hf_token:
        st.error("❌ Hugging Face token for pyannote.audio not found. Please set HF_TOKEN in .env")
        st.stop()
    return Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.0",
        use_auth_token=hf_token
    )

whisper_model = load_whisper_model()
diarization_pipeline = load_diarization_pipeline()

uploaded_file = st.file_uploader("📁 Upload a video", type=["mp4", "mov", "mkv"])
language_option = st.selectbox("🌐 Select Audio Language", ["Auto", "English", "Hindi", "Urdu"])
lang_code = None if language_option == "Auto" else language_option

if uploaded_file:
    try:
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        st.video("temp_video.mp4")

        st.write("🎧 Extracting audio...")
        with st.spinner("Extracting audio from video..."):
            subprocess.run([
                "ffmpeg", "-i", "temp_video.mp4", "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1", "audio.wav", "-y"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists("audio.wav") or os.path.getsize("audio.wav") == 0:
            st.error("❌ Audio extraction failed. Please upload a video with a valid audio track.")
            st.stop()

        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", "audio.wav"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        try:
            duration = float(result.stdout.decode().strip())
            if duration < 0.5:
                st.error("❌ Audio is too short or silent. Try a longer video.")
                st.stop()
        except:
            st.error("❌ Could not verify audio duration.")
            st.stop()

        st.audio("audio.wav")  # Let user hear it if they want

        # --- Speaker Diarization ---
        st.write("🔎 Performing speaker diarization...")
        with st.spinner("Identifying speakers..."):
            diarization = diarization_pipeline("audio.wav")

        speaker_segments = []
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "start": segment.start,
                "end": segment.end,
                "speaker": speaker
            })
            st.write(f"{segment.start:.2f}s - {segment.end:.2f}s: {speaker}")

        if not speaker_segments:
            st.info("No speakers detected.")

        # --- Whisper Transcription ---
        st.write("📝 Transcribing with Whisper...")
        with st.spinner("Transcribing audio..."):
            result = whisper_model.transcribe(
                "audio.wav",
                language=lang_code if lang_code else None,
                task="translate"  # Force English output
            )
            transcript = result["text"].strip()

        if not transcript:
            st.error("❌ Transcription failed or returned empty text.")
            st.stop()

        st.success("✅ Transcription complete")
        st.text_area("📄 Transcript:", transcript, height=150)

        # --- Align Whisper segments with diarization for speaker-attributed transcript ---
        segments = result.get("segments", [])

        def find_speaker_for_segment(start, end, speaker_segments):
            # Find the speaker segment with the largest overlap
            max_overlap = 0
            assigned_speaker = "Unknown"
            for seg in speaker_segments:
                overlap = max(0, min(end, seg["end"]) - max(start, seg["start"]))
                if overlap > max_overlap:
                    max_overlap = overlap
                    assigned_speaker = seg["speaker"]
            return assigned_speaker

        speaker_transcript = []
        for seg in segments:
            speaker = find_speaker_for_segment(seg["start"], seg["end"], speaker_segments)
            speaker_transcript.append(f"{speaker}: {seg['text']}")

        st.text_area("🗣️ Speaker-attributed Transcript:", "\n".join(speaker_transcript), height=200)
        st.download_button(
            "📥 Download Speaker Transcript",
            "\n".join(speaker_transcript),
            file_name="speaker_transcript.txt"
        )

        # --- Generate Viral Script ---
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

        new_script = response.text.strip().replace("**", "")
        st.text_area("📢 Final Script:", new_script, height=200)
        st.download_button("📥 Download Script", new_script, file_name="new_script.txt")

        # Extract only VOICEOVER lines
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

        # Clean up
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
