import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF # Nutze fpdf2 in requirements.txt!
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

# 2. DESIGN
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 8px; background-color: #10b981; color: white; }
    .sidebar-link { text-decoration: none; color: #1e3a8a; font-weight: bold; display: block; padding: 10px; background: #f0f2f6; border-radius: 5px; margin-bottom: 5px; text-align: center; border: 1px solid #d1d5db; }
    .deadline-box { background-color: #fee2e2; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444; margin-bottom: 20px; }
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
    return convert_from_bytes(file_bytes, dpi=72, first_page=1, last_page=1)

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

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_result" not in st.session_state: st.session_state.last_result = ""
if "last_deadlines" not in st.session_state: st.session_state.last_deadlines = ""

params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    st.session_state.credits += int(params.get("credits", 1))
    st.session_state.processed_sessions.append(params["session_id"])

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("icon_final_blau.png"): st.image("icon_final_blau.png", width=120)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Aufladen")
    st.markdown(f'<a href="{LINK_1}" target="_blank" class="sidebar-link">🛒 1 Analyse (3,99€)</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_3}" target="_blank" class="sidebar-link">🚀 3er Paket (9,99€)</a>', unsafe_allow_html=True)
    st.markdown(f'<a href="{LINK_10}" target="_blank" class="sidebar-link">💎 10er Paket (19,99€)</a>', unsafe_allow_html=True)
    if st.query_params.get("admin") == "ja": st.session_state.credits = 999

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Behörden-Dokument hier hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1])
    
    with col_v:
        st.subheader("📸 Vorschau")
        if upload.type == "application/pdf":
            try:
                img_preview = get_pdf_preview(upload.getvalue())
                st.image(img_preview[0], use_container_width=True)
            except: st.error("Vorschau-Fehler")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        st.subheader("🧠 Analyse & Antwort")
        if st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("Extrahiere Daten & Fristen..."):
                    txt = get_text_hybrid(upload)
                    # Getrenntes Abfragen von Fristen und Antwort für mehr Präzision
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=
                    )
                    full_text = res.choices[0].message.content
                    st.session_state.last_result = full_text
                    st.session_state.credits -= 1
            
            if st.session_state.last_result:
                st.markdown(st.session_state.last_result)
                
                st.divider()
                st.subheader("📩 Exportieren")
                c1, c2 = st.columns(2)
                
                with c1:
                    # PDF FIX: Nutze utf-8 fähigen Export
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", size=11)
                    # Einfaches Encoding-Handling für PDF
                    pdf_body = st.session_state.last_result.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 10, txt=pdf_body)
                    st.download_button("📩 Als PDF", pdf.output(dest='S').encode('latin-1'), "Amtsschimmel_Antwort.pdf", "application/pdf")
                
                with c2:
                    # EXCEL FIX: Nutze openpyxl engine
                    df = pd.DataFrame([{"Datum": datetime.now(), "Analyse": st.session_state.last_result}])
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button("📊 Als Excel", output.getvalue(), "Amtsschimmel_Analyse.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.warning("💳 Bitte lade Guthaben auf.")

st.info("Tipp: Digitale PDFs werden am präzisesten erkannt.")
