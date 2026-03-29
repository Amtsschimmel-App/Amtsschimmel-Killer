import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import shutil
import stripe
from datetime import datetime
import gc 

# 1. KONFIGURATION & DESIGN
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; scale: 1.02; }
    .result-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); white-space: pre-wrap; }
    .legal-box { font-size: 0.85em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE & ADMIN
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin Check
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

# 3. FUNKTIONEN
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50:
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def analyze_letter(raw_text, language):
    sys_p = f"Du bist Rechtsexperte. Analysiere den Brief. Sprache der Antwort: {language}. Liste FRISTEN auf und erstelle einen professionellen ANTWORTTEXT mit Platzhaltern."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

def speak_text(text, voice_type):
    voice_map = {"Weiblich": "nova", "Männlich": "onyx"}
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice_map.get(voice_type, "nova"),
        input=text[:4000]
    )
    return response.content

# 4. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    st.subheader("Einstellungen")
    lang_choice = st.radio("Antwort-Sprache", ["Deutsch", "English"], horizontal=True)
    voice_choice = st.selectbox("Vorlese-Stimme", ["Weiblich", "Männlich"])
    
    st.divider()
    st.subheader("Guthaben aufladen (Kein Abo)")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small style="color:#16a34a;">✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# 5. HAUPTBEREICH
t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ & Hilfe"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    if st.session_state.last_analysis:
        if st.button("🔄 Nächsten Brief bearbeiten"):
            st.session_state.last_analysis = ""; st.rerun()

    if not st.session_state.last_analysis:
        upload = st.file_uploader("Brief hochladen (PDF/Bild)", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type != "application/pdf": st.image(upload, width=300)
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("KI arbeitet..."):
                        raw = get_text_hybrid(upload)
                        st.session_state.last_analysis = analyze_letter(raw, lang_choice)
                        st.session_state.credits -= 1
                        st.rerun()
            else: st.error("Guthaben leer.")

    if st.session_state.last_analysis:
        st.success(f"Analyse ({lang_choice}):")
        st.markdown(f'<div class="result-box">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        
        # VORLESE-FUNKTION
        if st.button(f"🔊 Antwort vorlesen ({voice_choice})"):
            with st.spinner("Audio wird generiert..."):
                audio_content = speak_text(st.session_state.last_analysis, voice_choice)
                st.audio(audio_content, format="audio/mp3")
        
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Download .txt", st.session_state.last_analysis, "antwort.txt")

with t2:
    st.subheader("⚡ Schnelle Vorlagen")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Fristverlängerung...", language="text")

with t3:
    st.subheader("❓ FAQ")
    st.write("**Ist das ein Abo?** Nein. Jede Zahlung ist eine Einmalzahlung. Keine automatische Verlängerung.")
    st.write("**Sicherheit?** Dokumente werden verschlüsselt verarbeitet und sofort gelöscht.")

# 6. FOOTER
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"**Amtsschimmel-Killer**<br>Betreiberin: Elisabeth Reinecke<br>Ringelsweide 9, 40223 Düsseldorf<br>Telefon: +49 211 15821329<br>E-Mail: amtsschimmel-killer@proton.me<br>Web: amtsschimmel-killer.streamlit.app<br><br>Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-Texte.", unsafe_allow_html=True)
with c2:
    with st.expander("⚖️ Datenschutz (DSGVO)"):
        st.markdown("1. Daten werden vertraulich behandelt. 2. App-Hosting auf Streamlit Cloud. 3. Dokumente werden via TLS an OpenAI zur Analyse übertragen (keine Speicherung). 4. Zahlungen via Stripe (Einmalzahlung). 5. Recht auf Auskunft & Löschung.")
