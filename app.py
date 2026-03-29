import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import shutil
import stripe
import pandas as pd
import re
from fpdf import FPDF
from datetime import datetime
import gc 

# 1. KONFIGURATION
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")
LOGO_DATEI = "icon_final_blau.png"

# 2. SESSION STATE
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Stripe Check
params = st.query_params
if params.get("admin") == "GeheimAmt2024!": st.session_state.credits = 999
if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack = int(params.get("pack", 0))
        st.session_state.credits += pack
        st.session_state.processed_sessions.append(params["session_id"])
    except: pass

# 3. DESIGN (CSS)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; }
    .legal-box { font-size: 0.9em; color: #334155; line-height: 1.6; background: #f8fafc; padding: 25px; border-radius: 10px; border: 1px solid #e2e8f0; }
    .ampel-red { background-color: #fee2e2; border-left: 5px solid #ef4444; padding: 10px; border-radius: 5px; color: #991b1b; font-weight: bold; }
    .checklist-box { background-color: #f0fdf4; border: 1px solid #16a34a; padding: 15px; border-radius: 8px; color: #166534; }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNKTIONEN
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_letter(raw_text, lang):
    if len(raw_text) < 40: return "FEHLER_UNSCHARF"
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Analysiere den Brief. Falls unleserlich, antworte NUR: FEHLER_UNSCHARF.
    Struktur:
    ### AMPEL ### (Dringlichkeit: Hoch, Mittel oder Niedrig + Kurze Begründung)
    ### FRISTEN ### (Liste: Datum | Aktion | Dringlichkeit)
    ### CHECKLISTE ### (3-5 Schritte für den Versand)
    ### ANTWORTBRIEF ### (Vollständiger Text)"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

def create_excel_pro(text):
    # Extrahiert Zeilen aus dem Fristen-Abschnitt
    fristen_part = text.split("### FRISTEN ###")[1].split("###")[0]
    lines = [l.strip() for l in fristen_part.strip().split("\n") if "|" in l]
    data = [l.split("|") for l in lines]
    
    df = pd.DataFrame(data, columns=["Datum", "Aktion", "Priorität"]) if data else pd.DataFrame(columns=["Datum", "Aktion", "Priorität"])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen-Plan')
        worksheet = writer.sheets['Fristen-Plan']
        # Automatische Spaltenbreite
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, column_len)
    return output.getvalue()

def create_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return bytes(pdf.output())

# 5. SIDEBAR & HAUPTBEREICH (gekürzt auf Kernlogik)
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI)
    st.metric("Guthaben", f"{st.session_state.credits} Scans")
    lang_choice = st.radio("Sprache", ["Deutsch", "English"], horizontal=True)
    st.divider()
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ"])

with t1:
    st.title("Amtsschimmel-Killer 📄🚀")
    col_v, col_a = st.columns([1, 1.2])
    
    with col_v:
        upload = st.file_uploader("Brief hochladen", type=['pdf', 'png', 'jpg', 'jpeg'])
        if upload:
            if upload.type != "application/pdf": st.image(upload, use_container_width=True)
            else: st.info("✅ PDF geladen.")

    with col_a:
        if upload and st.session_state.credits > 0 and not st.session_state.full_res:
            if st.button("🚀 Analyse starten"):
                with st.spinner("KI analysiert Dringlichkeit..."):
                    # Hier get_text_hybrid Funktion einfügen (wie zuvor)
                    # raw = get_text_hybrid(upload)
                    raw = "Beispieltext..." 
                    res = analyze_letter(raw, lang_choice)
                    if "FEHLER_UNSCHARF" in res:
                        st.error("⚠️ Foto zu unscharf! Bitte mit mehr Licht neu fotografieren. Kein Abzug.")
                    else:
                        st.session_state.full_res = res
                        st.session_state.credits -= 1
                        st.rerun()

        if st.session_state.full_res:
            # Anzeige der Ampel & Checkliste
            if "### AMPEL ###" in st.session_state.full_res:
                ampel_text = st.session_state.full_res.split("### AMPEL ###")[1].split("###")[0]
                st.markdown(f'<div class="ampel-red">🚦 Dringlichkeit: {ampel_text}</div>', unsafe_allow_html=True)
            
            if "### CHECKLISTE ###" in st.session_state.full_res:
                check_text = st.session_state.full_res.split("### CHECKLISTE ###")[1].split("###")[0]
                st.markdown(f'<div class="checklist-box">✅ Versand-Checkliste:<br>{check_text}</div>', unsafe_allow_html=True)

            st.write(st.session_state.full_res.split("### ANTWORTBRIEF ###")[-1])
            
            st.divider()
            d1, d2, d3 = st.columns(3)
            with d1: st.download_button("📊 Excel-Fristenplan", create_excel_pro(st.session_state.full_res), "fristen.xlsx")
            with d2: st.download_button("📄 PDF Antwort", create_pdf_bytes(st.session_state.full_res), "antwort.pdf")
            with d3: 
                if st.button("🔄 Neu"): st.session_state.full_res = ""; st.rerun()

# --- RECHTSTEXTE (DEINE VORGABEN) ---
with t3:
    st.subheader("FAQ")
    st.write("**Ist das ein Abonnement?** Nein. Wir hassen Abos... (dein Text)")
    # ... Restliche FAQ exakt wie vorgegeben einfügen ...

# FOOTER mit Elisabeth Reinecke Impressum & Datenschutz (deine Vorgaben)
st.divider()
# ... Impressum & Datenschutz Code-Block wie zuvor ...
