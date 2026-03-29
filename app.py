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
# 1. KONFIGURATION & DESIGN
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; font-size: 0.9em; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; transform: scale(1.01); }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & STRIPE
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

params = st.query_params
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

if "session_id" in params and params["session_id"] not in st.session_state.processed_sessions:
    try:
        pack_val = int(params.get("pack", 0))
        st.session_state.credits += pack_val
        st.session_state.processed_sessions.append(params["session_id"])
        st.balloons()
    except: pass

# ==========================================
# 3. HILFSFUNKTIONEN (OCR, KI, EXPORT)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_from_file(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if len(text.strip()) < 20:
                images = convert_from_bytes(file.getvalue())
                for img in images:
                    text += pytesseract.image_to_string(img)
        else:
            img = Image.open(file)
            text = pytesseract.image_to_string(img)
    except: pass
    return text

def analyze_letter(raw_text, lang, mode="Standard"):
    if len(raw_text.strip()) < 40: return "FEHLER_UNSCHARF"
    intent = "Antwortbrief" if mode == "Standard" else "rechtlich fundierter WIDERSPRUCH"
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Struktur:
    ### AMPEL ### Dringlichkeit: [Niedrig/Mittel/Hoch] + Grund: [Satz]
    ### GLOSSAR ### (Begriffe)
    ### FRISTEN ### (Datum | Aktion | Dringlichkeit)
    ### ANTWORTBRIEF ### (Erstelle einen {intent})
    ### CHECKLISTE ### (Versand)"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    # Entferne Markdown-Symbole für sauberes Word
    clean_text = text.replace("###", "").replace("**", "")
    doc.add_paragraph(clean_text)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_excel_pro(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Datum": dates, "Ereignis": ["Frist aus Behördenbrief" for _ in dates], "Status": ["Offen" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen')
        worksheet = writer.sheets['Fristen']
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 5
            worksheet.set_column(i, i, max_len)
    return output.getvalue()

def create_ics(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        try:
            dt = datetime.strptime(d, "%d.%m.%Y").strftime("%Y%m%d")
            ics_content += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel-Killer\nDTSTART:{dt}\nDTEND:{dt}\nDESCRIPTION:Automatisch erinnerte Frist\nEND:VEVENT\n"
        except: pass
    ics_content += "END:VCALENDAR"
    return ics_content.encode('utf-8')

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    LOGO_PATH = "icon_final_blau.png"
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
    else: st.title("📄 Amtsschimmel-Killer")
    
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    lang_choice = st.selectbox("Zielsprache", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"])
    st.divider()
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ KEIN ABO</small></a>', unsafe_allow_html=True)

# ==========================================
# 5. HAUPTBEREICH (TABS)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Brief hochladen & killen 🚀")
    c1, c2 = st.columns(2)
    with c1:
        upload = st.file_uploader("Datei wählen (PDF/Bild):", type=['pdf', 'png', 'jpg', 'jpeg'])
    with c2:
        if upload and st.session_state.credits > 0:
            if st.button("🚀 ANALYSE STARTEN"):
                with st.spinner("Lese Brief..."):
                    txt = get_text_from_file(upload)
                    res = analyze_letter(txt, lang_choice, "Standard")
                    if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Kein Abzug.")
                    else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            if st.button("⚖️ WIDERSPRUCH ERSTELLEN"):
                with st.spinner("Erstelle Widerspruch..."):
                    txt = get_text_from_file(upload)
                    res = analyze_letter(txt, lang_choice, "Widerspruch")
                    if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf! Kein Abzug.")
                    else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Bitte Guthaben aufladen.")

    if st.session_state.full_res:
        st.divider()
        st.markdown(st.session_state.full_res)
        st.subheader("📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.download_button("📝 Word (Brief)", create_docx(st.session_state.full_res), "Antwortbrief.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        with d2:
            st.download_button("📊 Excel (Fristen)", create_excel_pro(st.session_state.full_res), "Fristen.xlsx", "application/vnd.ms-excel")
        with d3:
            st.download_button("📅 Kalender (.ics)", create_ics(st.session_state.full_res), "Fristen.ics", "text/calendar")
        with d4:
            if st.button("🔄 Neu"): st.session_state.full_res = ""; st.rerun()

with t2:
    st.header("⚡ Vorlagen")
    with st.expander("Fristverlängerung"): st.info("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    with st.expander("Widerspruch (Fristwahrend)"): st.info("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt separat. Mit freundlichen Grüßen, [Name]")
    with st.expander("Akteneinsicht"): st.info("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with t3:
    st.header("❓ FAQ")
    st.markdown('<span class="faq-q">Ist das ein Abonnement?</span>', unsafe_allow_html=True)
    st.write("Nein. Jede Zahlung ist eine Einmalzahlung.")
    st.markdown('<span class="faq-q">Wie sicher sind meine Dokumente?</span>', unsafe_allow_html=True)
    st.write("Verschlüsselt an OpenAI übertragen, keine dauerhafte Speicherung.")

with t4:
    st.header("⚖️ Impressum")
    st.write("Amtsschimmel-Killer | Elisabeth Reinecke | Ringelsweide 9, 40223 Düsseldorf")
    st.write("Kontakt: +49 211 15821329 | amtsschimmel-killer@proton.me")

with t5:
    st.header("🔒 Datenschutz")
    st.write("1. Vertraulichkeit nach DSGVO. 2. Hosting Streamlit Cloud. 3. Keine Speicherung der Briefe.")

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
