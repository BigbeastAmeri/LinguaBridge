import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from langdetect import detect
import io, base64, urllib.parse

# --- PAGE CONFIG - USA PRO LOOK ---
st.set_page_config(
    page_title="LinguaBridge - AI Voice Translator",
    page_icon="🌎",
    layout="centered"
)

# --- NEW FIXED CSS - NO RED BORDER ---
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 2rem; max-width: 600px;}
    .main-card {
        background: #1a1d24; border: 1px solid #2a2e39; 
        border-radius: 20px; padding: 24px; margin-bottom: 16px;
    }
    /* FIX FOR RED BORDER */
    div[data-baseweb="select"] > div {
        border-color: #2a2e39!important;
        background-color: #232733!important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #4F46E5!important;
        box-shadow: 0 0 0 1px #4F46E5!important;
    }
    input:focus { outline: none!important; }
    .result-box {
        background: #232733; border-radius: 16px; padding: 16px;
        border-left: 4px solid #4F46E5; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "Auto Detect": "auto",
    "English (US)": "en", "Spanish": "es", "French": "fr",
    "Chinese (Mandarin)": "zh", "German": "de", "Arabic": "ar",
    "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Hindi": "hi", "Italian": "it", "Korean": "ko",
    "Yoruba": "yo", "Igbo": "ig", "Hausa": "ha"
}
LANG_CODES = {v:k for k,v in LANGUAGES.items()}

if "count" not in st.session_state: st.session_state.count = 0
if "history" not in st.session_state: st.session_state.history = []

st.markdown("<h2 style='text-align:center;'>🌎 LinguaBridge</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b90a0; margin-top:-10px;'>Speak Any Language. Understand Everything.</p>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    src_lang_name = st.selectbox("From", list(LANGUAGES.keys()), index=0)
with c2:
    tgt_lang_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], index=1)

src_code = LANGUAGES[src_lang_name]
tgt_code = LANGUAGES[tgt_lang_name]

st.progress(st.session_state.count / 50, text=f"Free: {st.session_state.count}/50 translations")
if st.session_state.count >= 50:
    st.warning("Free limit reached. Upgrade to Pro for unlimited.")
    st.stop()

st.markdown("<p style='text-align:center; font-weight:600; margin-top:20px;'>🎙️ Hold to Talk</p>", unsafe_allow_html=True)
audio = mic_recorder(
    start_prompt=" ● Hold to Record ",
    stop_prompt=" ● Recording... Release to Stop",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="recorder"
)

if audio:
    r = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio['bytes'])) as source:
        audio_data = r.record(source)
        try:
            temp_text = r.recognize_google(audio_data)
            detected_code = detect(temp_text) if src_code == "auto" else src_code
            real_src = detected_code if src_code == "auto" else src_code
            translated = GoogleTranslator(source=real_src, target=tgt_code).translate(temp_text)
            st.session_state.count += 1
            st.session_state.history.insert(0, {"src": temp_text, "tgt": translated})
            st.markdown(f"""
            <div class="result-box">
                <small style="color:#8b90a0;">{LANG_CODES.get(real_src, real_src).upper()} DETECTED</small>
                <p style="font-size:18px; margin:8px 0;">{temp_text}</p>
                <hr style="border-color:#2a2e39;">
                <small style="color:#8b90a0;">{tgt_lang_name.upper()}</small>
                <h3 style="margin:8px 0; color:#fff;">{translated}</h3>
            </div>
            """, unsafe_allow_html=True)
            tts = gTTS(text=translated, lang=tgt_code)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            st.audio(mp3_fp, format="audio/mp3")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.code(translated, language=None)
                st.caption("↑ Copy from here")
            with col2:
                wa_text = urllib.parse.quote(f"LinguaBridge: {temp_text} -> {translated}")
                st.link_button("WhatsApp", f"https://wa.me/?text={wa_text}", use_container_width=True)
            with col3:
                st.link_button("Share X", f"https://twitter.com/intent/tweet?text={wa_text}", use_container_width=True)
            with st.expander("🔒 Pro V2: Clone My Exact Voice"):
                st.info("Pro feature: English to China, China to English with your exact voice. Integrate ElevenLabs API here.")
        except Exception as e:
            st.error(f"Could not understand audio. Please speak clearly. {e}")

if st.session_state.history:
    st.markdown("### Recent")
    for h in st.session_state.history[:3]:
        st.markdown(f"<div class='main-card'><small>{h['src']}</small><br><b>{h['tgt']}</b></div>", unsafe_allow_html=True)
