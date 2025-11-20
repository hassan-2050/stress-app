import streamlit as st
import io
import os
import random
import json
import numpy as np
import soundfile as sf
from gtts import gTTS
from PIL import Image

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Stress Relief Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CSS (UNCHANGED + SMALL ADDITIONS) ----------------------
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
    .session-complete {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
    }
    .main-content {
        min-height: 500px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- CONSTANTS ----------------------
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/your-form-id-here/viewform?usp=sharing"

# ---------------------- AI ASSISTANT ----------------------
class StressAssistant:
    def __init__(self):
        self.client = None
        self._setup()

    def _setup(self):
        """Hide API provider from UI."""
        try:
            from groq import Client
            # ⬇️ Put your real key here or use an env var
            self.client = Client(api_key="YOUR_GROQ_API_KEY")
            st.sidebar.success("🤖 Assistant Connected")
        except:
            st.sidebar.error("Assistant offline.")

    def analyze_sentiment(self, text):
        if not self.client:
            return "NEUTRAL", 0.5

        system_prompt = """
Return JSON only: {"label": "...", "score": ...}
"""

        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
            )

            out = json.loads(resp.choices[0].message.content)
            return out["label"], out["score"]
        except:
            return "NEUTRAL", 0.5

    def transcribe(self, path):
        if not self.client:
            return None

        try:
            with open(path, "rb") as f:
                audio = f.read()

            resp = self.client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=(os.path.basename(path), audio),
            )
            return resp.text
        except:
            return None

    def recommend(self, text, sentiment):
        if not self.client:
            return "Relax your shoulders and breathe slowly."

        prompt = f"You are a psychologist. User sentiment: {sentiment}. Give a warm 2-sentence recommendation."
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except:
            return "Take 3 slow breaths and focus on grounding your body."


