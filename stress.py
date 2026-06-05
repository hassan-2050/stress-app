import streamlit as st
import os
import json
import base64
import random
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
        margin: 1.2rem 0 0.25rem 0;
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

    .session-complete {
        background: var(--grad-success);
        padding: 2rem;
        text-align: center;
        color: #ffffff;
        box-shadow: 0 18px 45px rgba(5, 150, 105, 0.28);
    }
    .session-complete h2 { margin: 0 0 0.4rem 0; font-weight: 800; }

    /* Stress meter */
    .stress-score-num {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--ink);
        line-height: 1;
    }
    .band-badge {
        display: inline-block;
        padding: 0.3rem 1.1rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.06em;
        color: #ffffff;
    }
    .meter-track {
        position: relative;
        height: 16px;
        border-radius: 999px;
        margin: 1rem 0 0.4rem 0;
        background: linear-gradient(90deg, #10b981 0%, #f59e0b 55%, #ef4444 100%);
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.15);
    }
    .meter-marker {
        position: absolute;
        top: 50%;
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #ffffff;
        border: 4px solid #1e293b;
        transform: translate(-50%, -50%);
        box-shadow: 0 3px 8px rgba(0,0,0,0.25);
    }
    .meter-scale {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        color: var(--ink-soft);
        font-weight: 600;
    }

    /* Fact / factor items */
    .fact-item {
        background: var(--grad-surface);
        border: 1px solid var(--line);
        border-left: 4px solid #8b5cf6;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin: 0.6rem 0;
        color: var(--ink);
        line-height: 1.55;
    }
    .fact-item strong { color: #4338ca; }

    /* Disclaimer */
    .disclaimer {
        font-size: 0.85rem;
        color: var(--ink-soft);
        background: rgba(99, 102, 241, 0.06);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin: 1.2rem 0;
        line-height: 1.55;
    }

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
    .stTextInput > div > div > input, .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid var(--line);
    }
    .stTextInput > div > div > input:focus, .stTextArea textarea:focus {
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

    /* Brand logo */
    .brand-logo {
        display: flex;
        justify-content: center;
        margin: 0.5rem 0 0.25rem 0;
    }
    .brand-logo svg, .brand-logo img {
        filter: drop-shadow(0 12px 24px rgba(79, 70, 229, 0.30));
    }
    .brand-logo img {
        height: 92px;
        width: auto;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- BRAND LOGO ----------------------
LOGO_FILE = "NCAI Logo icon-05.png"

# Gradient SVG fallback, used only if the logo image cannot be found.
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


def render_logo():
    """Show the NCAI logo image, falling back to the gradient SVG mark if it is missing."""
    try:
        with open(LOGO_FILE, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<div class="brand-logo"><img src="data:image/png;base64,{encoded}" alt="NCAI logo"/></div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(LOGO_SVG, unsafe_allow_html=True)


# Quick stress facts shown while the analysis runs.
LOADING_FACTS = [
    "Slow breathing with longer out-breaths than in-breaths signals safety to your nervous system.",
    "Simply naming an emotion ('this is stress') can lower its intensity by engaging the thinking brain.",
    "A short walk outdoors tends to lower cortisol more than the same walk taken indoors.",
    "Stress narrows your attention; a 90-second pause is often enough to widen it again.",
    "A few minutes of daylight and a glass of water both measurably steady your mood.",
    "Writing a worry down moves it from looping thoughts onto the page, easing mental load.",
    "Your body cannot stay in full fight-or-flight for long; it is built to settle back down.",
]

# ---------------------- CONSTANTS ----------------------
WAVE_OUTPUT_FILENAME = "recorded_audio.wav"
FEEDBACK_FORM_URL = "https://docs.google.com/forms/d/your-form-id-here/viewform?usp=sharing"

VALID_USERS = {"admin", "trial1", "trial2"}
VALID_PASSWORD = "Test@123"

BAND_COLORS = {"LOW": "#10b981", "MODERATE": "#f59e0b", "HIGH": "#f97316", "SEVERE": "#ef4444"}
BAND_SUMMARY = {
    "LOW": "Your stress appears well managed right now. Keep doing what is working for you.",
    "MODERATE": "You are carrying a noticeable but manageable amount of stress today.",
    "HIGH": "Your stress level is elevated. It is worth taking some deliberate steps to ease it today.",
    "SEVERE": "Your stress level is very high. Please be gentle with yourself, and consider reaching out to someone you trust or a professional.",
}
CONTROL_OPTIONS = ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"]
SYMPTOM_OPTIONS = ["Headache", "Muscle tension", "Fatigue", "Racing heart", "Trouble sleeping", "Appetite changes", "None"]
STRESSOR_OPTIONS = ["Work or study", "Relationships", "Finances", "Health", "Family",
                    "Uncertainty about the future", "Other", "Prefer not to say"]


# ---------------------- STRESS SCORING (deterministic, evidence-informed) ----------------------
def compute_stress_index(intake):
    """Turn the intake answers into a 0-100 stress index, a band, and the factors driving it."""
    factors = []
    score = 0.0

    # Current self-reported stress carries the most weight (up to 40 pts).
    score += intake["stress_now"] / 10 * 40
    if intake["stress_now"] >= 7:
        factors.append(("High self-reported stress",
                        f"You rated your current stress at {intake['stress_now']}/10."))

    # Sleep debt below the recommended 7 hours (up to 15 pts).
    if intake["sleep_hours"] < 7:
        score += (7 - intake["sleep_hours"]) / 7 * 15
        factors.append(("Short sleep",
                        f"{intake['sleep_hours']:g} hours last night is below the recommended 7-9."))

    # Perceived loss of control — a core driver of chronic stress (up to 20 pts).
    control_level = CONTROL_OPTIONS.index(intake["control"])  # 0..4
    score += control_level / 4 * 20
    if control_level >= 3:
        factors.append(("Low sense of control",
                        "You often felt unable to control important things this past week."))

    # Energy (up to 10 pts).
    score += {"Low": 10, "Moderate": 5, "High": 0}.get(intake["energy"], 5)
    if intake["energy"] == "Low":
        factors.append(("Low energy", "Low energy can both result from and intensify stress."))

    # Physical symptoms (up to 10 pts).
    symptoms = [s for s in intake["symptoms"] if s != "None"]
    score += min(len(symptoms), 4) / 4 * 10
    if symptoms:
        factors.append(("Physical signs of stress",
                        "You reported: " + ", ".join(s.lower() for s in symptoms) + "."))

    # Physical inactivity (up to 5 pts).
    score += (7 - intake["exercise_days"]) / 7 * 5
    if intake["exercise_days"] <= 1:
        factors.append(("Little physical activity",
                        "Movement is one of the most effective natural stress regulators."))

    # Name the primary stressor for context (no score impact).
    if intake["stressor"] not in ("Prefer not to say",):
        factors.append(("Primary stressor",
                        f"You identified {intake['stressor'].lower()} as your main source of stress."))

    score = int(max(0, min(100, round(score))))
    if score <= 25:
        band = "LOW"
    elif score <= 50:
        band = "MODERATE"
    elif score <= 75:
        band = "HIGH"
    else:
        band = "SEVERE"
    return score, band, factors


def select_stress_facts(intake):
    """Pick evidence-based stress facts relevant to this person's answers."""
    facts = []
    symptoms = [s for s in intake["symptoms"] if s != "None"]

    if intake["sleep_hours"] < 7:
        facts.append("Adults generally need 7-9 hours of sleep. Even one short night raises cortisol "
                     "and makes stress noticeably harder to regulate the next day.")
    if intake["exercise_days"] <= 2:
        facts.append("A single 20-30 minute walk can measurably lower stress hormones and lift mood "
                     "through the release of endorphins.")
    if "Racing heart" in symptoms:
        facts.append("A racing heart under stress is driven by adrenaline. Breathing out for longer "
                     "than you breathe in (try 4 seconds in, 6 out) helps switch on the body's calming response.")
    if "Muscle tension" in symptoms or "Headache" in symptoms:
        facts.append("Stress often shows up physically as muscle tension or headaches before we "
                     "consciously notice we are stressed.")
    if intake["control"] in ("Fairly often", "Very often"):
        facts.append("A feeling of losing control is one of the strongest drivers of stress. Choosing "
                     "one small, doable action restores a real sense of agency.")
    if intake["stressor"] in ("Work or study", "Finances"):
        facts.append("Ongoing pressure from work or money is among the most common chronic stressors. "
                     "Short, regular breaks every 60-90 minutes reduce how much it builds up.")

    # Always close with a grounding, normalizing fact.
    facts.append("Stress itself is a normal, adaptive response. The goal is not to remove it, but to "
                 "keep it from staying switched on for too long.")

    # De-duplicate while preserving order and cap the list.
    seen, out = set(), []
    for f in facts:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out[:4]


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

    def transcribe(self, path):
        """Send audio file to Groq Whisper and return text."""
        if not self.client:
            st.warning("Voice transcription needs the assistant to be connected. "
                       "You can type your reflection instead.")
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

    def assess(self, text, intake, score, band):
        """Use the LLM to reflect on the person's words and give practical guidance.

        Falls back to a sensible templated response when the assistant is offline so the
        app stays useful without an API key.
        """
        fallback = {
            "observations": "",
            "recommendation": (
                "Take three slow breaths and relax your shoulders, then choose one small thing "
                "you can do in the next hour. Steady, small steps matter more than fixing everything today."
            ),
        }
        if not self.client:
            return fallback

        symptoms = ", ".join(intake["symptoms"]) if intake["symptoms"] else "none"
        summary = (
            f"Self-reported stress: {intake['stress_now']}/10. "
            f"Sleep last night: {intake['sleep_hours']:g} hours. "
            f"Main stressor: {intake['stressor']}. "
            f"Sense of control this week: {intake['control']}. "
            f"Energy today: {intake['energy']}. "
            f"Active days this week: {intake['exercise_days']}. "
            f"Physical signs: {symptoms}. "
            f"Computed stress index: {score}/100 ({band})."
        )
        system = (
            "You are a warm, evidence-based stress-management coach. You are NOT a doctor and never "
            "diagnose. Given an intake summary and what the person said in their own words, respond ONLY "
            "as a JSON object of the form "
            '{"observations": "<at most 2 supportive, specific sentences reflecting what stands out>", '
            '"recommendation": "<exactly 2 short, practical, doable sentences>"}. '
            "No markdown, no lists, no medical claims."
        )
        user = (
            f"INTAKE SUMMARY: {summary}\n\n"
            f"IN THEIR OWN WORDS: {text or '(they did not add a spoken or written reflection)'}"
        )
        try:
            resp = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.6,
                max_tokens=220,
                response_format={"type": "json_object"},
            )
            out = json.loads(resp.choices[0].message.content)
            return {
                "observations": str(out.get("observations", "")).strip(),
                "recommendation": str(out.get("recommendation", "")).strip() or fallback["recommendation"],
            }
        except Exception:
            return fallback


# ---------------------- LOGIN SCREEN ----------------------
def show_login():
    render_logo()
    st.markdown('<h1 class="main-header">Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sign in to begin your check-in</p>', unsafe_allow_html=True)

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
                st.success(f"Welcome, {username}. Redirecting to your check-in...")
                st.rerun()
            else:
                st.error("Invalid username or password.")


# ---------------------- RESULTS RENDERING ----------------------
def render_results():
    score = st.session_state.score
    band = st.session_state.band
    band_color = BAND_COLORS[band]

    st.markdown('<div style="margin-top:-1rem;">', unsafe_allow_html=True)

    # Stress snapshot with meter
    st.markdown(f"""
<div class="info-box">
<h3>Your Stress Snapshot</h3>
<div style="display:flex; align-items:center; gap:0.6rem;">
    <span class="stress-score-num">{score}</span>
    <span style="color:#64748b; font-weight:600;">/ 100</span>
    <span class="band-badge" style="background:{band_color}; margin-left:auto;">{band}</span>
</div>
<div class="meter-track"><div class="meter-marker" style="left:{score}%;"></div></div>
<div class="meter-scale"><span>Calm</span><span>Moderate</span><span>High</span></div>
<p style="margin-top:0.9rem; line-height:1.6;">{BAND_SUMMARY[band]}</p>
</div>
""", unsafe_allow_html=True)

    # What is driving the score
    if st.session_state.factors:
        st.markdown('<div class="section-title">What Is Driving This</div>', unsafe_allow_html=True)
        factors_html = "".join(
            f'<div class="fact-item"><strong>{label}</strong><br>'
            f'<span style="color:#64748b;">{detail}</span></div>'
            for label, detail in st.session_state.factors
        )
        st.markdown(factors_html, unsafe_allow_html=True)

    # The person's own words (and any AI reflection)
    if st.session_state.text:
        st.markdown('<div class="section-title">In Your Own Words</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="info-box">
<p style="font-size:1.05rem; line-height:1.6; font-style:italic;">{st.session_state.text}</p>
</div>
""", unsafe_allow_html=True)
    if st.session_state.observations:
        st.markdown(f"""
<div class="info-box">
<h3>What We Noticed</h3>
<p style="line-height:1.6;">{st.session_state.observations}</p>
</div>
""", unsafe_allow_html=True)

    # Stress facts relevant to this person
    st.markdown('<div class="section-title">Stress Facts For You</div>', unsafe_allow_html=True)
    facts_html = "".join(f'<div class="fact-item">{f}</div>' for f in st.session_state.facts)
    st.markdown(facts_html, unsafe_allow_html=True)

    # Personalized guidance
    st.markdown(f"""
<div class="result-box">
<h3>Your Personalized Guidance</h3>
<p style="font-size:1.2rem; line-height:1.7;">{st.session_state.rec}</p>
<div style="font-size:0.9rem; opacity:0.9; margin-top:0.5rem;">
You do not have to fix everything today. Small steps count.
</div>
</div>
""", unsafe_allow_html=True)

    # Listen to guidance
    try:
        tts = gTTS(st.session_state.rec)
        tts.save("rec.mp3")
        st.markdown('<div class="section-title">Listen to Your Guidance</div>', unsafe_allow_html=True)
        st.audio("rec.mp3")
    except Exception:
        st.warning("Voice generation failed.")

    # Responsible-use disclaimer
    st.markdown("""
<div class="disclaimer">
This check-in is a self-reflection tool, not a medical assessment or diagnosis. If your stress feels
unmanageable, or if you ever have thoughts of harming yourself, please contact a qualified professional
or your local emergency or crisis line right away.
</div>
""", unsafe_allow_html=True)

    # Session complete
    st.markdown("""
<div class="session-complete">
<h2>Check-In Complete</h2>
<p>You took a positive step today by pausing to check in with yourself.</p>
</div>
""", unsafe_allow_html=True)

    # Feedback
    st.markdown("""
<div class="feedback-box">
    <h3>Help Us Support You Better</h3>
    <p style="font-size:1.05rem; margin:0.5rem 0;">
        Your anonymous feedback helps improve this assistant for everyone.
    </p>
    <p style="font-size:0.95rem; color:#64748b;">It takes less than a minute.</p>
</div>
""", unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
<div style="text-align:center; margin: 0.5rem 0 1.5rem 0;">
    <a href="{FEEDBACK_FORM_URL}" target="_blank" class="link-btn">Share Your Feedback</a>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close margin wrapper


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

    render_logo()
    st.markdown('<h1 class="main-header">Stress Relief Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">A guided check-in: answer a few questions, share how you feel, and get a clear stress snapshot</p>',
        unsafe_allow_html=True,
    )

    # ---------------------- SIDEBAR ----------------------
    with st.sidebar:
        st.markdown(f"**Signed in as** `{st.session_state.username}`")
        if st.button("Log out", use_container_width=True):
            for key in ["logged_in", "username", "done", "text", "intake", "score",
                        "band", "factors", "facts", "observations", "rec"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.header("How to Use")
        st.markdown("""
**Step 1 — Check-In Questions**
Answer the short set of questions about your sleep, energy, and how you have been feeling. They take about a minute.

**Step 2 — Share How You Feel**
Speak or type a few sentences about what is on your mind. This part is optional but makes your guidance more personal.

**Step 3 — Analyze**
Select **Analyze My Stress**, then open the **Results** tab for your stress snapshot, the factors behind it, stress facts, and practical guidance.

**Tips**
- Answer honestly; there are no right answers
- 5-30 seconds of audio is plenty
- Use a quiet space if you record
        """)
        st.markdown("---")
        st.markdown("### Privacy Notice")
        st.info("""
- Your answers and audio are only used during this session
- Nothing is stored or logged by this demo
- Refresh the page to clear everything
        """)

    # ---------------------- APP STATE ----------------------
    if "done" not in st.session_state:
        st.session_state.done = False

    tab1, tab2 = st.tabs(["Check-In", "Results"])

    # ---------------------- TAB 1: CHECK-IN ----------------------
    with tab1:
        st.markdown('<div class="section-title">A Few Questions First</div>', unsafe_allow_html=True)
        st.markdown("These quick check-in questions ground the analysis in your real day. Nothing is stored.")

        c1, c2 = st.columns(2)
        with c1:
            stress_now = st.slider("How stressed do you feel right now?", 0, 10, 5,
                                   help="0 = completely calm, 10 = extremely stressed")
            sleep_hours = st.slider("How many hours did you sleep last night?", 0.0, 12.0, 7.0, 0.5)
            exercise_days = st.slider("How many days were you physically active this week?", 0, 7, 2)
        with c2:
            stressor = st.selectbox("What is the main source of your stress today?", STRESSOR_OPTIONS)
            control = st.selectbox(
                "In the past week, how often have you felt unable to control the important things in your life?",
                CONTROL_OPTIONS, index=2)
            energy = st.radio("How is your energy level today?",
                              ["Low", "Moderate", "High"], index=1, horizontal=True)

        symptoms = st.multiselect("Any physical signs lately? (select all that apply)",
                                  SYMPTOM_OPTIONS, default=[])

        st.markdown('<div class="section-title">Share How You Feel</div>', unsafe_allow_html=True)
        st.markdown("Speak or type a little about what is on your mind. This is optional, but it makes your guidance more personal.")

        audio_file = st.audio_input("Record (optional)")
        typed = st.text_area(
            "Or type it here (optional)",
            placeholder="For example: Work has been overwhelming and I have not been sleeping well...",
            height=110,
        )

        analyze = st.button("Analyze My Stress", use_container_width=True)

        if analyze:
            intake = {
                "stress_now": stress_now,
                "sleep_hours": sleep_hours,
                "exercise_days": exercise_days,
                "stressor": stressor,
                "control": control,
                "energy": energy,
                "symptoms": symptoms or ["None"],
            }

            # Prefer typed text; otherwise transcribe the recording if one was made.
            text = (typed or "").strip()
            if not text and audio_file is not None:
                try:
                    raw = audio_file.read()
                    with open(WAVE_OUTPUT_FILENAME, "wb") as f:
                        f.write(raw)
                    text = assistant.transcribe(WAVE_OUTPUT_FILENAME) or ""
                except Exception as e:
                    st.error("Audio processing failed.")
                    st.exception(e)

            # Keep the person company with a few quick facts while the analysis runs.
            loading_box = st.empty()
            picks = random.sample(LOADING_FACTS, 3)
            loading_box.markdown(
                '<div class="section-title">While we analyze your check-in</div>'
                + "".join(f'<div class="fact-item">{p}</div>' for p in picks),
                unsafe_allow_html=True,
            )

            with st.spinner("Analyzing your check-in..."):
                score, band, factors = compute_stress_index(intake)
                facts = select_stress_facts(intake)
                ai = assistant.assess(text, intake, score, band)

            loading_box.empty()

            st.session_state.intake = intake
            st.session_state.text = text
            st.session_state.score = score
            st.session_state.band = band
            st.session_state.factors = factors
            st.session_state.facts = facts
            st.session_state.observations = ai.get("observations", "")
            st.session_state.rec = ai.get("recommendation", "")
            st.session_state.done = True

            st.success("Analysis ready. Open the Results tab to view your stress snapshot.")

    # ---------------------- TAB 2: RESULTS ----------------------
    with tab2:
        if not st.session_state.done:
            st.info("""
**Welcome to Your Results**

To see your analysis here:

1. Open the **Check-In** tab
2. Answer the questions and, if you like, share how you feel
3. Select **Analyze My Stress**, then return here
            """)
        else:
            render_results()


if __name__ == "__main__":
    main()
