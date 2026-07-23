import streamlit as st
from streamlit_mic_recorder import mic_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import io
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="LinguaBridge - AI Voice Translator",
    page_icon="🌎",
    layout="centered"
)

# --- CSS - PRO DARK + NO RED BORDER ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 600px;}
    .main-title {text-align:center; font-size: 32px; font-weight: 800; margin-bottom: 0px;}
    .sub-title {text-align:center; color:#8b90a0; font-size:14px; margin-top:5px; margin-bottom:30px;}
    div[data-baseweb="select"] > div {
        border-color: #2a2e39!important;
        background-color: #232733!important;
        border-radius: 12px!important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #4F46E5!important;
        box-shadow: 0 0 0 1px #4F46E5!important;
    }
    .result-box {
        background: #232733; 
        border-radius: 16px; 
        padding: 20px;
        border-left: 4px solid #4F46E5; 
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .stButton > button {
        background-color: #232733!important;
        border: 1px solid #2a2e39!important;
        border-radius: 12px!important;
        color: white!important;
    }
</style>
""", unsafe_allow_html=True)

# --- ONLY GOOGLE FREE LANGUAGES - NO AFRICA ---
LANGUAGES = {
    "Auto Detect": "auto",
    "English (US)": "en",
    "Spanish": "es",
    "French": "fr",
    "Chinese (Mandarin)": "zh",
    "German": "de",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Hindi": "hi",
    "Italian": "it",
    "Korean": "ko",
    "Dutch": "nl",
    "Turkish": "tr"
}

if "history" not in st.session_state:
    st.session_state.history = []

# --- HEADER ---
st.markdown('<p class="main-title">🌎 LinguaBridge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Speak Any Language. Understand Everything.</p>', unsafe_allow_html=True)

# --- LANGUAGE SELECT ---
c1, c2 = st.columns(2)
with c1:
    src_name = st.selectbox("From", list(LANGUAGES.keys()), index=0)
with c2:
    tgt_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], index=1)

src_code = LANGUAGES[src_name]
tgt_code = LANGUAGES[tgt_name]

# --- MIC BUTTON ---
# --- FIX iPHONE LONG PRESS MENU (THIS IS THE REAL FIX) ---
st.markdown("""
<style>
* {
  -webkit-touch-callout: none !important;
  -webkit-user-select: none !important;
  user-select: none !important;
}
button, [data-testid="stAudio"] {
  -webkit-touch-callout: none !important;
  user-select: none !important;
}
</style>
""", unsafe_allow_html=True)

# --- MIC BUTTON ---
audio = mic_recorder(
    start_prompt="🎙️ Hold to Record",
    stop_prompt="🔴 Release to Stop",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="recorder",
)
# --- PROCESS AUDIO ---
if audio:
    import io
    wav_buffer = io.BytesIO(audio['bytes'])
    r = sr.Recognizer()
    with sr.AudioFile(wav_buffer) as source:
        audio_data = r.record(source)
        temp_text = r.recognize_google(audio_data)
    translated = GoogleTranslator(source='auto', target=tgt_code).translate(temp_text)
        # Translate with Google FREE
        translated = GoogleTranslator(source="auto", target=tgt_code).translate(temp_text)
        st.session_state.history.insert(0, {"src": temp_text, "tgt": translated, "from": src_name, "to": tgt_name})

        # Result Box
        st.markdown(f"""
        <div class='result-box'>
            <small style="color:#8b90a0; letter-spacing:1px;">{src_name.upper()}</small>
            <p style="font-size:22px; font-weight:700; margin:10px 0; color:#fff;">{temp_text}</p>
            <hr style="border-color:#2a2e39; margin:15px 0;">
            <small style="color:#8b90a0; letter-spacing:1px;">{tgt_name.upper()}</small>
            <h3 style="margin:10px 0; color:#fff; font-size:22px;">{translated}</h3>
        </div>
        """, unsafe_allow_html=True)

        # Audio playback - Google FREE TTS
        tts = gTTS(text=translated, lang=tgt_code)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        st.audio(mp3_fp, format="audio/mp3")

        # Copy + Share
        col1, col2 = st.columns(2)
        with col1:
            st.code(translated, language=None)
            st.caption("↑ Long press to copy")
        with col2:
            wa_text = urllib.parse.quote(f"{temp_text} -> {translated} (via LinguaBridge)")
            st.link_button("Share to WhatsApp", f"https://wa.me/?text={wa_text}", use_container_width=True)

    except Exception as e:
        st.error(f"Could not hear you. Speak louder and try again.")
        st.caption(f"Error: {e}")

# --- HISTORY ---
if st.session_state.history:
    st.markdown("### Recent Translations")
    for h in st.session_state.history[:5]:
        st.markdown(f"""
        <div style='background:#1a1d24; border:1px solid #2a2e39; padding:12px 16px; border-radius:12px; margin-bottom:8px;'>
            <small style='color:#8b90a0;'>{h['from']} → {h['to']}</small><br>
            <small style='color:#fff;'>{h['src']}</small><br>
            <b style='color:#fff;'>{h['tgt']}</b>
        </div>
        """, unsafe_allow_html=True)

    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
