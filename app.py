import streamlit as st
from streamlit_mic_recorder import mic_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import io

st.set_page_config(page_title="LinguaBridge", page_icon="🌐", layout="centered")

LANGUAGES = {
    "Auto Detect": "auto", "English": "en", "Spanish": "es",
    "French": "fr", "German": "de", "Yoruba": "yo",
    "Igbo": "ig", "Hausa": "ha", "Arabic": "ar", "Portuguese": "pt",
}

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
div[data-baseweb="select"] {border-left: 4px solid #7c3aed !important;}
button[kind="secondary"] {border: 1.5px solid #7c3aed !important; border-left: 4px solid #7c3aed !important; background: #1c1c24 !important;}
.stApp {background: #0a0a0f;}

/* TITLE */
.main-title {text-align:center; font-size:32px; font-weight:800; color:white;}
.sub-title {text-align:center; color:#8b8fa3; margin-bottom:35px;}

/* PURPLE LINE FOR DROPDOWNS - YOUR REQUEST */
div[data-baseweb="select"] {
    background: #1c1c24 !important;
    border-left: 4px solid #7c3aed !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(124,58,237,0.15) !important;
}
div[data-baseweb="select"]:focus-within {
    border-left: 4px solid #a78bfa !important;
    box-shadow: 0 0 25px rgba(124,58,237,0.4) !important;
}

/* RECORD BUTTON PURPLE GLOW */
button[kind="secondary"] {
    border: 1.5px solid rgba(124,58,237,0.4) !important;
    border-left: 4px solid #7c3aed !important;
    background: #1c1c24 !important;
    color: white !important;
    border-radius: 12px !important;
    height: 55px !important;
    font-weight: 600 !important;
}

/* RESULT CARD WITH PURPLE LINE - LIKE YOUR SCREENSHOT */
.result-card {
    background: #1e1e28;
    border-radius: 20px;
    padding: 24px;
    margin-top: 25px;
    border-left: 5px solid #7c3aed;
    box-shadow: -5px 0 30px rgba(124,58,237,0.2), 0 10px 30px rgba(0,0,0,0.4);
}
.result-label {font-size:11px; letter-spacing:2px; color:#6b7280; font-weight:700;}
.result-original {font-size:22px; font-weight:600; color:#e5e7eb; margin:8px 0;}
.result-translated {font-size:28px; font-weight:800; color:white; margin:12px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌐 LinguaBridge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Speak Any Language. Understand Everything.</p>', unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []
if 'from_lang' not in st.session_state:
    st.session_state.from_lang = "Auto Detect"
    st.session_state.to_lang = "Spanish"
if 'do_swap' not in st.session_state:
    st.session_state.do_swap = False

if st.session_state.do_swap:
    temp_from = st.session_state.from_lang
    st.session_state.from_lang = st.session_state.to_lang
    st.session_state.to_lang = temp_from
    st.session_state.do_swap = False

c1, c2, c3 = st.columns([4,1,4])
with c1:
    st.markdown("From")
    src_name = st.selectbox("From", list(LANGUAGES.keys()), key="from_lang", label_visibility="collapsed")
    src_code = LANGUAGES[src_name]
with c2:
    st.markdown(" ")
    if st.button("🔄", use_container_width=True):
        st.session_state.do_swap = True
        st.rerun()
with c3:
    st.markdown("To")
    tgt_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], key="to_lang", label_visibility="collapsed")
    tgt_code = LANGUAGES[tgt_name]
st.write("")
audio = mic_recorder(
    start_prompt="🎙️ Hold to Record",
    stop_prompt="🔴 Release to Translate",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="recorder"
)

if audio:
    try:
        wav_buffer = io.BytesIO(audio['bytes'])
        r = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            audio_data = r.record(source)
            temp_text = r.recognize_google(audio_data)
        if temp_text:
            translated = GoogleTranslator(source="auto", target=tgt_code).translate(temp_text)
            st.markdown(f"""
            <div class='result-card'>
                <div class='result-label'>{src_name.upper()}</div>
                <div class='result-original'>{temp_text}</div>
                <hr style="border-color:rgba(255,255,255,0.08); margin:18px 0;">
                <div class='result-label'>{tgt_name.upper()}</div>
                <div class='result-translated'>{translated}</div>
            </div>
            """, unsafe_allow_html=True)
            try:
                tts = gTTS(translated, lang=tgt_code)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                st.audio(mp3_fp, format="audio/mp3")
                st.code(translated, language=None)
                st.caption("👆 Long press to copy")
            except:
                pass
    except:
        st.error("Couldn't hear you - speak louder")
