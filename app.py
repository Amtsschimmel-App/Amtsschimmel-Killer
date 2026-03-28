import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF 
import pdfplumber
from pdf2image import convert_from_bytes
import pandas as pd
import io
import os
import shutil
import stripe
from datetime import datetime
from openpyxl.styles import Alignment

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; font-weight: bold; }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 2px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; transition: 0.3s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; }
    .buy-title { font-weight: bold; font-size: 1.1em; display: block; margin-bottom: 2px; }
    .buy-subtitle { font-size: 0.85em; color: #64748b; display: block; font-weight: normal; }
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

params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            to_add = int(params.get("pack", 1))
            st.session_state.credits += to_add
            st.session_state.processed_sessions.append(params["session_id"])
            st.toast(f"✅ {to_add} Analyse(n) freigeschaltet!", icon="✨")
            st.query_params.clear()
    except: pass

# --- 5. SIDEBAR ---
with st.sidebar:
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Guthaben laden")
    st.caption("Einmalzahlung • Kein Abo")
    
    links = [("📄 Einzel-Analyse", LINK_1, "3,99 € | KEIN ABO"),
             ("🚀 Spar-Paket (3 Scans)", LINK_3, "9,99 € | KEIN ABO"),
             ("💎 Sorglos-Paket (10 Scans)", LINK_10, "19,99 € | KEIN ABO")]
             
    for title, link, sub in links:
        st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><span class="buy-title">{title}</span><span class="buy-subtitle">{sub}</span></a>', unsafe_allow_html=True)
    
    if params.get("admin") == "ja": st.session_state.credits = 999

# --- 6. HAUPTSEITE ---
st.title("Amtsschimmel-Killer 📄🚀")

upload = st.file_uploader("Behörden-Dokument hier hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_v, col_a = st.columns([1, 1.5])
    with col_v:
        st.subheader("📸 Vorschau")
        if upload.type == "application/pdf":
            try:
                images = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(images, use_container_width=True)
            except: st.info("Vorschau wird generiert...")
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
                    pdf.set_font("helvetica", size=11)
                    clean_text = st.session_state.last_result.replace("€", "Euro").replace("–", "-").replace("„", '"').replace("“", '"').replace("✅", "OK")
                    pdf.multi_cell(0, 8, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
                    st.download_button("📩 PDF laden", bytes(pdf.output()), "Antwortschreiben.pdf", "application/pdf")
                except Exception as e: st.error(f"PDF-Fehler: {e}")
            
            with c2:
                try:
                    df = pd.DataFrame([{"Analyse": st.session_state.last_result, "Datum": datetime.now().strftime("%d.%m.%Y")}])
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Ergebnis')
                        worksheet = writer.sheets['Ergebnis']
                        # Breite der Spalte A auf 120 setzen
                        worksheet.column_dimensions['A'].width = 120
                        # Zeilenumbruch für alle Zellen in Spalte A aktivieren
                        for row in worksheet.iter_rows(min_row=2, max_col=1):
                            for cell in row:
                                cell.alignment = Alignment(wrap_text=True, vertical='top')
                    
                    st.download_button("📊 Excel laden", excel_buffer.getvalue(), "Analyse.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e: st.error(f"Excel-Fehler: {e}")
            
            if st.button("🔄 Nächstes Dokument"):
                st.session_state.last_result = ""
                st.rerun()

        elif st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("KI arbeitet..."):
                    try:
                        extracted = get_text_hybrid(upload)
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Du bist Fachanwalt. 1. Fristen fett auflisten. 2. Formelles Antwortschreiben (600+ Wörter) mit fetter Betreffzeile."},
                                {"role": "user", "content": f"Text: {extracted}"}
                            ]
                        )
                        st.session_state.last_result = res.choices[0].message.content
                        st.session_state.credits -= 1
                        st.rerun()
                    except Exception as e: st.error(f"KI-Fehler: {e}")
        else:
            st.warning("💳 Bitte Guthaben laden (KEIN ABO).")

st.info("Hinweis: KI-basierte Analyse. Keine Rechtsberatung.")
