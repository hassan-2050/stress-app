import streamlit as st
import os
import json
from gtts import gTTS
from PIL import Image  # reserved for future UI work

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(
    page_title="Stress Relief Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- CSS ----------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --grad-primary: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        --grad-accent:  linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        --grad-surface: linear-gradient(135deg, #ffffff 0%, #f4f5ff 100%);
        --grad-success: linear-gradient(135deg, #059669 0%, #10b981 100%);
        --grad-danger:  linear-gradient(135deg, #e11d48 0%, #fb7185 100%);
        --grad-neutral: linear-gradient(135deg, #475569 0%, #64748b 100%);
        --ink:        #1e293b;
        --ink-soft:   #64748b;
        --line:       rgba(99, 102, 241, 0.14);
        --shadow:     0 10px 30px rgba(30, 41, 59, 0.08);
        --shadow-lg:  0 18px 45px rgba(79, 70, 229, 0.18);
    }

    html, body, [class*="css"], .stMarkdown, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* App backdrop */
    .stApp {
        background:
            radial-gradient(1200px 600px at 12% -10%, rgba(124, 58, 237, 0.10), transparent 60%),
            radial-gradient(1000px 500px at 100% 0%, rgba(219, 39, 119, 0.08), transparent 55%),
            linear-gradient(180deg, #f7f8ff 0%, #eef1fb 100%);
        background-attachment: fixed;
    }

    /* Headings */
    .main-header {
        font-size: 2.85rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: -0.03em;
        margin: 0.5rem 0 0.25rem 0;
        background: var(--grad-primary);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 1.05rem;
        color: var(--ink-soft);
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 500;
    }

    /* Section title accent */
    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.01em;
        margin-bottom: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-title::before {
        content: "";
        width: 6px;
        height: 1.35rem;
        border-radius: 6px;
        background: var(--grad-accent);
    }

    /* Generic card surfaces */
    .info-box, .result-box, .feedback-box,
    .sentiment-positive, .sentiment-negative, .sentiment-neutral,
    .session-complete {
        border-radius: 18px;
        margin: 1.1rem 0;
        box-shadow: var(--shadow);
    }

    .info-box {
        background: var(--grad-surface);
        border: 1px solid var(--line);
        border-left: 5px solid #6366f1;
        padding: 1.5rem 1.75rem;
        color: var(--ink);
    }
    .info-box h3 { color: #4338ca; font-weight: 700; margin: 0 0 0.6rem 0; }

    .result-box {
        background: var(--grad-accent);
        padding: 1.75rem 1.9rem;
        color: #ffffff;
        box-shadow: var(--shadow-lg);
    }
    .result-box h3 { color: #ffffff; font-weight: 700; margin: 0 0 0.6rem 0; }

    .feedback-box {
        background: var(--grad-surface);
        border: 1px solid var(--line);
        padding: 1.6rem 1.75rem;
        text-align: center;
        color: var(--ink);
    }
    .feedback-box h3 { color: #4338ca; font-weight: 700; margin: 0 0 0.5rem 0; }

    .sentiment-positive, .sentiment-negative, .sentiment-neutral {
        padding: 1.6rem 1.75rem;
        color: #ffffff;
        text-align: center;
        box-shadow: var(--shadow-lg);
    }
    .sentiment-positive { background: var(--grad-success); }
    .sentiment-negative { background: var(--grad-danger); }
    .sentiment-neutral  { background: var(--grad-neutral); }
    .sentiment-positive h3, .sentiment-negative h3, .sentiment-neutral h3 {
        margin: 0 0 0.4rem 0; font-weight: 700; letter-spacing: 0.02em;
    }
    .sentiment-score {
        font-size: 2rem; font-weight: 800; margin: 0.2rem 0;
    }

    .session-complete {
        background: var(--grad-success);
        padding: 2rem;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 18px 45px rgba(5, 150, 105, 0.28);
    }
    .session-complete h2 { margin: 0 0 0.4rem 0; font-weight: 800; }

    /* Buttons */
    .stButton > button {
        background: var(--grad-accent);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.28);
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 26px rgba(99, 102, 241, 0.38);
        filter: brightness(1.05);
    }
    .stButton > button:active { transform: translateY(0); }

    /* Link button (feedback) */
    .link-btn {
        background: var(--grad-primary);
        color: #ffffff !important;
        padding: 0.75rem 2.2rem;
        text-decoration: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        display: inline-block;
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.32);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .link-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 30px rgba(124, 58, 237, 0.42);
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid var(--line);
        padding: 0.65rem 0.9rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid var(--line);
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: var(--ink-soft);
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #4338ca;
        background: rgba(99, 102, 241, 0.08);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f3f4ff 100%);
        border-right: 1px solid var(--line);
    }

    /* Auth card wrapper */
    .auth-card {
        max-width: 420px;
        margin: 0 auto;
        background: var(--grad-surface);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 2rem 2rem 1rem 2rem;
        box-shadow: var(--shadow);
    }

    /* Brand logo */
    .brand-logo {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0 0.25rem 0;
    }
    .brand-logo svg {
        filter: drop-shadow(0 12px 24px rgba(79, 70, 229, 0.30));
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- BRAND LOGO ----------------------
LOGO_SVG = """
<div class="brand-logo">
<svg width="76" height="76" viewBox="0 0 84 84" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="brandGrad" x1="0" y1="0" x2="84" y2="84" gradientUnits="userSpaceOnUse">
      <stop stop-color="#4f46e5"/>
      <stop offset="0.5" stop-color="#7c3aed"/>
      <stop offset="1" stop-color="#db2777"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="80" height="80" rx="22" fill="url(#brandGrad)"/>
  <circle cx="42" cy="42" r="23" stroke="#ffffff" stroke-opacity="0.28" stroke-width="2.5"/>
  <path d="M20 49 Q31 35 42 49 T64 49" stroke="#ffffff" stroke-width="3.2"
        stroke-linecap="round" fill="none" opacity="0.95"/>
  <path d="M20 38 Q31 24 42 38 T64 38" stroke="#ffffff" stroke-width="3.2"
        stroke-linecap="round" fill="none" opacity="0.6"/>
</svg>
</div>
"""

# ---------------------- CONSTANTS ----------------------
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/your-form-id-here/viewform?usp=sharing"

VALID_USERS = {"admin", "trial1", "trial2"}
VALID_PASSWORD = "Test@123"

# ---------------------- AI ASSISTANT ----------------------
class StressAssistant:
    def __init__(self):
        self.client = None
        self._setup()

    def _setup(self):
        """Initialize Groq client (API key from env or hardcoded)."""
        try:
            from groq import Groq  # or Client, depending on your installed version
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            if not api_key:
                # fallback: paste same key you use locally, if you want
                api_key = "YOUR_GROQ_API_KEY"

            if not api_key or api_key == "YOUR_GROQ_API_KEY":
                st.sidebar.error("GROQ_API_KEY not set. Set env var or update code.")
                return

            self.client = Groq(api_key=api_key)
            st.sidebar.success("Assistant connected")
        except Exception as e:
            self.client = None
            st.sidebar.error("Assistant offline (Groq init failed).")
            st.sidebar.write(e)

    def analyze_sentiment(self, text):
        if not self.client:
            return "NEUTRAL", 0.5

        system_prompt = (
            "You are a sentiment classifier. Classify the user's message into exactly "
            "one label: POSITIVE, NEGATIVE, or NEUTRAL, and give a confidence score "
            "between 0.0 and 1.0. Respond with ONLY a JSON object of the form "
            '{"label": "POSITIVE"|"NEGATIVE"|"NEUTRAL", "score": <float 0-1>}. '
            "No prose, no markdown, no code fences."
        )

        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},  # forces valid JSON
            )

            content = resp.choices[0].message.content.strip()

            # Defensive: strip code fences if the model still wraps output
            if content.startswith("```"):
                content = content.strip("`").lstrip()
                if content.lower().startswith("json"):
                    content = content[4:].lstrip()

            out = json.loads(content)

            label = str(out.get("label", "NEUTRAL")).upper()
            if label not in {"POSITIVE", "NEGATIVE", "NEUTRAL"}:
                label = "NEUTRAL"

            try:
                score = float(out.get("score", 0.5))
            except (TypeError, ValueError):
                score = 0.5
            score = max(0.0, min(1.0, score))  # clamp

            return label, score
        except Exception:
            # Silent fallback so a parse hiccup doesn't break the UX
            return "NEUTRAL", 0.5

    def transcribe(self, path):
        """Send audio file to Groq Whisper and return text."""
        if not self.client:
            st.error("Assistant client not configured (Groq).")
            return None

        try:
            with open(path, "rb") as f:
                resp = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=f,          # filename has .wav extension
                    temperature=0.0,
                )

            if isinstance(resp, str):
                return resp.strip()

            text = getattr(resp, "text", None)
            if text:
                return text.strip()

            st.error("Transcription response had no text.")
            return None
        except Exception as e:
            st.error("Transcription failed.")
            st.exception(e)
            return None

    def recommend(self, text, sentiment):
        if not self.client:
            return "Relax your shoulders and breathe slowly."

        prompt = (
            f"You are a warm, supportive psychologist. The user's sentiment is: {sentiment}. "
            "Respond in exactly 2 short sentences with a kind, practical suggestion. "
            "Do not use lists, headings, or markdown."
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.7,
                max_tokens=120,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            st.error("Recommendation generation failed.")
            st.exception(e)
            return "Take 3 slow breaths and focus on grounding your body."


# ---------------------- LOGIN SCREEN ----------------------
def show_login():
    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sign in to begin your session</p>', unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown('<div class="section-title">Account Login</div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        login_btn = st.button("Sign In", use_container_width=True)

        if login_btn:
            if username in VALID_USERS and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}. Redirecting to your session...")
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ---------------------- MAIN APP ----------------------
def main():
    # --- Session auth state ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None

    # If not logged in, show login and stop
    if not st.session_state.logged_in:
        show_login()
        return

    # From here on: user is logged in
    assistant = StressAssistant()

    st.markdown(LOGO_SVG, unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Your personal mental wellness companion — speak your mind and receive gentle guidance</p>',
        unsafe_allow_html=True,
    )

    # ---------------------- SIDEBAR INSTRUCTIONS ----------------------
    with st.sidebar:
        st.markdown(f"**Signed in as** `{st.session_state.username}`")
        if st.button("Log out", use_container_width=True):
            for key in ["logged_in", "username", "done", "text", "sentiment", "score", "rec"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.header("How to Use")
        st.markdown("""
**Recording Instructions**
1. Open the **Record Session** tab.
2. Select **Click to record** and allow microphone access.
3. Speak naturally about how you are feeling.
4. Wait a moment while your audio is processed.
5. Switch to the **Results** tab to view your insights.

**Tips for Best Results**
- Use a quiet environment
- Speak clearly at a normal pace
- 5–30 seconds of audio is usually enough
- Describe your current emotions honestly

**What You Will Get**
- A transcript of what you said
- A high-level emotional tone (sentiment)
- A short, personalized recommendation
- An audio version of the guidance
        """)
        st.markdown("---")
        st.markdown("### Privacy Notice")
        st.info("""
- Your audio is only used during this session
- Transcription text stays in memory for this page only
- No personal data is stored or logged by this demo
- Refresh the page to clear everything
        """)

    # ---------------------- SESSION STATE FOR APP LOGIC ----------------------
    if "done" not in st.session_state:
        st.session_state.done = False

    tab1, tab2 = st.tabs(["Record Session", "Results"])

    # ---------------------- TAB 1: RECORD ----------------------
    with tab1:
        st.markdown('<div class="section-title">Record Your Thoughts</div>', unsafe_allow_html=True)
        st.markdown("Speak about whatever is on your mind — work, life, stress, worries, or anything you would like to share.")

        audio_file = st.audio_input("Click to record")

        if audio_file:
            try:
                raw = audio_file.read()
                with open(WAVE_OUTPUT_FILENAME, "wb") as f:
                    f.write(raw)

                st.markdown('<div class="section-title">Your Recording</div>', unsafe_allow_html=True)
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

                st.success("Done. Open the Results tab to see your insights.")
            except Exception as e:
                st.error("Audio processing failed.")
                st.exception(e)

    # ---------------------- TAB 2: RESULTS ----------------------
    with tab2:
        if not st.session_state.done:
            st.info("""
**Welcome to Your Results**

To see your analysis here:

1. Open the **Record Session** tab
2. Record a short message
3. Return here to view your transcript, emotional tone, and guidance
            """)
        else:
            # Pull the main results a bit higher on the page
            st.markdown('<div style="margin-top:-1rem;">', unsafe_allow_html=True)

            # What user shared
            st.markdown(f"""
<div class="info-box">
<h3>What You Shared</h3>
<p style="font-size:1.1rem; line-height:1.6; font-style:italic;">{st.session_state.text}</p>
<div style="text-align:right; font-size:0.9rem; color:#64748b;">
Your words help us understand how you are feeling.
</div>
</div>
""", unsafe_allow_html=True)

            # Sentiment box (now handles NEUTRAL too)
            if st.session_state.sentiment == "POSITIVE":
                box = "sentiment-positive"
            elif st.session_state.sentiment == "NEGATIVE":
                box = "sentiment-negative"
            else:
                box = "sentiment-neutral"

            st.markdown(f"""
<div class="{box}">
<h3>Emotional State</h3>
<div class="sentiment-score">{st.session_state.score*100:.1f}%</div>
<p style="margin:0; font-weight:600; letter-spacing:0.04em;">{st.session_state.sentiment}</p>
<p style="font-size:0.9rem; opacity:0.9; margin-top:0.5rem;">
A simple, high-level emotional snapshot based on your words.
</p>
</div>
""", unsafe_allow_html=True)

            # Guidance box
            st.markdown(f"""
<div class="result-box">
<h3>Your Personalized Guidance</h3>
<p style="font-size:1.2rem; line-height:1.7;">
{st.session_state.rec}
</p>
<div style="font-size:0.9rem; opacity:0.9; margin-top:0.5rem;">
You do not have to fix everything today — small steps count.
</div>
</div>
""", unsafe_allow_html=True)

            # TTS
            try:
                tts = gTTS(st.session_state.rec)
                tts.save("rec.mp3")
                st.markdown('<div class="section-title">Listen to Your Guidance</div>', unsafe_allow_html=True)
                st.audio("rec.mp3")
            except Exception:
                st.warning("Voice generation failed.")

            # Session complete banner
            st.markdown("""
<div class="session-complete">
<h2>Session Complete</h2>
<p>You took a positive step today by checking in with yourself.</p>
</div>
""", unsafe_allow_html=True)

            # Feedback section
            st.markdown("""
<div class="feedback-box">
    <h3>Help Us Support You Better</h3>
    <p style="font-size:1.05rem; margin:0.5rem 0;">
        Your anonymous feedback helps improve this assistant for everyone.
    </p>
    <p style="font-size:0.95rem; color:#64748b;">
        It takes less than a minute.
    </p>
</div>
""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
<div style="text-align:center; margin: 0.5rem 0 1.5rem 0;">
    <a href="{FEEDBACK_FORM_URL}" target="_blank" class="link-btn">
        Share Your Feedback
    </a>
</div>
""", unsafe_allow_html=True)

            with st.expander("Preview: what we will ask you", expanded=False):
                st.markdown("""
- How helpful was the guidance?
- What felt most meaningful to you?
- What could be improved (optional)?
- How was the overall experience?
                """)

            st.success("Thank you for taking a moment for your mental wellness.")

            st.markdown('</div>', unsafe_allow_html=True)  # close margin wrapper


if __name__ == "__main__":
    main()
