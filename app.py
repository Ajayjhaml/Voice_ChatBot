import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import base64
import io
import time
import re

# === Setup ===
st.set_page_config(page_title="🧠 Voice Assistant", layout="wide")
st.title("🤖 AI – Voice Assistant")

# === State Init ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You're Sem, a helpful AI assistant."

# === Theme ===
def apply_theme(dark_mode):
    theme_css = """
        body, .stApp {
            background-color: #121212;
            color: #f0f0f0;
        }
        .stButton>button, .stTextInput>div>div>input {
            background-color: #1f1f1f;
            color: white;
            border: 1px solid #444;
        }
    """ if dark_mode else """
        body, .stApp {
            background-color: #f5f5f5;
            color: #222;
        }
        .stButton>button, .stTextInput>div>div>input {
            background-color: #fff;
            color: #222;
        }
    """
    st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

# === Sidebar ===
st.sidebar.title("⚙️ Settings")
st.session_state.dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.system_prompt = st.sidebar.text_area("🧠 System Prompt", st.session_state.system_prompt, height=100)
apply_theme(st.session_state.dark_mode)

# === Jarvis Pulse Animation ===
def jarvis_circle():
    st.markdown("""
        <style>
        .jarvis-circle {
            width: 110px;
            height: 110px;
            border-radius: 50%;
            background: radial-gradient(circle at center, rgba(0, 191, 255, 0.2), transparent 70%);
            animation: pulseGlow 2s infinite ease-in-out;
            box-shadow:
                0 0 20px rgba(0, 191, 255, 0.6),
                0 0 40px rgba(0, 191, 255, 0.4),
                0 0 60px rgba(0, 191, 255, 0.2);
            margin: auto;
        }
        @keyframes pulseGlow {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        </style>
        <div class="jarvis-circle"></div>
    """, unsafe_allow_html=True)

# === TTS using gTTS ===
def speak_text(text):
    try:
        clean_text = re.sub(r"[^\w\s,.!?]", "", text)
        tts = gTTS(text=clean_text)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode()
        st.markdown(f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"TTS Error: {e}")

# === Recognize speech from microphone ===
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Speech recognition service error."

# === Call local FastAPI LLM server ===
def get_llm_response(prompt):
    try:
        res = requests.post("http://127.0.0.1:8000/generate", json={
            "instruction": st.session_state.system_prompt,
            "input": prompt,
            "max_tokens": 100,
            "temperature": 0.7
        })
        if res.status_code == 200:
            return res.json().get("response", "No response from model.")
        else:
            return f"Model Error {res.status_code}"
    except Exception as e:
        return f"Exception: {e}"

# === Layout Columns ===
left_col, divider, right_col = st.columns([1.2, 0.05, 2])

# === Left: Chat History ===
with left_col:
    st.subheader("🕘 Chat History")
    if st.button("➕ New Chat"):
        st.session_state.chat_history = []
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history[::-1]:
            st.markdown(f"**🗣️ You:** {chat['user']}")
            st.markdown(f"**🤖 Assistant:** {chat['bot']}")
            st.markdown("---")
    else:
        st.info("No chat yet.")

# === Divider Line ===
with divider:
    st.markdown('<div style="width:2px;height:100vh;background:linear-gradient(to bottom, #00bfff, #fff0);border-radius:5px;"></div>', unsafe_allow_html=True)

# === Right: Live Chat ===
with right_col:
    st.subheader("🎤 Speak to AI Assistant")
    jarvis_circle()

    if st.button("🎙️ Talk Now"):
        user_query = recognize_speech()
        st.success(f"🗣️ You: {user_query}")

        with st.spinner("🤔 Assistant is thinking..."):
            response = get_llm_response(user_query)

        # Typewriter animation
        output_area = st.empty()
        typed = ""
        for word in response.split():
            typed += word + " "
            output_area.markdown(f"### 🤖 Assistant:\n\n{typed}")
            time.sleep(0.04)

        # Voice output
        speak_text(response)

        # Store chat
        st.session_state.chat_history.append({
            "user": user_query,
            "bot": response
        })
