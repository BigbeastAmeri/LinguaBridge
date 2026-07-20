import streamlit as st
from streamlit_mic_recorder import mic_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, urllib.parse

try:
    import whisper
    import speech_recognition as sr
    WHISPER_AVAILABLE = True
except:
    import speech_recognition as sr
    WHISPER_AVAILABLE = False

st.set_page_config(page_title="LinguaBridge", page_icon="🌎", layout="centered")

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 2rem; max-width: 600px;}
    div[data-baseweb="select"] > div {
        border-color: #2a2e39!important; background-color: #232733!important;
    }
    div[data-baseweb="select"] > div:focus-within {
        border-color: #4F46E5!important; box-shadow: 0 0 0 1px #4F46E5!important;
    }
    .result-box {
        background: #232733; border-radius: 16px; padding: 16px;
        border-left: 4px solid #4F46E5; margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "Auto Detect": "auto", "English (US)": "en", "Spanish": "es", "French": "fr",
    "Chinese (Mandarin)": "zh", "German": "de", "Arabic": "ar",
    "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Hindi": "hi", "Italian": "it", "Korean": "ko",
    "Yoruba": "yo", "Igbo": "ig", "Hausa": "ha"
}

st.markdown("<h2 style='text-align:center;'>🌎 LinguaBridge</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b90a0; margin-top:-10px;'>Speak Any Language. Understand Everything.</p>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    src_name = st.selectbox("From", list(LANGUAGES.keys()), index=0)
with c2:
    tgt_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], index=1)

src_code = LANGUAGES[src_name]
tgt_code = LANGUAGES[tgt_name]

st.markdown("<p style='text-align:center; font-weight:600; margin-top:30px;'>🎙️ Hold to Talk</p>", unsafe_allow_html=True)

audio = mic_recorder(
    start_prompt=" ● Hold to Record ",
    stop_prompt=" ● Recording... Release to Stop",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="recorder"
)

if audio:
    try:
        # Hybrid: Yoruba/Igbo/Hausa = Whisper FREE, Others = Google FREE
        if src_code in ["yo", "ig", "ha"] and WHISPER_AVAILABLE:
            st.toast("Listening for Yoruba/Igbo/Hausa...")
            with open("/tmp/temp.wav", "wb") as f:
                f.write(audio['bytes'])
            model = whisper.load_model("tiny")
            result = model.transcribe("/tmp/temp.wav", language=src_code)
            temp_text = result["text"]
        else:
            r = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(audio['bytes'])) as source:
                audio_data = r.record(source)
                lang_for_google = "en-US" if src_code == "auto" else src_code
                temp_text = r.recognize_google(audio_data, language=lang_for_google)

        translated = GoogleTranslator(source="auto", target=tgt_code).translate(temp_text)

        st.markdown(f"""
        <div class='result-box'>
            <small style="color:#8b90a0;">{src_name.upper()}</small>
            <p style="font-size:20px; font-weight:600; margin:8px 0;">{temp_text}</p>
            <hr style="border-color:#2a2e39;">
            <small style="color:#8b90a0;">{tgt_name.upper()}</small>
            <h3 style="margin:8px 0; color:#fff;">{translated}</h3>
        </div>
        """, unsafe_allow_html=True)

        tts = gTTS(text=translated, lang=tgt_code)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        st.audio(mp3_fp, format="audio/mp3")

        st.code(translated, language=None)
        st.caption("↑ Long press to copy")
        
        wa_text = urllib.parse.quote(f"{temp_text} -> {translated} (LinguaBridge)")
        st.link_button("Share to WhatsApp", f"https://wa.me/?text={wa_text}", use_container_width=True)

    except Exception as e:
        st.error(f"Could not understand. Try again. {e}")
