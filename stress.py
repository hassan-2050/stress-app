import streamlit as st
import io
import os
import random
import json
from gtts import gTTS
from PIL import Image  # kept for future use if needed
from pydub import AudioSegment

try:
    import imageio_ffmpeg
    AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    # If this fails, pydub will try system ffmpeg instead
    pass

# ---------- Page configuration ----------
st.set_page_config(
    page_title="Stress Relief Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.2rem;
        color: #5D6D7E;
        text-align: center;
        margin-bottom: 3rem;
        font-style: italic;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .info-box {
        background: linear-gradient(135deg, #A8E6CF, #88D8A3);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .result-box {
        background: linear-gradient(135deg, #FFD93D, #FF8E53);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .feedback-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .sentiment-positive {
        background: linear-gradient(135deg, #56ab2f, #a8e6cf);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .sentiment-negative {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .recording-indicator {
        font-size: 1.5rem;
        color: #FF6B6B;
        text-align: center;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .feedback-button {
        background: linear-gradient(45deg, #4CAF50, #45a049) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.8rem 2rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 1rem 0 !important;
    }
    .feedback-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.6) !important;
        background: linear-gradient(45deg, #45a049, #4CAF50) !important;
    }
    .session-complete {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
    }
    .main-content { min-height: 600px; }
    .api-warning {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Config ----------
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/your-form-id-here/viewform?usp=sharing"

# ---------- Assistant ----------
class StressAssistant:
    def __init__(self):
        self.client = None
        self._setup_client()

    def _setup_client(self):
        """Initialize AI client using a hardcoded key (for local testing)."""
        try:
            from groq import Client

            # 🔴 WARNING: hardcoding secrets is unsafe for shared / production code.
            # Use this ONLY for local experiments and NEVER commit this key.
            api_key = "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"  # <-- put your key here locally

            self.client = Client(api_key=api_key)
            # No provider name in UI message
            st.sidebar.success("🤖 AI Assistant: Connected ✓")
            return True

        except Exception:
            # Generic message, no provider/API name exposed
            st.sidebar.error("Assistant could not be initialized.")
            return False

    def analyze_sentiment(self, text: str):
        """
        Classify sentiment via API.
        Returns (label, score) where label ∈ {POSITIVE, NEGATIVE, NEUTRAL}.
        """
        if not self.client:
            # Generic error, no API name
            st.error("Sentiment analysis is not available at the moment.")
            return "NEUTRAL", 0.5

        try:
            system_prompt = """
You are a precise sentiment classifier.
Given the user's text, respond ONLY with a JSON object like:
{"label": "POSITIVE" | "NEGATIVE" | "NEUTRAL", "score": float between 0 and 1}

Rules:
- label must be one of: POSITIVE, NEGATIVE, NEUTRAL
- score is your confidence.
Do NOT add any extra text.
""".strip()

            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                max_tokens=60,
            )

            content = resp.choices[0].message.content.strip()
            data = json.loads(content)

            label = str(data.get("label", "NEUTRAL")).upper()
            score = float(data.get("score", 0.5))

            if label not in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
                label = "NEUTRAL"

            score = max(0.0, min(1.0, score))
            return label, score

        except Exception as e:
            # Generic failure text
            st.error(f"Sentiment analysis failed: {e}")
            return "NEUTRAL", 0.5

    def transcribe_audio_groq_first(self, wav_path: str):
        """
        Use cloud transcription for robust, accurate transcription.
        """
        if not self.client:
            st.error("Transcription service is not available at the moment.")
            return None

        try:
            with open(wav_path, "rb") as f:
                data = f.read()

            resp = self.client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(os.path.basename(wav_path), data),
            )

            if hasattr(resp, "text") and resp.text:
                return resp.text
            if isinstance(resp, dict) and "text" in resp:
                return resp["text"]
            return None

        except Exception as e:
            st.error(f"Transcription failed: {e}")
            return None

    def get_recommendation(self, text: str, sentiment: str):
        """Get personalized recommendation from LLM (API-based)."""
        if not self.client:
            fallback_suggestions = [
                ("🌿 **Quick Stress Relief**: It sounds like you're carrying a lot right now. "
                 "Try this breathing: **Inhale 4, hold 4, exhale 6** ×3. You took a great step by pausing 💚"),
                ("🌈 **Gentle Reminder**: Feeling overwhelmed is human. "
                 "Jot down 3 tiny things you're grateful for—this often shifts perspective 🌟"),
                ("💧 **Self-Care Moment**: Take a slow sip of water and stretch your arms overhead. "
                 "Your body sometimes needs a reminder that you're safe 🫂"),
                ("☀️ **Nature Break**: Look out a window for 2 minutes. "
                 "Notice one thing you can see, hear, and feel—it grounds the nervous system 🌱"),
            ]
            return random.choice(fallback_suggestions)

        try:
            system_prompt = f"""
You are a compassionate psychologist specializing in stress management.
Based on the user's spoken text and their detected sentiment ({sentiment}),
provide a warm, empathetic, and practical recommendation in 1–2 sentences.

Focus on:
- Acknowledging their feelings
- Offering a simple, actionable suggestion
- Providing gentle encouragement

Keep it concise, supportive, and professional.
""".strip()

            llm_response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"User said: '{text}'"},
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=120,
            )
            return llm_response.choices[0].message.content.strip()

        except Exception as e:
            st.error(f"Failed to generate AI recommendation: {e}")
            fallback_suggestions = [
                "Take a slow breath and allow the feeling to be there. A 5-minute walk can reset your mind.",
                "You’re doing well by noticing how you feel. Place a hand on your chest and take 3 calm breaths.",
                "Tough moments pass. Choose one small, kind action for yourself right now.",
            ]
            return random.choice(fallback_suggestions)

# ---------- App ----------
def main():
    assistant = StressAssistant()

    # Header
    st.markdown('<h1 class="main-header">🧠 Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Your personal mental wellness companion - speak your mind, receive gentle guidance</p>',
        unsafe_allow_html=True,
    )

    # Session state
    if "session_completed" not in st.session_state:
        st.session_state.session_completed = False
    if "transcribed_text" not in st.session_state:
        st.session_state.transcribed_text = None
    if "recommendation" not in st.session_state:
        st.session_state.recommendation = None
    if "sentiment" not in st.session_state:
        st.session_state.sentiment = None
    if "confidence" not in st.session_state:
        st.session_state.confidence = None

    # Sidebar
    with st.sidebar:
        st.header("📋 How to Use")
        st.markdown("""
### 🎙️ Recording Instructions
1. Click the recorder below and speak (up to ~60s).
2. Wait for it to finish and upload.
3. Your audio is processed and analyzed automatically.
4. Review your analysis and guidance.

### 💡 Tips
- Quiet environment helps.
- Speak naturally about how you feel.

### 🎯 You Get
- 📊 Sentiment analysis
- 🎧 Audio playback
- 💬 Personalized recommendation
- 🔊 Spoken recommendation (gTTS)
- 📝 Quick feedback
        """)
        st.markdown("---")
        st.markdown("### ℹ️ Privacy Notice")
        st.info("""
🔒 Your Privacy Matters:
- Audio handled inside your app session
- Transcriptions used only for analysis & guidance
- No personal data is stored by this app
        """)

    tab1, tab2 = st.tabs(["🎙️ Record Session", "📊 Your Results"])

    # ------------ TAB 1: Record ------------
    with tab1:
        st.subheader("🎙️ Record Your Thoughts")
        audio_file = st.audio_input("Click to record (browser mic)")

        st.caption(
            "Tip: Speak clearly for ~10–30 seconds for best results. "
            "We’ll convert your recording to a clean 16 kHz mono WAV."
        )

        if audio_file is not None:
            try:
                # 1) Read raw bytes
                raw_bytes = audio_file.read()
                if not raw_bytes:
                    st.error("No audio data received from the browser.")
                    st.stop()

                # 2) Decode with pydub
                try:
                    audio_seg = AudioSegment.from_file(io.BytesIO(raw_bytes))
                except Exception as e:
                    st.error("❌ Could not read the audio data. "
                             "Make sure ffmpeg is installed and the format is supported.")
                    st.exception(e)
                    st.stop()

                # 3) Standardize to 16k mono WAV
                try:
                    audio_seg = audio_seg.set_channels(1).set_frame_rate(16000).set_sample_width(2)
                    audio_seg.export(WAVE_OUTPUT_FILENAME, format="wav")
                except Exception as e:
                    st.error("❌ Failed to convert audio to WAV. "
                             "This is usually an ffmpeg issue (missing or not found).")
                    st.exception(e)
                    st.stop()

                # 4) Playback
                st.audio(WAVE_OUTPUT_FILENAME, format="audio/wav")

                # 5) Transcription
                with st.spinner("🔍 Transcribing your voice..."):
                    transcribed_text = assistant.transcribe_audio_groq_first(WAVE_OUTPUT_FILENAME)

                if not transcribed_text:
                    st.warning("I couldn't understand the audio well enough. "
                               "Try speaking a bit closer to the mic.")
                    st.stop()

                st.session_state.transcribed_text = transcribed_text
                st.session_state.session_completed = True

                # 6) Sentiment
                with st.spinner("🎭 Analyzing your emotional tone..."):
                    sentiment, confidence = assistant.analyze_sentiment(transcribed_text)
                st.session_state.sentiment = sentiment
                st.session_state.confidence = confidence

                # 7) Recommendation
                with st.spinner("🤔 Generating personalized recommendation..."):
                    recommendation = assistant.get_recommendation(transcribed_text, sentiment)
                st.session_state.recommendation = recommendation

                st.success("✅ Session completed! Check your results in the 'Your Results' tab.")

            except Exception as e:
                st.error("Unexpected error while processing your recording.")
                st.exception(e)

    # ------------ TAB 2: Results ------------
    with tab2:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        if st.session_state.session_completed and st.session_state.transcribed_text:
            # What you shared
            st.markdown(f"""
<div class="info-box">
    <h3>📝 What You Shared</h3>
    <p style="font-size: 1.2rem; margin: 1rem 0; font-style: italic; line-height: 1.5;">
        {st.session_state.transcribed_text}
    </p>
    <div style="text-align: right; font-size: 0.9rem; color: #5D6D7E;">
        💭 Your honest words help us understand you better
    </div>
</div>
""", unsafe_allow_html=True)

            # Sentiment
            if st.session_state.sentiment:
                sentiment = st.session_state.sentiment
                conf = st.session_state.confidence or 0.5
                sentiment_emoji = "😊" if sentiment == "POSITIVE" else "😔" if sentiment == "NEGATIVE" else "😐"
                sentiment_color_class = (
                    "sentiment-positive" if sentiment == "POSITIVE" else "sentiment-negative"
                )

                st.markdown(f"""
<div class="{sentiment_color_class}">
    <h3>{sentiment_emoji} Your Emotional State</h3>
    <p style="font-size: 1.1rem; margin: 0.5rem 0;">Detected: <strong>{sentiment}</strong></p>
    <p style="margin: 0.5rem 0; opacity: 0.9;">Confidence: <strong>{(conf * 100):.1f}%</strong></p>
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
        🌈 This helps us tailor the perfect recommendation for you
    </div>
</div>
""", unsafe_allow_html=True)

            # Recommendation
            if st.session_state.recommendation:
                st.markdown(f"""
<div class="result-box">
    <h3>💡 Your Personalized Guidance</h3>
    <div style="font-size: 1.3rem; font-style: italic; margin: 1.5rem 0; line-height: 1.6; background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 10px;">
        {st.session_state.recommendation}
    </div>
    <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #2E86AB;">
        🌟 Remember, small steps lead to big changes
    </div>
</div>
""", unsafe_allow_html=True)

                # TTS
                try:
                    with st.spinner("🗣️ Creating audio recommendation..."):
                        tts = gTTS(text=st.session_state.recommendation, lang="en", slow=False)
                        recommendation_audio_path = "recommendation.mp3"
                        tts.save(recommendation_audio_path)

                    st.markdown("""
<div style="background: linear-gradient(135deg, #667eea, #764ba2); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; text-align: center;">
    <h4 style="color: white; margin: 0 0 1rem 0;">🎧 Listen to Your Recommendation</h4>
</div>
""", unsafe_allow_html=True)

                    st.audio(recommendation_audio_path, format="audio/mp3")

                    with open(recommendation_audio_path, "rb") as audio_file:
                        st.download_button(
                            label="💾 Download This Guidance",
                            data=audio_file.read(),
                            file_name="my_stress_relief_guidance.mp3",
                            mime="audio/mpeg",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")

            # Quick actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 New Session", use_container_width=True):
                    for key in ["session_completed", "transcribed_text", "recommendation", "sentiment", "confidence"]:
                        st.session_state[key] = None if key != "session_completed" else False
                    st.rerun()

            with col2:
                st.markdown("---")
                st.info("👆 Switch to 'Record Session' tab to start fresh")

            with col3:
                if st.button("📝 Save This Session", use_container_width=True):
                    st.success("Session saved to your browser! 🎉")

        else:
            st.info("""
### 🌟 Welcome to Your Wellness Journey

**Start by recording your thoughts in the "Record Session" tab above.**

**What to expect:**
- 📝 Your words will appear here clearly
- 🎭 We'll analyze your emotional tone
- 💡 You'll receive personalized guidance
- 🎧 Hear your recommendation in a calming voice

**Remember:** This is a safe space to express yourself honestly.
""")

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------ Post-session Feedback ------------
    if st.session_state.session_completed and st.session_state.transcribed_text:
        st.markdown("---")
        st.markdown("""
<div class="session-complete">
    <h2>🎉 Thank You for This Moment of Self-Care!</h2>
    <p style="font-size: 1.2rem; margin: 1rem 0;">Your vulnerability is your strength 💪</p>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div class="feedback-box">
    <h3>📝 Help Us Support You Better</h3>
    <p style="font-size: 1.1rem; margin: 1rem 0;">Your feedback helps us make this tool even more helpful for everyone!</p>
    <p style="font-size: 1rem; margin: 0.5rem 0; opacity: 0.9;">It takes just 1 minute and is completely anonymous</p>
</div>
""", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
<div style="margin-top: 1rem; text-align:center;">
    <a href="{FEEDBACK_FORM_URL}" target="_blank" style="
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 12px 30px;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        transition: all 0.3s ease;">
        🌟 Share Your Feedback
    </a>
</div>
""", unsafe_allow_html=True)

        with st.expander("👀 Preview: What we'll ask you", expanded=False):
            st.markdown("""
### Quick 4-question survey:
1. ⭐ **How helpful was the recommendation?** (1-5 stars)
2. 💭 **What felt most meaningful to you?**
3. 💡 **What could we improve?** (optional)
4. ⏱️ **How was the experience overall?**

*All responses are anonymous and help us serve you better!*
""")

        st.balloons()
        st.success("💚 You're doing important work by caring for your mental wellness!")

if __name__ == "__main__":
    main()
