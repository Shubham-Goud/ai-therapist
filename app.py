import io
from datetime import datetime
from typing import List, Dict, Any

import streamlit as st

from core.therapist_engine import generate_reply
from core.storage import log_message
from core.sentiment import analyze_sentiment

# Optional libs for TTS + voice input
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

TTS_AVAILABLE = gTTS is not None
VOICE_AVAILABLE = sr is not None

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Therapist (Educational)",
    page_icon="🧠",
    layout="centered",
)


# ---------------- SESSION STATE ----------------
def init_session_state():
    if "messages" not in st.session_state:
        # [{"role": "user"/"ai", "text": "...", "ts": datetime}]
        st.session_state.messages = []

    if "sentiments" not in st.session_state:
        # [{"label": "...", "compound": float, "time": datetime}]
        st.session_state.sentiments = []

    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"

    if "tts_enabled" not in st.session_state:
        st.session_state.tts_enabled = False

# ---------------- THEME CSS ----------------
def inject_css(theme: str = "Dark"):
    if theme == "Light":
        bg = "#f3f4f6"
        text = "#111827"
        card_bg = "#ffffffcc"
        sidebar_bg = "#e5e7eb"
    elif theme == "AMOLED":
        bg = "#000000"
        text = "#e5e7eb"
        card_bg = "#020617cc"
        sidebar_bg = "#020617"
    else:  # Dark
        bg = "#020617"
        text = "#e5e7eb"
        card_bg = "#0f172acc"
        sidebar_bg = "#020617"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top, #1f2937 0, {bg} 45%, {bg} 100%);
            color: {text};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 800px;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {sidebar_bg} 0%, #111827 50%, {sidebar_bg} 100%);
            color: {text};
        }}
        .stMarkdown, .stText, .stCaption {{
            color: {text} !important;
        }}
        [data-testid="stChatMessage"] {{
            border-radius: 0.9rem;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.35rem;
            background: {card_bg};
        }}
        .stAlert {{
            background: rgba(248, 250, 252, 0.08) !important;
            border: 1px solid rgba(248, 250, 252, 0.25) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------- SIDEBAR (SIMPLE, OPTIONAL EXTRAS) ----------------
def render_sidebar() -> str:
    st.sidebar.markdown("## 🧠 AI Therapist")

    st.sidebar.markdown(
        "A simple, supportive chat assistant for talking about how you feel."
    )
    st.sidebar.markdown(
        "> **Important:** This is for learning only.\n"
        "> It is *not* a real therapist and cannot handle emergencies."
    )

    # All advanced controls go inside an expander so the main UX stays simple.
    with st.sidebar.expander("⚙️ Optional settings & tools", expanded=False):
        # Theme toggle
        theme = st.radio(
            "Theme",
            ["Dark", "Light", "AMOLED"],
            index=["Dark", "Light", "AMOLED"].index(st.session_state.theme),
        )
        st.session_state.theme = theme

        st.write("---")

        # TTS toggle
        tts_enabled = st.checkbox(
            "🔊 AI voice replies (TTS)",
            value=st.session_state.tts_enabled,
        )
        st.session_state.tts_enabled = tts_enabled
        if tts_enabled and not TTS_AVAILABLE:
            st.warning("gTTS not installed. TTS will not work until it is installed.")

        # Voice info
        if VOICE_AVAILABLE:
            st.success("🎤 Voice input available via .wav upload in the main area.")
        else:
            st.info("🎤 Voice input optional. Install `SpeechRecognition` to enable it.")

        st.write("---")

        # Download conversation
        if st.session_state.messages:
            lines = []
            for msg in st.session_state.messages:
                role = "You" if msg["role"] == "user" else "AI"
                ts = msg["ts"].strftime("%Y-%m-%d %H:%M:%S")
                lines.append(f"[{ts}] {role}: {msg['text']}")
            transcript = "\n".join(lines)

            st.download_button(
                "💾 Download conversation as .txt",
                transcript,
                file_name="ai_therapist_session.txt",
                mime="text/plain",
            )

        # New session
        if st.button("🔁 Clear chat and start new session"):
            st.session_state.messages = []
            st.session_state.sentiments = []
            st.rerun()

    return st.session_state.theme


# ---------------- HEADER ----------------
def render_header():
    st.markdown(
        """
        <div style="text-align:center; padding: 0.3rem;">
            <h1>🧠 AI Therapist</h1>
            <p style="color:#9ca3af; font-size:0.95rem;">
                Just type how you're feeling and I'll respond in a calm, simple way.<br>
                <b>I'm not a real therapist and can't handle emergencies.</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "If you ever feel in danger or very unsafe, please contact a trusted person or your local emergency number.",
        icon="⚠️",
    )


# ---------------- CORE MESSAGE HANDLER ----------------
def handle_user_message(user_text: str):
    """Core pipeline for one user message."""
    now = datetime.now()

    # 1. Save user message
    st.session_state.messages.append(
        {"role": "user", "text": user_text, "ts": now}
    )
    log_message("user", user_text)

    # 2. Sentiment detection (for logs / research)
    senti = analyze_sentiment(user_text)
    if senti.get("available"):
        st.session_state.sentiments.append(
            {
                "label": senti["label"],
                "compound": senti["compound"],
                "time": now,
            }
        )

    # 3. Generate AI reply (friendly + safe)
    reply, is_crisis = generate_reply(user_text)

    st.session_state.messages.append(
        {"role": "ai", "text": reply, "ts": datetime.now()}
    )
    log_message("ai", reply)

    # 4. Show AI reply in chat
    with st.chat_message("assistant", avatar="🤖"):
        if is_crisis:
            st.error(reply)
        else:
            # Small "thinking" placeholder – feels more like a chat app
            placeholder = st.empty()
            placeholder.markdown("_Thinking..._")
            placeholder.markdown(reply)

        # 5. Optional TTS playback
        if st.session_state.tts_enabled and TTS_AVAILABLE:
            try:
                tts = gTTS(reply)
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format="audio/mp3")
            except Exception:
                st.warning("Couldn't generate voice for this reply.")


# ---------------- CHAT UI (MAIN EXPERIENCE) ----------------
def render_chat():
    st.markdown("---")

    # Show previous messages
    for msg in st.session_state.messages:
        role = "assistant" if msg["role"] == "ai" else "user"
        avatar = "🤖" if role == "assistant" else "🧑"
        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["text"])

    # Text chat input – main way to use it
    user_input = st.chat_input("Tell me what's going on in your mind...")
    if user_input:
        handle_user_message(user_input)

    # Optional voice input (kept very simple)
    st.markdown("#### 🎤 Or share with your voice (optional)")
    st.caption("Upload a short .wav clip and I'll try to turn it into text and reply.")

    audio_file = st.file_uploader(
        "Upload a .wav file",
        type=["wav"],
        key="voice_uploader",
    )

    if audio_file is not None:
        if not VOICE_AVAILABLE:
            st.warning("`SpeechRecognition` is not installed, so voice input won't work.")
        else:
            if st.button("Transcribe and send"):
                recognizer = sr.Recognizer()
                try:
                    with sr.AudioFile(audio_file) as source:
                        audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data)
                    st.success(f"Transcribed: **{text}**")
                    handle_user_message(text)
                except Exception:
                    st.error("Sorry, I couldn't understand that audio.")


# ---------------- MAIN ----------------
def main():
    init_session_state()
    theme = render_sidebar()
    inject_css(theme)
    render_header()
    render_chat()


if __name__ == "__main__":
    main()
