import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF # WICHTIG: In requirements.txt muss 'fpdf2' stehen!
import pdfplumber
from pdf2image import convert_from_bytes
import pandas as pd
import io
import os
import shutil
import stripe
from datetime import datetime

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; background-color: #10b981; color: white; font-weight: bold; }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 12px; color: #1e3a8a !important; text-align: center; border: 1px solid #d1d5db; }
    .buy-title { font-weight: bold; font-size: 1.1em; display: block; }
    .buy-subtitle { font-size: 0.85em; color: #64748b; display: block; }
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

# Zahlungs-Check via URL
params = st.query_params
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        session = stripe.checkout.Session.retrieve(params["session_id"])
        if session.payment_status in ["paid", "no_payment_required"]:
            to_add = int(params.get("pack", 1))
            st.session_state.credits += to_add
            st.session_state.processed_sessions.append(params["session_id"])
            st.toast(f"✅ {to_add} Analyse(n) freigeschaltet!", icon="✨")
    except: pass

# --- 5. SIDEBAR ---
with st.sidebar:
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    st.subheader("💳 Guthaben laden")
    
    links = [("📄 1 Analyse", LINK_1, "3,99 € | Einmalzahlung"),
             ("🚀 Spar-Paket (3)", LINK_3, "9,99 € | Einmalzahlung"),
             ("💎 Sorglos (10)", LINK_10, "19,99 € | Einmalzahlung")]
             
    for title, link, sub in links:
        st.markdown(f'<a href="{link}" target="_blank" class="buy-button"><span class="buy-title">{title}</span><span class="buy-subtitle">{sub}</span></a>', unsafe_allow_html=True)
    
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
                images = convert_from_bytes(upload.getvalue(), dpi=72, first_page=1, last_page=1)
                st.image(images, use_container_width=True)
            except: st.error("Vorschau nicht verfügbar.")
        else:
            st.image(upload, use_container_width=True)

    with col_a:
        st.subheader("🧠 Analyse-Ergebnis")
        
        if st.session_state.last_result:
            # TEXT ANZEIGEN
            st.markdown(st.session_state.last_result)
            st.divider()
            
            # DOWNLOAD BEREICH
            c1, c2 = st.columns(2)
            
            # PDF GENERIERUNG
            with c1:
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("helvetica", size=11)
                    # FIX: Euro-Symbol und Sonderzeichen bereinigen
                    clean_text = st.session_state.last_result.replace("€", "Euro").replace("–", "-").replace("„", '"').replace("“", '"')
                    # FIX: latin-1 encoding sicherstellen
                    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
                    
                    # FIX: bytearray zu bytes konvertieren
                    pdf_bytes = bytes(pdf.output()) 
                    
                    st.download_button(
                        label="📩 PDF laden",
                        data=pdf_bytes,
                        file_name="Amtsschimmel_Antwort.pdf",
                        mime="application/pdf"
                    )
                except Exception as e: 
                    st.error(f"PDF-Fehler: {e}")
            
            # EXCEL GENERIERUNG
            with c2:
                try:
                    df = pd.DataFrame([{"Analyse": st.session_state.last_result, "Datum": datetime.now().strftime("%d.%m.%Y %H:%M")}])
                    excel_buffer = io.BytesIO()
                    # engine='openpyxl' ist wichtig
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    
                    st.download_button(
                        label="📊 Excel laden",
                        data=excel_buffer.getvalue(),
                        file_name="Amtsschimmel_Analyse.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e: 
                    st.error(f"Excel-Fehler: {e}")
            
            if st.button("🔄 Nächstes Dokument"):
                st.session_state.last_result = ""
                st.rerun()

        elif st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("KI erstellt Analyse & Antwortschreiben..."):
                    try:
                        extracted = get_text_hybrid(upload)
                        res = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "Du bist ein Fachanwalt. \n\nSTRUKTUR DER ANTWORT:\n1. Zuerst: Eine Liste aller FRISTEN in fett.\n2. Dann: Ein formelles ANTWORTSCHREIBEN.\n\nDAS ANTWORTSCHREIBEN MUSS MIT EINER ÜBERSCHRIFT BEGINNEN, Z.B.:\n'**BETREFF: ANTWORTSCHREIBEN ZUM SCHREIBEN VOM [DATUM] / AZ: [NUMMER]**'\n\nSchreibe sehr ausführlich (min. 600 Wörter), juristisch fundiert und höflich aber bestimmt."},
                                {"role": "user", "content": f"Hier ist der Text des Dokuments: {extracted}"}
                            ]
                        )
                        st.session_state.last_result = res.choices[0].message.content
                        st.session_state.credits -= 1
                        st.rerun()
                    except Exception as e: 
                        st.error(f"KI-Fehler: {e}")
        else:
            st.warning("💳 Bitte lade dein Guthaben in der Sidebar auf.")

st.info("Hinweis: Diese KI-Analyse ersetzt keine individuelle Rechtsberatung.")
