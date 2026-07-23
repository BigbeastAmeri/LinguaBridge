import streamlit as st
from streamlit_mic_recorder import mic_recorder
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import io

st.set_page_config(page_title="LinguaBridge", page_icon="🌐", layout="centered")

LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Yoruba": "yo",
    "Igbo": "ig",
    "Hausa": "ha",
    "Arabic": "ar",
    "Portuguese": "pt",
}

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.main-title {text-align:center; font-size:32px; font-weight:700;}
.sub-title {text-align:center; color:#888; margin-bottom:30px;}
.result-box {background:#1e1e2f; padding:20px; border-radius:15px; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🌐 LinguaBridge</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Speak Any Language. Understand Everything.</p>', unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

c1, c2 = st.columns(2)
with c1:
    src_name = st.selectbox("From", list(LANGUAGES.keys()), index=0)
    src_code = LANGUAGES[src_name]
with c2:
    tgt_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], index=0)
    tgt_code = LANGUAGES[tgt_name]

audio = mic_recorder(
    start_prompt="🎙️ Hold to Record",
    stop_prompt="🔴 Release to Stop",
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
            st.success(f"You said: {temp_text}")
            translated = GoogleTranslator(source="auto", target=tgt_code).translate(temp_text)
            st.session_state.history.insert(0, {"src": temp_text, "tgt": translated, "from": src_name, "to": tgt_name})
            
            st.markdown(f"""
            <div class='result-box'>
                <small style="color:#8b90a0;">{src_name.upper()}</small>
                <p style="font-size:20px; font-weight:600;">{temp_text}</p>
                <hr style="border-color:#2a2e39;">
                <small style="color:#8b90a0;">{tgt_name.upper()}</small>
                <h3 style="color:#fff;">{translated}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                tts = gTTS(translated, lang=tgt_code)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                st.audio(mp3_fp, format="audio/mp3")
            except:
                pass
                
    except sr.UnknownValueError:
        st.error("Could not understand audio. Speak louder.")
    except Exception as e:
        st.error(f"Error: {e}")
