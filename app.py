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
import shutil
import stripe
import numpy as np
import cv2
from datetime import datetime

# 1. SEITEN-KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# 2. API INITIALISIERUNG
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    stripe.api_key = st.secrets["STRIPE_API_KEY"]
    LINK_1 = st.secrets["STRIPE_LINK_1"]
    LINK_3 = st.secrets["STRIPE_LINK_3"]
    LINK_10 = st.secrets["STRIPE_LINK_10"]
except Exception as e:
    st.error(f"⚠️ Konfigurationsfehler in den Secrets: {e}")

# TESSERACT PFAD
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

# --- HILFSFUNKTIONEN ---
def clean_text(text):
    if not text: return ""
    return text.replace("```text", "").replace("```", "").strip()

def remove_emojis(text):
    return text.encode('latin-1', 'ignore').decode('latin-1') if text else ""

class PDF(FPDF):
    def header(self):
        logo_path = "icon_final_blau.png"
        if os.path.exists(logo_path):
            self.image(logo_path, 170, 8, 30)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'Amtsschimmel-Killer | Analyse-Gutachten', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()} | Erstellt am {datetime.now().strftime("%d.%m.%Y")}', 0, 0, 'C')

def create_full_pdf(erk, fri, ant, ste, meta, fehler):
    pdf = PDF()
    pdf.add_page()
    
    sections = [
        ("Dokument von", meta.get('behoerde', '-')),
        ("Aktenzeichen / Referenz", meta.get('az', '-')),
        ("Zusammenfassung (Klartext)", erk),
        ("Fristen & Termine", fri),
        ("Rechtlicher Antwortentwurf", ant)
    ]
    
    for title, content in sections:
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(230, 235, 245)
        pdf.cell(0, 8, title, ln=1, fill=True)
        pdf.set_font("Arial", size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
        pdf.multi_cell(0, 6, txt=remove_emojis(content))
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

def create_excel(data_dict):
    df = pd.DataFrame([data_dict])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analyse')
        workbook  = writer.book
        worksheet = writer.sheets['Analyse']
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#CFE2F3', 'border': 1})
        cell_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, 50, cell_fmt)
    return output.getvalue()

# --- 3. CREDITS & SESSION STATE ---
if "credits" not in st.session_state: st.session_state.credits = 0
if "verified_sessions" not in st.session_state: st.session_state.verified_sessions = []
if "analyse_ergebnis" not in st.session_state: st.session_state.analyse_ergebnis = None

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
    except: st.sidebar.error("Zahlung nicht verifiziert.")

if is_admin: st.session_state.credits = 999

# --- 4. SIDEBAR ---
with st.sidebar:
    logo_file = "icon_final_blau.png"
    if os.path.exists(logo_file): st.image(logo_file, width=150)
    st.header("Dein Status")
    st.metric("Verfügbare Analysen", st.session_state.credits)
    
    stripe_html = f'''
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="background: #f9fafb; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db;">
                <a href="{LINK_1}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; background:#f9fafb; color:black; border:1px solid #d1d5db; padding:8px; cursor:pointer; font-weight:bold;">Analyse (1 Dokument)</button></a>
            </div>
            <div style="background: #10b981; padding: 10px; border-radius: 8px;">
                <a href="{LINK_3}" target="_blank" style="text-decoration:none;"><button style="width:100%; border-radius:5px; background:#10b981; color:white; border:none; padding:10px; cursor:pointer; font-weight:bold;">Spar-Paket (3 Dokumente)</button></a>
            </div>
        </div>
    '''
    if is_admin:
        with st.expander("🛠️ Admin-Links"): st.markdown(stripe_html, unsafe_allow_html=True)
    elif st.session_state.credits <= 0:
        st.subheader("💳 Guthaben aufladen")
        st.markdown(stripe_html, unsafe_allow_html=True)