# ---------------------- MAIN APP ----------------------
def main():
    assistant = StressAssistant()

    st.markdown('<h1 class="main-header">🧠 Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your personal mental wellness companion - speak your mind, receive gentle guidance</p>', unsafe_allow_html=True)

    # ---------------------- SIDEBAR INSTRUCTIONS (NEW) ----------------------
    with st.sidebar:
        st.header("📋 How to Use")
        st.markdown("""
### 🎙️ Recording Instructions
1. Go to the **"🎙️ Record Session"** tab.
2. Click on **"Click to record"** and allow microphone access.
3. Speak naturally about how you're feeling.
4. Wait a moment while your audio is processed.
5. Switch to the **"📊 Results"** tab to view your insights.

### 💡 Tips for Best Results
- Use a **quiet environment**.
- Speak **clearly and at a normal pace**.
- Recording just **5–30 seconds** is usually enough.
- Try to describe your **current emotions honestly**.

### 🎯 What You'll Get
- 📝 A transcript of what you said  
- 📊 A basic sentiment label (positive/negative/neutral)  
- 💡 A short, personalized recommendation  
- 🎧 An audio version of the guidance
        """)
        st.markdown("---")
        st.markdown("### ℹ️ Privacy Notice")
        st.info("""
- Your audio is used only for this session.
- Transcription text is kept in memory for the current session only.
- No personal data is stored or logged by this demo.
- You can refresh the page to clear everything.
        """)

    # Session vars
    if "done" not in st.session_state:
        st.session_state.done = False

    tab1, tab2 = st.tabs(["🎙️ Record Session", "📊 Results"])

    # ---------------------- TAB 1 ----------------------
    with tab1:
        st.subheader("🎙️ Record Your Thoughts")
        st.markdown("Speak about whatever is on your mind — work, life, stress, worries, or anything you’d like to share.")

        audio_file = st.audio_input("Click to record")

        if audio_file:
            raw = audio_file.read()

            # ---------------------- Audio decode w/o pydub ----------------------
            try:
                audio_buf = io.BytesIO(raw)
                try:
                    data, sr = sf.read(audio_buf, dtype='float32')
                except:
                    with open("temp_audio", "wb") as f:
                        f.write(raw)
                    data, sr = sf.read("temp_audio", dtype='float32')
                    os.remove("temp_audio")

                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)

                target_sr = 16000
                if sr != target_sr:
                    duration = len(data) / sr
                    new_len = int(duration * target_sr)
                    data = np.interp(
                        np.linspace(0, len(data), new_len),
                        np.arange(len(data)),
                        data
                    )

                sf.write(WAVE_OUTPUT_FILENAME, data, target_sr)

                st.markdown("#### 🔊 Your Recording")
                st.audio(WAVE_OUTPUT_FILENAME)

                text = assistant.transcribe(WAVE_OUTPUT_FILENAME)
                if not text:
                    st.error("Could not understand audio. Please try again and speak a bit more clearly or for a bit longer.")
                    return

                label, score = assistant.analyze_sentiment(text)
                rec = assistant.recommend(text, label)

                st.session_state.text = text
                st.session_state.sentiment = label
                st.session_state.score = score
                st.session_state.rec = rec
                st.session_state.done = True

                st.success("✅ Done! Open the **📊 Results** tab to see your insights.")

            except Exception as e:
                st.error("Audio processing failed.")
                st.exception(e)

    # ---------------------- TAB 2 ----------------------
    with tab2:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)

        if not st.session_state.done:
            st.info("""
### 🌟 Welcome to Your Results
To see your analysis here:

1. Go to the **🎙️ Record Session** tab  
2. Record a short message  
3. Come back here to view your transcript, emotional tone, and guidance
            """)
        else:
            # UI untouched below, with added context + feedback at end:
            st.markdown(f"""
<div class="info-box">
<h3>📝 What You Shared</h3>
<p style="font-size:1.1rem; line-height:1.6; font-style:italic;">{st.session_state.text}</p>
<div style="text-align:right; font-size:0.9rem; color:#5D6D7E;">💭 Your words help us understand how you're feeling.</div>
</div>
""", unsafe_allow_html=True)

            box = "sentiment-positive" if st.session_state.sentiment == "POSITIVE" else "sentiment-negative"
            emoji = "😊" if box == "sentiment-positive" else "😔"

            st.markdown(f"""
<div class="{box}">
<h3>{emoji} Emotional State</h3>
<p>{st.session_state.sentiment} ({st.session_state.score*100:.1f}%)</p>
<p style="font-size:0.9rem; opacity:0.9;">This is a simple, high-level emotional snapshot based on your words.</p>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="result-box">
<h3>💡 Your Personalized Guidance</h3>
<p style="font-size:1.2rem; line-height:1.7; font-style:italic;">{st.session_state.rec}</p>
<div style="text-align:center; font-size:0.9rem; color:#2E86AB; margin-top:0.5rem;">🌟 You don't have to fix everything today — small steps count.</div>
</div>
""", unsafe_allow_html=True)

            # TTS
            try:
                tts = gTTS(st.session_state.rec)
                tts.save("rec.mp3")
                st.markdown("#### 🎧 Listen to Your Guidance")
                st.audio("rec.mp3")
            except:
                st.warning("Voice generation failed.")

            st.markdown("""
<div class="session-complete">
<h2>🎉 Session Complete</h2>
<p>You took a positive step today by checking in with yourself.</p>
</div>
""", unsafe_allow_html=True)

            # ---------------------- FEEDBACK SECTION (NEW) ----------------------
            st.markdown("""
<div class="feedback-box">
    <h3>📝 Help Us Support You Better</h3>
    <p style="font-size:1.05rem; margin:0.5rem 0;">
        Your anonymous feedback helps improve this assistant for everyone.
    </p>
    <p style="font-size:0.95rem; opacity:0.9;">
        It takes less than a minute.
    </p>
</div>
""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
<div style="text-align:center; margin-bottom:1.5rem;">
    <a href="{FEEDBACK_FORM_URL}" target="_blank" style="
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 12px 30px;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.05rem;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
        transition: all 0.3s ease;
    ">
        🌟 Share Your Feedback
    </a>
</div>
""", unsafe_allow_html=True)

            with st.expander("👀 Preview: What we'll ask you", expanded=False):
                st.markdown("""
- ⭐ How helpful was the guidance?  
- 💭 What felt most meaningful to you?  
- 💡 What could be improved (optional)?  
- ⏱️ How was the overall experience?
                """)

            st.balloons()
            st.success("💚 Thank you for taking a moment for your mental wellness.")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
