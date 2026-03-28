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

# 2. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
    STRIPE_LINKS = {"1": st.secrets["STRIPE_LINK_1"], "3": st.secrets["STRIPE_LINK_3"], "10": st.secrets["STRIPE_LINK_10"]}
except Exception as e:
    st.error(f"Konfigurationsfehler: {e}")

if shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

# --- HILFSFUNKTIONEN (CACHED FÜR SPEED) ---

@st.cache_data
def get_pdf_preview(file_bytes):
    """Erzeugt schnell ein Vorschaubild der ersten Seite."""
    images = convert_from_bytes(file_bytes, dpi=72, first_page=1, last_page=1)
    return images[0]

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

def create_pdf_download(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Säuberung für PDF-Export (Latin-1)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def create_excel_download(text):
    df = pd.DataFrame([{"Analyse_Datum": datetime.now().strftime("%d.%m.%Y"), "Ergebnis": text}])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- 3. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "last_result" not in st.session_state: st.session_state.last_result = None

# Stripe Check
params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    st.session_state.credits += int(params.get("credits", 1))
    st.session_state.processed_sessions.append(params["session_id"])

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("👤 Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Aufladen")
    st.markdown(f'[🛒 1er ({STRIPE_LINKS["1"]})]( {STRIPE_LINKS["1"]} )', unsafe_allow_html=True)
    st.markdown(f'[🚀 3er ({STRIPE_LINKS["3"]})]( {STRIPE_LINKS["3"]} )', unsafe_allow_html=True)
    if st.query_params.get("admin") == "ja": st.session_state.credits = 999

# --- 5. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_left, col_right = st.columns([1, 1]) # Zwei Spalten Layout
    
    with col_left:
        st.subheader("📸 Vorschau")
        if upload.type == "application/pdf":
            img_preview = get_pdf_preview(upload.getvalue())
            st.image(img_preview, use_container_width=True)
        else:
            st.image(upload, use_container_width=True)

    with col_right:
        st.subheader("🧠 Analyse & Antwort")
        if st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("KI arbeitet..."):
                    raw_text = get_text_hybrid(upload)
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Du bist Fachanwalt. Erstelle ein EXTREM ausführliches Antwortschreiben (mind. 600 Wörter) mit rechtlichen Begründungen."},
                            {"role": "user", "content": f"Analysiere: {raw_text}"}
                        ]
                    )
                    st.session_state.last_result = res.choices[0].message.content
                    st.session_state.credits -= 1
            
            if st.session_state.last_result:
                st.write(st.session_state.last_result)
                
                st.divider()
                st.subheader("📩 Exportieren")
                c1, c2 = st.columns(2)
                with c1:
                    pdf_data = create_pdf_download(st.session_state.last_result)
                    st.download_button("📄 PDF Download", pdf_data, "Antwort.pdf", "application/pdf")
                with c2:
                    xlsx_data = create_excel_download(st.session_state.last_result)
                    st.download_button("📊 Excel Download", xlsx_data, "Analyse.xlsx", "application/vnd.ms-excel")
        else:
            st.warning("Kein Guthaben vorhanden.")

st.info("Hinweis: Durch Caching lädt die Vorschau beim zweiten Mal blitzschnell.")