# --- 5. HAUPT-LOGIK ---
st.title("Amtsschimmel-Killer 📄🚀")
upload = st.file_uploader("Dokument hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])

if upload and "last_file" in st.session_state and st.session_state.last_file != upload.name:
    st.session_state.analyse_ergebnis = None
if upload: st.session_state.last_file = upload.name

if upload:
    col_img, col_ana = st.columns(2)
    current_img = None
    with col_img:
        st.subheader("📸 Dokument")
        if upload.type == "application/pdf":
            try:
                pages = convert_from_bytes(upload.getvalue(), first_page=1, last_page=1, dpi=100)
                current_img = pages if isinstance(pages, list) else pages[0]
                st.image(current_img, use_container_width=True)
            except: st.info("PDF bereit.")
        else:
            current_img = Image.open(upload)
            st.image(current_img, use_container_width=True)

    with col_ana:
        st.subheader("🧠 KI-Analyse")
        
        if st.session_state.analyse_ergebnis is None:
            if st.session_state.credits > 0:
                if st.button("🚀 Analyse jetzt starten (-1 Credit)", use_container_width=True):
                    with st.status("Verarbeite Dokument...", expanded=True) as status:
                        txt = pytesseract.image_to_string(current_img, lang='deu')
                        
                        prompt = f"""Analysiere dieses Dokument STRENG in diesem Format:
                        BEHOERDE: [Name/Absender]
                        AZ: [Aktenzeichen/Referenz]
                        ZUSAMMENFASSUNG: [Ausführliche Erklärung in mind. 5 Sätzen.]
                        FRISTEN: [Konkrete Daten und Folgen.]
                        FORMFEHLER: [Rechtliche Mängel.]
                        ANTWORTENTWURF: und [Datum] als Platzhalter.]
                        STEUER: [Infos zu Beträgen]
                        Text: {txt}"""
                        
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": "Du bist ein erfahrener Jurist für Behördenkorrespondenz."}, {"role": "user", "content": prompt}]
                        )
                        
                        raw = res.choices.message.content
                        if not is_admin: st.session_state.credits -= 1
                        
                        def ext(tag, src):
                            m = re.search(rf"{tag}:?\s*(.*?)(?=\n[A-Z]+:|$)", src, re.DOTALL | re.IGNORECASE)
                            return clean_text(m.group(1)) if m else "Nicht gefunden"

                        st.session_state.analyse_ergebnis = {
                            "meta": {"behoerde": ext("BEHOERDE", raw), "az": ext("AZ", raw)},
                            "erk": ext("ZUSAMMENFASSUNG", raw),
                            "fri": ext("FRISTEN", raw),
                            "fehler": ext("FORMFEHLER", raw),
                            "ant": ext("ANTWORTENTWURF", raw),
                            "ste": ext("STEUER", raw)
                        }
                        status.update(label="✅ Analyse abgeschlossen!", state="complete")
                        st.rerun()
            else: st.error("Bitte Guthaben aufladen.")

        if st.session_state.analyse_ergebnis:
            res = st.session_state.analyse_ergebnis
            st.header(res['meta']['behoerde'])
            with st.expander("💡 Zusammenfassung", expanded=True): st.write(res['erk'])
            st.warning(f"📅 Fristen: {res['fri']}")
            
            final_a = st.text_area("Vorschau Antwortentwurf:", value=res['ant'], height=450)
            
            p_data = create_full_pdf(res['erk'], res['fri'], final_a, res['ste'], res['meta'], res['fehler'])
            e_data = create_excel({"Absender": res['meta']['behoerde'], "Referenz": res['meta']['az'], "Zusammenfassung": res['erk'], "Fristen": res['fri'], "Brief-Entwurf": final_a})
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 PDF laden", data=p_data, file_name=f"Analyse_{res['meta']['behoerde']}.pdf", use_container_width=True)
            c2.download_button("📊 Excel laden", data=e_data, file_name=f"Daten_{res['meta']['behoerde']}.xlsx", use_container_width=True)

st.divider()
st.caption("v15.0 - Branded PDF & High-Volume Legal Drafting")
