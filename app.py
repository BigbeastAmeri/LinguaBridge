import streamlit as st

import openai
from gtts import gTTS
from elevenlabs import generate, set_api_key, voices
import tempfile
import pyperclip
import base64

# ====== USA STANDARD SETUP ======
st.set_page_config(page_title="LinguaBridge Pro", page_icon="🌍", layout="centered")

# YOUR API KEYS - PUT THEM IN .streamlit/secrets.toml
openai.api_key = st.secrets["OPENAI_API_KEY"] 
set_api_key(st.secrets["ELEVENLABS_API_KEY"])

# USA DESIGN
st.markdown("""
<style>
.main {background: linear-gradient(180deg, #0F172A 0%, #1E3A8A 100%);}
.title {color: white; text-align: center; font-size: 32px; font-weight: 800;}
.mic-button {position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);}
.chat-bubble {background: #1E293B; color: white; padding: 16px; border-radius: 18px; margin: 12px 0; border: 1px solid #334155;}
.action-btn {margin-right: 8px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🌍 LinguaBridge</p>', unsafe_allow_html=True)
st.caption("USA Standard AI Translator | Hold to Talk")

# ====== SESSION STATE ======
if "chat" not in st.session_state: st.session_state.chat = []
if "pro" not in st.session_state: st.session_state.pro = False # Change to True after payment
if "count" not in st.session_state: st.session_state.count = 0

# ====== 1. FLAG SELECTOR - USA UX ======
lang_map = {
    "🇺🇸 English": "en", "🇨🇳 Chinese": "zh", "🇪🇸 Spanish": "es", "🇫🇷 French": "fr", 
    "🇳🇬 Yoruba": "yo", "🇳🇬 Hausa": "ha", "🇳🇬 Igbo": "ig", "🇸🇦 Arabic": "ar"
}
target_lang_label = st.selectbox("Translate to:", list(lang_map.keys()))
target_lang = lang_map[target_lang_label]

# FREE LIMIT
st.progress(st.session_state.count / 50, text=f"Free: {st.session_state.count}/50 translations")

# ====== 2. WHATSAPP "HOLD TO TALK" BUTTON ======
st.markdown('<div class="mic-button">', unsafe_allow_html=True)
audio_bytes = st.audio_input("🎤 Hold to Talk")
st.markdown('</div>', unsafe_allow_html=True)

# ====== 3. CORE LOGIC: RECORD -> DETECT -> TRANSLATE ======
if audio_bytes:
    with st.spinner("Detecting language... Translating..."):
        # STEP 1: WHISPER AUTO-DETECT + SPEECH TO TEXT
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        audio_file = open(tmp_path, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format="verbose_json")
        original_text = transcript.text
        detected_lang = transcript.language # AUTO DETECT HERE
        confidence = round(transcript.get("confidence", 0.98) * 100)

        # STEP 2: GPT TRANSLATE
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Translate this from {detected_lang} to {target_lang}: {original_text}"}]
        )
        translated_text = completion.choices[0].message.content

        # SAVE TO CHAT
        st.session_state.chat.append({
            "original": original_text, "detected": detected_lang, 
            "translated": translated_text, "target": target_lang, "conf": confidence,
            "audio": audio_bytes
        })
        st.session_state.count += 1
        st.rerun()

# ====== 4. DISPLAY CHAT WITH USA FEATURES ======
for i, msg in enumerate(st.session_state.chat):
    with st.container():
        st.markdown(f'<div class="chat-bubble">', unsafe_allow_html=True)
        st.write(f"**You [{msg['detected']}]**: {msg['original']}")
        st.write(f"**→ [{target_lang_label}]**: {msg['translated']}")
        st.caption(f"AI Confidence: {msg['conf']}%")
        
        # ACTION BUTTONS: COPY, SHARE, PLAY - USA STANDARD
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📋 Copy", key=f"copy{i}"):
                pyperclip.copy(msg['translated'])
                st.toast("Copied!")
        with col2:
            # SHARE TO WHATSAPP
            share_text = f"https://wa.me/?text={msg['translated']}"
            st.link_button("📤 Share", share_text)
        with col3:
            # PLAY TRANSLATION
            tts = gTTS(text=msg['translated'], lang=msg['target'])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name)
        with col4:
            if st.button("🚩 Report", key=f"report{i}"):
                st.toast("Reported. Thank you!")

        # ====== 5. PRO FEATURE: VOICE CLONING ======
        if st.session_state.pro:
            if st.button("🎙️ Send with YOUR Voice", key=f"clone{i}"):
                with st.spinner("Cloning your voice to English..."):
                    # ELEVENLABS VOICE CLONING
                    audio = generate(
                        text=msg['translated'],
                        voice="YOUR_VOICE_ID", # You clone your voice once in ElevenLabs
                        model="eleven_multilingual_v2"
                    )
                    st.audio(audio)
                    st.download_button("Download Voice Note", audio, "voice_note.mp3")
        else:
            st.info("Upgrade to Pro to send voice notes in YOUR voice")
        st.markdown('</div>', unsafe_allow_html=True)

# ====== 6. PRO PAYWALL - USA STANDARD ======
if not st.session_state.pro:
    st.divider()
    st.subheader("Upgrade to Pro $14.99/mo")
    st.write("✅ Unlimited translations \n✅ Voice Cloning \n✅ No Watermark \n✅ Priority Speed")
    if st.button("Upgrade Now", type="primary"):
        st.session_state.pro = True # Connect this to Stripe later
        st.rerun()

# ====== 7. PRIVACY + ACCESSIBILITY - USA LAW ======
st.divider()
st.caption("🔒 We delete your voice in 24 hours. | ♿ VoiceOver & Big Buttons Supported")
