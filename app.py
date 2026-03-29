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
from docx.shared import Inches
from datetime import datetime

# ==========================================
# 1. DESIGN & KONSTANTEN (FEST FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .analysis-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 25px; border-radius: 12px; border-left: 6px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); color: #1e293b; line-height: 1.6; }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: white; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a; text-align: center; font-size: 0.9em; transition: 0.2s; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"

# ==========================================
# 2. SESSION STATE (STABILE CREDITS & LOGS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        st.session_state.credits += int(params.get("pack", 0))
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 3. EXPORT FUNKTIONEN (MIT LOGO)
# ==========================================
def create_docx_with_logo(text):
    doc = Document()
    if os.path.exists(LOGO_DATEI):
        doc.add_picture(LOGO_DATEI, width=Inches(1.5))
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(f"Datum: {datetime.now().strftime('%d.%m.%Y')}")
    doc.add_paragraph("-" * 30)
    doc.add_paragraph(text.replace("###", "").replace("**", ""))
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_pdf_with_logo(text):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_DATEI):
        pdf.image(LOGO_DATEI, 10, 8, 33)
        pdf.ln(25)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Amtsschimmel-Killer Analyse", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    clean_text = text.replace("###", "").replace("**", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

def create_excel_pro(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({
        "Datum": dates, 
        "Vorgang": ["Frist / Termin aus Brief" for _ in dates],
        "Details": [text[:500].replace("\n", " ") + "..." for _ in dates]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen-Check')
        worksheet = writer.sheets['Fristen-Check']
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 40) # Automatische Breite
    return output.getvalue()

def create_ics(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        try:
            clean_d = datetime.strptime(d, "%d.%m.%Y").strftime("%Y%m%d")
            ics += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel-Killer\nDTSTART:{clean_d}\nDTEND:{clean_d}\nDESCRIPTION:Erinnerung an Behördenfrist\nEND:VEVENT\n"
        except: pass
    ics += "END:VCALENDAR"
    return ics.encode('utf-8')

# ==========================================
# 4. KI-LOGIK
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_from_file(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
            if len(text.strip()) < 30:
                imgs = convert_from_bytes(file.getvalue())
                for i in imgs: text += pytesseract.image_to_string(i)
        else:
            text = pytesseract.image_to_string(Image.open(file))
    except: pass
    return text

def analyze_letter(raw_text, lang, mode="Standard"):
    if len(raw_text.strip()) < 40: return "FEHLER_UNSCHARF"
    intent = "Antwortbrief" if mode == "Standard" else "WIDERSPRUCH (hart & rechtlich fundiert)"
    sys_p = f"""Rechtsexperte. Sprache: {lang}. Struktur IMMER:
    ### 🚦 DRINGLICHKEITS-AMPEL ### (ROT/GELB/GRÜN + Grund)
    ### 📖 BEHÖRDEN-DOLMETSCHER ### (3 Begriffe einfach erklärt)
    ### 📅 WICHTIGE FRISTEN ### (Datum | Aktion | Dringlichkeit)
    ### ✍️ DEIN {intent} ### (Vollständiger Entwurf)
    ### 📋 VERSAND-CHECKLISTE ### (Genaue Anweisungen)"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    lang_choice = st.selectbox("🌍 Sprache wählen", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"])
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><b>KEIN ABO | Einmalzahlung</b></a>', unsafe_allow_html=True)

# ==========================================
# 6. HAUPTBEREICH (LAYOUT-OPTIMIERUNG)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    col_links, col_rechts = st.columns([1, 1.3])
    
    with col_links:
        st.subheader("1. Dokument hochladen")
        upload = st.file_uploader("Bild oder PDF wählen:", type=['pdf','png','jpg','jpeg'], key="up_main")
        if upload:
            if upload.type.startswith("image"):
                st.image(upload, caption="Vorschau deines Briefes", use_container_width=True)
            else:
                st.info("✅ PDF-Datei erfolgreich geladen.")

    with col_rechts:
        st.subheader("2. Analyse & Killer-Entwurf")
        if upload and st.session_state.credits > 0:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Lese Brief..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Bitte neu fotografieren.")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with c2:
                if st.button("⚖️ WIDERSPRUCH"):
                    with st.spinner("Erstelle Widerspruch..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Bitte neu fotografieren.")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload:
            st.warning("⚠️ Guthaben leer. Bitte in der Sidebar aufladen.")

        if st.session_state.full_res:
            st.markdown(f'<div class="analysis-box">{st.session_state.full_res}</div>', unsafe_allow_html=True)
            st.divider()
            st.subheader("📥 Downloads")
            d1, d2, d3, d4 = st.columns(4)
            with d1: st.download_button("📝 Word", create_docx_with_logo(st.session_state.full_res), "Antwortbrief.docx")
            with d2: st.download_button("📄 PDF", create_pdf_with_logo(st.session_state.full_res), "Analyse.pdf")
            with d3: st.download_button("📊 Excel", create_excel_pro(st.session_state.full_res), "Fristen.xlsx")
            with d4: st.download_button("📅 Kalender", create_ics(st.session_state.full_res), "Fristen.ics")
            if st.button("🔄 Neue Analyse"): st.session_state.full_res = ""; st.rerun()

# ==========================================
# 7. RECHTLICHE TABS (FEST VERANKERT)
# ==========================================
with t2:
    st.header("⚡ Schnell-Vorlagen")
    st.info("**Fristverlängerung:** Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum]...")
    st.info("**Widerspruch:** Hiermit lege ich gegen Ihren Bescheid vom [Datum] Widerspruch ein. Eine Begründung folgt separat...")

with t3:
    st.header("❓ FAQ")
    st.write("**Ist das ein Abo?** Nein. Einmalzahlung. Kein Abo.")
    st.write("**Wie sicher sind meine Daten?** Wir speichern nichts. Die Analyse erfolgt live und wird danach gelöscht.")

with t4:
    st.header("⚖️ Impressum")
    st.write("Amtsschimmel-Killer | Elisabeth Reinecke | Ringelsweide 9, 40223 Düsseldorf | amtsschimmel-killer@proton.me")

with t5:
    st.header("🔒 Datenschutz")
    st.write("Wir behandeln Ihre personenbezogenen Daten vertraulich nach DSGVO. Dokumente werden verschlüsselt an OpenAI übertragen.")

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
