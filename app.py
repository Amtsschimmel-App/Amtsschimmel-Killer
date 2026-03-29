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
    .legal-box { font-size: 0.85em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .result-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE & ADMIN LOGIK
if "credits" not in st.session_state: st.session_state.credits = 0
if "last_analysis" not in st.session_state: st.session_state.last_analysis = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
# Admin-Check (999 Scans)
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999
    st.toast("🔓 ADMIN-MODUS AKTIV")

# Stripe-Rückkehr
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    pack = int(params.get("pack", 1))
    st.session_state.credits += pack
    st.session_state.processed_sessions.append(params["session_id"])
    st.balloons()

# 3. HILFSFUNKTIONEN (KI & OCR)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50: # OCR falls PDF nur Bilder enthält
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

def analyze_letter(raw_text):
    sys_p = "Du bist Rechtsexperte. Analysiere den Brief. Liste FRISTEN (Datum) und erstelle einen professionellen ANTWORTTEXT mit Platzhaltern für [Name] und [Aktenzeichen]."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

# 4. SIDEBAR
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung</small></a>', unsafe_allow_html=True)

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
            # Dokumentvorschau
            if upload.type == "application/pdf":
                st.info("PDF hochgeladen.")
            else:
                st.image(upload, width=300)
            
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse starten"):
                    with st.spinner("Amtsschimmel wird vertrieben..."):
                        raw = get_text_hybrid(upload)
                        st.session_state.last_analysis = analyze_letter(raw)
                        st.session_state.credits -= 1
                        st.rerun()
            else: st.error("Bitte Guthaben aufladen.")

    if st.session_state.last_analysis:
        st.success("Analyse & Antwort:")
        st.markdown(f'<div class="result-box">{st.session_state.last_analysis}</div>', unsafe_allow_html=True)
        st.code(st.session_state.last_analysis, language="text")
        st.download_button("💾 Download", st.session_state.last_analysis, "antwort.txt")

with t2:
    st.subheader("⚡ Schnelle Vorlagen")
    with st.expander("⏳ Fristverlängerung"):
        st.code("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Fristverlängerung...", language="text")

with t3:
    st.subheader("❓ FAQ")
    st.write("**Ist das ein Abo?** Nein, reine Einmalzahlung.")
    st.write("**Datenschutz?** Scans werden nach der Analyse gelöscht.")

# 6. FOOTER
st.divider()
c1, c2 = st.columns(2)
with c1:
    with st.expander("🏢 Impressum"):
        st.markdown(f"Elisabeth Reinecke, Ringelsweide 9, 40223 Düsseldorf. Tel: +49 211 15821329. E-Mail: amtsschimmel-killer@proton.me")
with c2:
    with st.expander("⚖️ Datenschutz (DSGVO)"):
        st.markdown("Verantwortlich: Elisabeth Reinecke. Wir nutzen SSL-Verschlüsselung. Dokumente werden zur Analyse an OpenAI übertragen und nicht dauerhaft gespeichert. Zahlungen via Stripe.")
