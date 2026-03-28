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

# 1. SEITEN-KONFIGURATION (Mobile Responsive)
st.set_page_config(
    page_title="Amtsschimmel-Killer", 
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CUSTOM CSS FÜR MOBILE DESIGN (Buttons & Abstände)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1e3a8a;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stDownloadButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #10b981;
        color: white;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
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

# TESSERACT PFAD
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---

def get_text_hybrid(uploaded_file):
    """Hybrid-Extraktion: Digitaler Text zuerst, dann OCR."""
    text = ""
    file_bytes = uploaded_file.getvalue()
    
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        
        if len(text.strip()) < 50: # Falls kaum Text erkannt (Scan)
            images = convert_from_bytes(file_bytes, dpi=200)
            text = "\n".join([pytesseract.image_to_string(img, lang='deu') for img in images])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file), lang='deu')
    return text.strip()

class PDF_Gen(FPDF):
    def header(self):
        if os.path.exists("icon_final_blau.png"):
            self.image("icon_final_blau.png", 170, 8, 25)
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'Amtsschimmel-Killer Dokumentation', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Erstellt am {datetime.now().strftime("%d.%m.%Y")} | Seite {self.page_no()}', 0, 0, 'C')

def create_pdf(content):
    pdf = PDF_Gen()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    # Zeichen-Encoding für PDF
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, txt=safe_text)
    return pdf.output()

# --- 4. SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "preview_cached" not in st.session_state: st.session_state.preview_cached = None
if "last_uploaded_name" not in st.session_state: st.session_state.last_uploaded_name = None

# Admin Check
is_admin = st.query_params.get("admin") == "ja"
if is_admin: st.session_state.credits = 999

# --- 5. SIDEBAR (Mobile einklappbar) ---
with st.sidebar:
    if os.path.exists("icon_final_blau.png"): st.image("icon_final_blau.png", width=120)
    st.header("👤 Dein Konto")
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    
    if st.session_state.credits <= 0:
        st.subheader("💳 Aufladen")
        st.markdown(f'[🛒 1 Analyse (3,99€)]({LINK_1})', unsafe_allow_html=True)
        st.markdown(f'[🚀 3er Spar-Paket (9,99€)]({LINK_3})', unsafe_allow_html=True)
        st.markdown(f'[💎 10er Sorglos (19,99€)]({LINK_10})', unsafe_allow_html=True)
    st.divider()

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")
st.caption("Behördensprache verstehen & rechtssicher antworten.")

upload = st.file_uploader("Dokument hochladen (PDF oder Bild)", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    # Schnelle Vorschau-Logik
    if st.session_state.last_uploaded_name != upload.name:
        if upload.type == "application/pdf":
            with st.spinner("Erzeuge Vorschau..."):
                preview_pages = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.session_state.preview_cached = preview_pages[0]
        else:
            st.session_state.preview_cached = Image.open(upload)
        st.session_state.last_uploaded_name = upload.name

    # Layout für Mobile: Vorschau oben, Button darunter
    st.image(st.session_state.preview_cached, caption="Dokument-Vorschau", use_container_width=True)

    if st.session_state.credits > 0:
        if st.button("🚀 JETZT ANALYSIEREN"):
            with st.spinner("KI liest und verfasst Antwort (ca. 10 Sek)..."):
                extracted_text = get_text_hybrid(upload)
                
                if extracted_text:
                    try:
                        # Verbesserter Prompt für LÄNGE und JURISTISCHE TIEFE
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Du bist ein spezialisierter Rechtsanwalt für Verwaltungsrecht. Verfasse extrem ausführliche, professionelle Schriftsätze mit klaren Rechtsanträgen."},
                                {"role": "user", "content": f"""Analysiere diesen Text und erstelle ein SEHR LANGES Antwortschreiben (mind. 500 Wörter).
                                1. Fasse den Sachverhalt präzise zusammen.
                                2. Nenne rechtliche Bedenken oder Fristprobleme.
                                3. Verfasse ein versandfertiges Antwortschreiben inkl. Platzhaltern [Name], [Datum] etc.
                                Nutze Fachbegriffe wie 'Akteneinsicht gemäß VwVfG', 'Widerspruch' oder 'Fristverlängerung'.
                                
                                Dokument-Text:
                                {extracted_text}"""}
                            ],
                            temperature=0.4
                        )
                        
                        ergebnis = response.choices.message.content
                        st.session_state.credits -= 1
                        
                        st.success("✅ Analyse fertig!")
                        st.markdown("### 📝 Analyse & Antwortschreiben")
                        st.write(ergebnis)
                        
                        # Download Section
                        pdf_data = create_pdf(ergebnis)
                        st.download_button("📩 Download als PDF", data=pdf_data, file_name="Antwortschreiben.pdf", mime="application/pdf")
                        
                        # Cleanup Session
                        st.session_state.last_uploaded_name = None 
                        
                    except Exception as e:
                        st.error(f"KI-Fehler: {e}")
                else:
                    st.error("Text konnte nicht gelesen werden. Ist das Dokument zu unscharf?")
    else:
        st.warning("💳 Kein Guthaben mehr. Bitte lade dein Konto in der Seitenleiste (Sidebar) auf.")

st.info("Hinweis: Digitale PDFs werden sofort verarbeitet. Scans können durch das OCR etwas länger dauern.")
