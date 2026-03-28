import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pdfplumber
import pandas as pd
import io
import os
import shutil
import stripe
from datetime import datetime

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. DESIGN (Optimierte Sidebar-Buttons mit Fokus auf Transparenz)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 8px; background-color: #10b981; color: white; }
    
    .buy-button {
        text-decoration: none;
        display: block;
        padding: 12px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-bottom: 12px;
        transition: all 0.2s;
        color: #1e3a8a !important;
        text-align: center;
    }
    .buy-button:hover {
        background: #f1f5f9;
        border-color: #1e3a8a;
        transform: translateY(-1px);
    }
    .buy-title { font-weight: bold; font-size: 1.1em; display: block; }
    .buy-subtitle { font-size: 0.85em; color: #64748b; display: block; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 3. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
    LINK_1 = st.secrets["STRIPE_LINK_1"]
    LINK_3 = st.secrets["STRIPE_LINK_3"]
    LINK_10 = st.secrets["STRIPE_LINK_10"]
except Exception as e:
    st.error(f"⚠️ Konfigurationsfehler: {e}")

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- HILFSFUNKTIONEN ---

@st.cache_data
def get_pdf_preview(file_bytes):
    images = convert_from_bytes(file_bytes, dpi=72, first_page=1, last_page=1)
    return images if images else None

def get_text_hybrid(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        if len(text.strip()) < 50:
            images = convert_from_bytes(file_bytes, dpi=150)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

# --- 4. SESSION STATE & ZAHLUNGS-LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_result" not in st.session_state: st.session_state.last_result = ""

params = st.query_params
current_sid = params.get("session_id")

if current_sid and current_sid not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(current_sid)
        if session.payment_status in ["paid", "no_payment_required"]:
            to_add = int(params.get("pack", params.get("credits", 1)))
            st.session_state.credits += to_add
            st.session_state.processed_sessions.append(current_sid)
            st.toast(f"✅ {to_add} Analyse(n) freigeschaltet!", icon="✨")
    except: pass

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("icon_final_blau.png"): st.image("icon_final_blau.png", width=120)
    st.metric("Verfügbares Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Guthaben laden")
    
    # Buttons mit explizitem Hinweis: KEIN ABO / EINMALZAHLUNG
    st.markdown(f'''
        <a href="{LINK_1}" target="_blank" class="buy-button">
            <span class="buy-title">📄 1 Analyse</span>
            <span class="buy-subtitle">3,99 € | Einmalzahlung | KEIN ABO</span>
        </a>
        <a href="{LINK_3}" target="_blank" class="buy-button">
            <span class="buy-title">🚀 Spar-Paket (3 Stück)</span>
            <span class="buy-subtitle">9,99 € | Einmalzahlung | KEIN ABO</span>
        </a>
        <a href="{LINK_10}" target="_blank" class="buy-button">
            <span class="buy-title">💎 Sorglos-Paket (10 Stück)</span>
            <span class="buy-subtitle">19,99 € | Einmalzahlung | KEIN ABO</span>
        </a>
    ''', unsafe_allow_html=True)
    
    if params.get("admin") == "ja": st.session_state.credits = 999

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Behörden-Dokument hier hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns(2)
    
    with col_v:
        st.subheader("📸 Vorschau")
        if upload.type == "application/pdf":
            try:
                img_preview = get_pdf_preview(upload.getvalue())
                if img_preview: st.image(img_preview, use_container_width=True)
            except: st.error("Vorschau-Fehler")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        st.subheader("🧠 Analyse-Ergebnis")
        
        if st.session_state.last_result:
            st.markdown(st.session_state.last_result)
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=10)
                    pdf_text = st.session_state.last_result.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, txt=pdf_text)
                    st.download_button("📩 PDF laden", pdf.output(dest='S').encode('latin-1'), "Antwortschreiben.pdf", "application/pdf")
                except: st.error("PDF Fehler")
            with c2:
                try:
                    df = pd.DataFrame([{"Inhalt": st.session_state.last_result}])
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button("📊 Excel laden", output.getvalue(), "Analyse.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except: st.error("Excel Fehler")
            
            if st.button("🔄 Nächstes Dokument"):
                st.session_state.last_result = ""
                st.rerun()

        elif st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("KI verfasst Antwort (ca. 20-30 Sek)..."):
                    try:
                        txt = get_text_hybrid(upload)
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Du bist Fachanwalt. Liste Fristen fett auf und schreibe ein langes Antwortschreiben (600+ Wörter)."},
                                {"role": "user", "content": f"Analysiere: {txt}"}
                            ],
                            temperature=0.3
                        )
                        st.session_state.last_result = response.choices.message.content
                        st.session_state.credits -= 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"KI-Fehler: {e}")
        else:
            st.warning("💳 Bitte lade dein Guthaben auf, um die Analyse zu starten.")

st.info("Tipp: Nutze digitale PDFs für die höchste Genauigkeit.")
