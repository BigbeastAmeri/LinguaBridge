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

# Hide Streamlit chrome + Pro styling
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display:none;}
    .block-container {padding-top: 2rem; max-width: 600px;}
    .main-card {
        background: #1a1d24; border: 1px solid #2a2e39; 
        border-radius: 20px; padding: 24px; margin-bottom: 16px;
    }
    .mic-button { display: flex; justify-content: center; margin: 20px 0; }
    .result-box {
        background: #232733; border-radius: 16px; padding: 16px;
        border-left: 4px solid #4F46E5;
    }
    .whatsapp-btn {
        background: #25D366; color: white; border-radius: 50px;
        padding: 12px 24px; width: 80px; height: 80px;
        display: flex; align-items: center; justify-content: center;
        font-size: 36px; box-shadow: 0 8px 24px rgba(37,211,102,0.3);
        transition: all 0.2s; user-select: none;
    }
    .whatsapp-btn:active { transform: scale(0.92); }
</style>
""", unsafe_allow_html=True)

# --- LANGUAGES - Full USA Standard List ---
LANGUAGES = {
    "Auto Detect": "auto",
    "English (US)": "en", "Spanish": "es", "French": "fr",
    "Chinese (Mandarin)": "zh", "German": "de", "Arabic": "ar",
    "Portuguese": "pt", "Russian": "ru", "Japanese": "ja",
    "Hindi": "hi", "Italian": "it", "Korean": "ko", "Yoruba": "yo",
    "Igbo": "ig", "Hausa": "ha"
}
LANG_CODES = {v:k for k,v in LANGUAGES.items()}

# --- STATE ---
if "count" not in st.session_state: st.session_state.count = 0
if "history" not in st.session_state: st.session_state.history = []

# --- HEADER ---
st.markdown("<h2 style='text-align:center;'>🌎 LinguaBridge</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b90a0; margin-top:-10px;'>Speak Any Language. Understand Everything.</p>", unsafe_allow_html=True)

# --- LANGUAGE SELECTORS - V1 CORE ---
c1, c2 = st.columns(2)
with c1:
    src_lang_name = st.selectbox("From", list(LANGUAGES.keys()), index=0)
with c2:
    tgt_lang_name = st.selectbox("To", [k for k in LANGUAGES.keys() if k != "Auto Detect"], index=1)

src_code = LANGUAGES[src_lang_name]
tgt_code = LANGUAGES[tgt_lang_name]

# Free limit
st.progress(st.session_state.count / 50, text=f"Free: {st.session_state.count}/50 translations")
if st.session_state.count >= 50:
    st.warning("Free limit reached. Upgrade to Pro for unlimited.")
    st.stop()

# --- MIC - WhatsApp Style Hold to Talk ---
st.markdown("<p style='text-align:center; font-weight:600; margin-top:20px;'>🎙️ Hold to Talk</p>", unsafe_allow_html=True)
audio = mic_recorder(
    start_prompt=" ● Hold to Record ",
    stop_prompt=" ● Recording... Release to Stop",
    just_once=False,
    use_container_width=True,
    format="wav",
    key="recorder"
)

transcribed_text = None
if audio:
    # Transcribe
    r = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio['bytes'])) as source:
        audio_data = r.record(source)
        try:
            # Auto detect logic
            temp_text = r.recognize_google(audio_data)
            detected_code = detect(temp_text) if src_code == "auto" else src_code
            # If auto, use detected as source for translation
            real_src = detected_code if src_code == "auto" else src_code
            
            transcribed_text = temp_text
            st.session_state.count += 1
            
            # Translate
            translated = GoogleTranslator(source=real_src, target=tgt_code).translate(temp_text)
            
            # Save history
            st.session_state.history.insert(0, {"src": temp_text, "tgt": translated})
            
            # --- RESULT CARD - Professional ---
            st.markdown(f"""
            <div class="result-box">
                <small style="color:#8b90a0;">{LANG_CODES.get(real_src, real_src).upper()} DETECTED</small>
                <p style="font-size:18px; margin:8px 0;">{temp_text}</p>
                <hr style="border-color:#2a2e39;">
                <small style="color:#8b90a0;">{tgt_lang_name.upper()}</small>
                <h3 style="margin:8px 0; color:#fff;">{translated}</h3>
            </div>
            """, unsafe_allow_html=True)

            # --- TTS Audio ---
            tts = gTTS(text=translated, lang=tgt_code)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            st.audio(mp3_fp, format="audio/mp3")

            # --- ACTION ROW: Copy + Share ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("📋 Copy", on_click=lambda: st.toast("Copied!"), use_container_width=True)
                st.code(translated) # This enables native copy
            with col2:
                # WhatsApp Share
                wa_text = urllib.parse.quote(f"LinguaBridge Translation: {temp_text} -> {translated}")
                wa_url = f"https://wa.me/?text={wa_text}"
                st.link_button("WhatsApp", wa_url, use_container_width=True)
            with col3:
                st.link_button("Share X", f"https://twitter.com/intent/tweet?text={wa_text}", use_container_width=True)

            # V2 PRO FEATURE STUB - Voice Cloning
            with st.expander("🔒 Pro V2: Clone My Exact Voice"):
                st.info("Pro feature: English to China, China to English with your exact voice. Integrate ElevenLabs API here.")
                st.code("# ElevenLabs code will go here\n# voice = elevenlabs.clone(file)\n# elevenlabs.text_to_speech(translated, voice=voice)")

        except Exception as e:
            st.error(f"Could not understand audio. Please speak clearly. {e}")

# --- HISTORY ---
if st.session_state.history:
    st.markdown("### Recent")
    for h in st.session_state.history[:3]:
        st.markdown(f"<div class='main-card'><small>{h['src']}</small><br><b>{h['tgt']}</b></div>", unsafe_allow_html=True)
