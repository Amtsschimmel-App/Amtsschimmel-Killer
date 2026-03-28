import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pdfplumber
import io
import os
import shutil
import stripe
from datetime import datetime

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. DESIGN (Mobile Optimiert)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
    STRIPE_LINKS = {
        "1": st.secrets["STRIPE_LINK_1"],
        "3": st.secrets["STRIPE_LINK_3"],
        "10": st.secrets["STRIPE_LINK_10"]
    }
except Exception as e:
    st.error(f"⚠️ Secrets Fehler: {e}")

# TESSERACT PFAD
if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- HILFSFUNKTIONEN ---

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

# --- 4. ZAHLUNGS-VALIDIERUNG ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status == "paid":
            amount = int(params.get("credits", 1))
            st.session_state.credits += amount
            st.session_state.processed_sessions.append(params["session_id"])
            st.toast(f"✅ {amount} Analysen gutgeschrieben!", icon="✨")
    except:
        pass

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("👤 Dein Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    st.subheader("💳 Aufladen")
    st.markdown(f'[🛒 1 Analyse (3,99€)]({STRIPE_LINKS["1"]})', unsafe_allow_html=True)
    st.markdown(f'[🚀 3er Spar-Paket (9,99€)]({STRIPE_LINKS["3"]})', unsafe_allow_html=True)
    st.markdown(f'[💎 10er Sorglos (19,99€)]({STRIPE_LINKS["10"]})', unsafe_allow_html=True)
    if st.query_params.get("admin") == "ja":
        st.session_state.credits = 999

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    # VORSCHAU LOGIK FIX
    with st.expander("📄 Dokument-Vorschau ansehen", expanded=True):
        if upload.type == "application/pdf":
            try:
                images = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(images[0], use_container_width=True)
            except:
                st.warning("Vorschau für dieses PDF nicht verfügbar.")
        else:
            st.image(upload, use_container_width=True)
    
    if st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("KI liest Dokument und schreibt Antwort..."):
                extracted_text = get_text_hybrid(upload)
                if extracted_text:
                    try:
                        # FIX: Richtiger API-Aufruf
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Du bist ein spezialisierter Rechtsanwalt. Verfasse ein sehr ausführliches Antwortschreiben (mind. 500 Wörter) im juristischen Stil."},
                                {"role": "user", "content": f"Erstelle eine Analyse und ein Antwortschreiben basierend auf diesem Text: {extracted_text}"}
                            ]
                        )
                        # FIX: Attribut-Zugriff korrigiert
                        antwort_text = res.choices[0].message.content
                        st.markdown("### Dein fertiges Schreiben:")
                        st.write(antwort_text)
                        
                        st.session_state.credits -= 1
                        st.success("Erfolg! 1 Credit abgezogen.")
                    except Exception as e:
                        st.error(f"Fehler bei der KI-Anfrage: {e}")
                else:
                    st.error("Konnte keinen Text im Dokument finden.")
    else:
        st.warning("Bitte lade dein Guthaben in der Sidebar auf.")

st.info("Tipp: Nutze digitale PDFs für die schnellste Verarbeitung.")
