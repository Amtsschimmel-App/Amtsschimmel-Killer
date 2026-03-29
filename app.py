import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
import pandas as pd
import re
from fpdf import FPDF
from docx import Document
from datetime import datetime

# ==========================================
# 1. DESIGN & CSS (FEST VERANKERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; font-size: 0.9em; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; transform: scale(1.01); }
    .log-box { font-family: monospace; font-size: 0.8em; background: #f1f5f9; padding: 10px; border-radius: 5px; border: 1px solid #cbd5e1; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE (CREDITS & LOGS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []
if "app_logs" not in st.session_state: st.session_state.app_logs = []

def add_log(step, message, is_error=False):
    now = datetime.now().strftime("%H:%M:%S")
    entry = f"[{now}] {step}: {message}"
    st.session_state.app_logs.append(entry)
    if is_error: st.error(entry)

# Admin & Stripe Check
params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999
    add_log("ADMIN", "Admin-Guthaben (999) aktiviert.")

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack_val = int(params.get("pack", 0))
        st.session_state.credits += pack_val
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 3. KI-LOGIK & OCR
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_from_file(file):
    text = ""
    add_log("OCR", "Starte Texterkennung...")
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if len(text.strip()) < 30:
                add_log("OCR", "PDF enthält kein Text-Layer, wechsle zu Bild-Scan.")
                images = convert_from_bytes(file.getvalue())
                for img in images: text += pytesseract.image_to_string(img)
        else:
            img = Image.open(file)
            text = pytesseract.image_to_string(img)
        add_log("OCR", f"Erfolgreich. {len(text)} Zeichen erkannt.")
    except Exception as e:
        add_log("OCR", f"Fehler: {str(e)}", True)
    return text

def analyze_letter(raw_text, lang, mode="Standard"):
    if len(raw_text.strip()) < 50: return "FEHLER_UNSCHARF"
    add_log("KI", f"Sende Daten an OpenAI (Modus: {mode})...")
    
    intent = "Antwortbrief" if mode == "Standard" else "WIDERSPRUCH (hart)"
    sys_p = f"Rechtsexperte. Sprache: {lang}. Struktur: ### AMPEL ###, ### GLOSSAR ###, ### FRISTEN ###, ### ANTWORTBRIEF ###, ### CHECKLISTE ###."
    
    try:
        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
        add_log("KI", "Analyse von OpenAI empfangen.")
        return resp.choices[0].message.content
    except Exception as e:
        add_log("KI", f"Fehler: {str(e)}", True)
        return "KI_ABSTURZ"

# ==========================================
# 4. EXPORT FUNKTIONEN
# ==========================================
def create_docx(text):
    add_log("EXPORT", "Generiere Word-Datei...")
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    clean = text.replace("###", "").replace("**", "")
    doc.add_paragraph(clean); bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

def create_pdf(text):
    add_log("EXPORT", "Generiere PDF...")
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    clean = text.replace("###", "").replace("**", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean); return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("icon_final_blau.png"): st.image("icon_final_blau.png", use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    lang_choice = st.selectbox("🌍 Sprache", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"])
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | KEIN ABO</small></a>', unsafe_allow_html=True)

# ==========================================
# 6. HAUPTBEREICH
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Amtsschimmel-Killer 🚀")
    c1, c2 = st.columns([1, 1])
    with c1:
        upload = st.file_uploader("Brief hochladen:", type=['pdf', 'png', 'jpg', 'jpeg'], key="up")
        if upload and upload.type.startswith("image"): st.image(upload, caption="Vorschau", use_container_width=True)
    with c2:
        if upload and st.session_state.credits > 0:
            if st.button("🚀 ANALYSE STARTEN"):
                txt = get_text_from_file(upload)
                res = analyze_letter(txt, lang_choice, "Standard")
                if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf.")
                elif "KI_ABSTURZ" in res: st.error("❌ KI-Verbindung fehlgeschlagen.")
                else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            if st.button("⚖️ WIDERSPRUCH"):
                txt = get_text_from_file(upload)
                res = analyze_letter(txt, lang_choice, "Widerspruch")
                if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf.")
                else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Guthaben leer.")

        # LOG-BOX (WICHTIG FÜR DICH)
        if st.session_state.app_logs:
            with st.expander("🛠️ System-Logs (Diagnose)"):
                for log in st.session_state.app_logs[-5:]: st.markdown(f"`{log}`")

    if st.session_state.full_res:
        st.divider(); st.markdown(st.session_state.full_res)
        st.subheader("📥 Downloads")
        d_col = st.columns(4)
        with d_col[0]: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Antwort.docx")
        with d_col[1]: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with d_col[2]: 
            if st.button("🔄 Neu"): st.session_state.full_res = ""; st.session_state.app_logs = []; st.rerun()

# FESTE TEXTE FÜR IMPRESSUM & DATENSCHUTZ & FAQ (WIE OBEN VEREINBART)
with t3:
    st.header("❓ FAQ")
    st.markdown("**Ist das ein Abonnement?**  \nNein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung.")
    st.markdown("**Wie sicher sind meine Dokumente?**  \nIhre Dokumente werden verschlüsselt an OpenAI übertragen und nach der Sitzung gelöscht.")
    st.markdown("**Was passiert bei Fehlern?**  \nEin Scan wird nur berechnet, wenn die KI erfolgreich war. Bei unscharfen Fotos gibt es keinen Abzug.")

with t4:
    st.header("⚖️ Impressum")
    st.markdown("Amtsschimmel-Killer  \nBetreiberin: Elisabeth Reinecke  \nRingelsweide 9, 40223 Düsseldorf  \n\nTelefon: +49 211 15821329  \nE-Mail: amtsschimmel-killer@proton.me")

with t5:
    st.header("🔒 Datenschutz")
    st.markdown("Wir behandeln Ihre Daten vertraulich entsprechend der DSGVO. Dokumente werden zur Analyse an OpenAI (USA) übertragen und nicht gespeichert.")

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
