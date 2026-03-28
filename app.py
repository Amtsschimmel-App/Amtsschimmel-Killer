import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
from fpdf import FPDF
from pdf2image import convert_from_bytes
import pandas as pd
import io
import re
import os
from datetime import datetime
import shutil
import stripe
import numpy as np
import cv2

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG & SECRETS LADEN
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
    # Links aus Secrets laden
    LINK_1 = st.secrets["STRIPE_LINK_1"]
    LINK_3 = st.secrets["STRIPE_LINK_3"]
    LINK_10 = st.secrets["STRIPE_LINK_10"]
except Exception:
    st.error("⚠️ Secrets fehlen (API-Keys oder Stripe-Links)!")

# TESSERACT PFAD-FIX
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---
def remove_emojis(text):
    return text.encode('latin-1', 'ignore').decode('latin-1') if text else ""

def create_full_pdf(erk, fri, ant, ste, meta, fehler):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16); pdf.set_text_color(30, 58, 138)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=1, align='C'); pdf.ln(10)
    sections = [("Behörde", meta.get('behoerde', '-')), ("Aktenzeichen", meta.get('az', '-')), ("Erklärung", erk), ("Fristen", fri), ("Antwortentwurf", ant)]
    for title, content in sections:
        pdf.set_font("Arial", "B", 11); pdf.set_fill_color(240, 240, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        pdf.set_font("Arial", size=10); pdf.ln(2)
        pdf.multi_cell(0, 6, txt=remove_emojis(content))
        pdf.ln(4)
    return pdf.output(dest='S').encode('latin-1')

def create_excel(data_dict):
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        worksheet = writer.sheets['Analyse']
        wrap = writer.book.add_format({'text_wrap': True, 'valign': 'top'})
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 50, wrap)
    return output.getvalue()

# --- 3. CREDITS & MULTI-PAKET LOGIK ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "verified_sessions" not in st.session_state: st.session_state.verified_sessions = []

session_id = st.query_params.get("session_id")
pack_type = st.query_params.get("pack") 
is_admin = st.query_params.get("admin") == "ja"

if session_id and session_id not in st.session_state.verified_sessions:
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status == "paid":
            amount = int(pack_type) if pack_type else 1
            st.session_state.credits += amount
            st.session_state.verified_sessions.append(session_id)
            st.toast(f"✨ {amount} Analysen freigeschaltet!", icon="✅")
    except: st.sidebar.error("Zahlungs-Verifizierung fehlgeschlagen.")

if is_admin: st.session_state.credits = 999

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📄 Amtsschimmel-Killer")
    st.header("Dein Guthaben")
    st.metric("Verfügbare Analysen", st.session_state.credits)
    
    stripe_html = f'''
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="background: #f9fafb; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db;">
                <a href="{LINK_1}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; background:#f9fafb; color:black; border:1px solid #d1d5db; padding:8px; cursor:pointer; font-weight:bold;">Analyse (1 Dokument)</button></a>
                <p style="margin:0; font-size:10px; text-align:center; color:gray;">3,99 € | Einmalzahlung</p>
            </div>
            <div style="background: #10b981; padding: 10px; border-radius: 8px;">
                <a href="{LINK_3}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; background:#10b981; color:white; border:none; padding:10px; cursor:pointer; font-weight:bold;">Spar-Paket (3 Dokumente)</button></a>
                <p style="margin:0; font-size:10px; text-align:center; color:white;">9,99 € | KEIN ABO</p>
            </div>
            <div style="background: #1e3a8a; padding: 10px; border-radius: 8px;">
                <a href="{LINK_10}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; background:#1e3a8a; color:white; border:none; padding:8px; cursor:pointer; font-weight:bold;">Sorglos-Paket (10 Dokumente)</button></a>
                <p style="margin:0; font-size:10px; text-align:center; color:white;">19,99 € | KEIN ABO</p>
            </div>
        </div>
    '''

    if is_admin:
        with st.expander("🛠️ Stripe-Links testen"): st.markdown(stripe_html, unsafe_allow_html=True)
    elif st.session_state.credits <= 0:
        st.subheader("💳 Guthaben aufladen")
        st.markdown(stripe_html, unsafe_allow_html=True)
    
    st.divider()
    if "kosten" not in st.session_state: st.session_state.kosten = 0.0
    if is_admin:
        with st.expander("📊 Admin-Statistik"):
            st.metric("OpenAI API-Kosten", f"${st.session_state.kosten:.4f}")

# --- 5. HAUPT-LOGIK ---
st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Behörden-Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload:
    col_img, col_ana = st.columns(2)
    current_img = None
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            try:
                pages = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
                current_img = pages[0] if isinstance(pages, list) else pages
                st.image(current_img, use_container_width=True)
            except: st.info("PDF geladen.")
        else:
            current_img = Image.open(upload)
            st.image(current_img, use_container_width=True)

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        if st.session_state.credits > 0:
            if st.button("🚀 Analyse jetzt starten (-1 Credit)", use_container_width=True):
                with st.status("Dokument wird analysiert...", expanded=True) as status:
                    full_text = pytesseract.image_to_string(current_img, lang='deu') if current_img else ""
                    if len(full_text.strip()) < 15:
                        status.update(label="❌ Fehler: Text unleserlich", state="error")
                    else:
                        prompt = f"Analysiere detailliert: {full_text}. BEHOERDE, AZ, ERKLÄRUNG, FRISTEN, FORMFEHLER, ANTWORT (ausführlich), STEUER."
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": "Verwaltungsrechtler."}, {"role": "user", "content": prompt}])
                        if not is_admin: st.session_state.credits -= 1
                        st.session_state.kosten += (res.usage.total_tokens / 1000) * 0.00015
                        raw = res.choices[0].message.content

                        def ext(tag, src):
                            m = re.search(rf"{tag}:(.*?)(?=\n[A-Z]+:|$)", src, re.DOTALL | re.IGNORECASE)
                            return m.group(1).strip() if m else "Nicht gefunden"

                        meta = {"behoerde": ext("BEHOERDE", raw), "az": ext("AZ", raw)}
                        erk, fri, fehler, ant, ste = ext("ERKLÄRUNG", raw), ext("FRISTEN", raw), ext("FORMFEHLER", raw), ext("ANTWORT", raw), ext("STEUER", raw)
                        
                        status.update(label="✅ Analyse fertig!", state="complete")
                        st.header(meta['behoerde'])
                        with st.expander("💡 Zusammenfassung", expanded=True): st.write(erk)
                        st.warning(f"📅 Fristen: {fri}")
                        
                        final_a = st.text_area("Vorschau Antwortentwurf:", value=ant, height=250)
                        pdf_data = create_full_pdf(erk, fri, final_a, ste, meta, fehler)
                        excel_data = create_excel({"Behörde": meta['behoerde'], "AZ": meta['az'], "Frist": fri, "Antwort": final_a})
                        
                        st.download_button("📥 PDF-Analyse laden", data=pdf_data, file_name=f"Analyse.pdf", use_container_width=True)
                        st.download_button("📊 Excel-Tabelle laden", data=excel_data, file_name="Daten.xlsx", use_container_width=True)
        else:
            st.error("Bitte wähle ein Paket links aus, um Guthaben aufzuladen.")

st.divider()
st.caption("v13.1 - Dynamic Links via Secrets")
