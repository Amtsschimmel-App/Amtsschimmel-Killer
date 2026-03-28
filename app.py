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
    # Deine Stripe Payment Links
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

# --- 4. ZAHLUNGS-VALIDIERUNG (Ersatz für Webhook) ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Prüfe URL Parameter nach Rückkehr von Stripe
params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status == "paid":
            # Extrahiere Paket-Größe aus Metadata oder Query-Param
            amount = int(params.get("credits", 1))
            st.session_state.credits += amount
            st.session_state.processed_sessions.append(params["session_id"])
            st.toast(f"✅ {amount} Analysen gutgeschrieben!", icon="✨")
    except Exception as e:
        st.sidebar.error("Zahlung konnte nicht verifiziert werden.")

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header("👤 Dein Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    
    st.subheader("💳 Aufladen")
    # WICHTIG: In Stripe Dashboard bei "Payment Links" die "Pass-through-Parameter" aktivieren
    # Oder einfach die Links hier direkt mit ?session_id={CHECKOUT_SESSION_ID} nutzen (falls möglich)
    st.markdown(f'[🛒 1 Analyse (3,99€)]({STRIPE_LINKS["1"]})', unsafe_allow_html=True)
    st.markdown(f'[🚀 3er Spar-Paket (9,99€)]({STRIPE_LINKS["3"]})', unsafe_allow_html=True)
    st.markdown(f'[💎 10er Sorglos (19,99€)]({STRIPE_LINKS["10"]})', unsafe_allow_html=True)
    
    if st.query_params.get("admin") == "ja":
        st.session_state.credits = 999
        st.success("Admin-Modus: Unbegrenzt")

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    st.info("Vorschau wird geladen...")
    # (Hier käme die Vorschau-Logik von oben hin)
    
    if st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("KI verfasst ausführliche Antwort..."):
                extracted_text = get_text_hybrid(upload)
                if extracted_text:
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Verfasse ein sehr ausführliches Antwortschreiben (mind. 500 Wörter) im juristischen Stil."},
                            {"role": "user", "content": f"Text: {extracted_text}"}
                        ]
                    )
                    st.markdown("### Ergebnis:")
                    st.write(res.choices.message.content)
                    st.session_state.credits -= 1
                    st.rerun()
    else:
        st.warning("Kein Guthaben. Bitte links aufladen.")
