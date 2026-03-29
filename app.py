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
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 15px; display: block; font-size: 1.1em; }
    .faq-a { margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #cbd5e1; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE (GUTHABEN & ADMIN)
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
# 3. KI-LOGIK (BEHÖRDEN-DOLMETSCHER & AMPEL)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text_from_file(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if len(text.strip()) < 30:
                images = convert_from_bytes(file.getvalue())
                for img in images: text += pytesseract.image_to_string(img)
        else:
            img = Image.open(file)
            text = pytesseract.image_to_string(img)
    except: pass
    return text

def analyze_letter(raw_text, lang, mode="Standard"):
    # FEHLERBEHANDLUNG: Falls kein Text erkannt wird
    if len(raw_text.strip()) < 50: 
        return "FEHLER_UNSCHARF"
    
    intent = "Antwortbrief (höflich/bestimmt)" if mode == "Standard" else "WIDERSPRUCH (rechtlich scharf mit Paragraphen)"
    
    sys_p = f"""Du bist ein erfahrener Rechtsexperte und Behörden-Berater. Sprache: {lang}.
    Analysiere den hochgeladenen Brief und erstelle EXAKT diese Sektionen:

    1. ### 🚦 DRINGLICHKEITS-AMPEL ###
    Wähle: [ROT: Sofort handeln!] oder [GELB: Frist beachten] oder [GRÜN: Nur zur Info]. Erkläre kurz warum.

    2. ### 📖 BEHÖRDEN-DOLMETSCHER (Glossar) ###
    Erkläre 3-4 schwierige Fachbegriffe aus dem Brief in ganz einfachem Deutsch.

    3. ### 📅 WICHTIGE FRISTEN ###
    Liste alle Fristen im Format: Datum | Aktion | Dringlichkeit.

    4. ### ✍️ DEIN {intent} ###
    Schreibe den fertigen Brieftext. Platzhalter wie [Name] verwenden.

    5. ### 📋 VERSAND-CHECKLISTE ###
    Gib genaue Anweisungen (z.B. Einschreiben Einwurf, Kopie machen, Unterschrift).
    """
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}]
        )
        return resp.choices[0].message.content
    except:
        return "KI-FEHLER: Bitte versuchen Sie es erneut."

# ==========================================
# 4. EXPORT-FUNKTIONEN (WORD, PDF, EXCEL, ICS)
# ==========================================
def create_docx(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(text.replace("###", "").replace("**", "")); bio = io.BytesIO()
    doc.save(bio); return bio.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=11)
    clean = text.replace("###", "").replace("**", "")
    pdf.multi_cell(0, 8, txt=clean.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Datum": dates, "Ereignis": ["Frist aus Brief" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fristen')
    return output.getvalue()

def create_ics(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        ics += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel\nDTSTART:{datetime.now().strftime('%Y%m%d')}\nEND:VEVENT\n"
    ics += "END:VCALENDAR"
    return ics.encode('utf-8')

# ==========================================
# 5. SIDEBAR (FLAGGEN & LOGO)
# ==========================================
with st.sidebar:
    if os.path.exists("icon_final_blau.png"): st.image("icon_final_blau.png", use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    
    st.divider()
    lang_choice = st.selectbox("🌍 Zielsprache", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", 
        "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", 
        "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"
    ])
    
    st.divider()
    st.subheader("💳 Guthaben")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | KEIN ABO</small></a>', unsafe_allow_html=True)

# ==========================================
# 6. HAUPTBEREICH (TABS)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Behörden-Assistent 📄🚀")
    c1, c2 = st.columns(2)
    with c1:
        upload = st.file_uploader("Brief fotografieren oder hochladen:", type=['pdf', 'png', 'jpg', 'jpeg'])
    with c2:
        if upload and st.session_state.credits > 0:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Dolmetscher arbeitet..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Text ist zu unscharf. Bitte nochmal mit mehr Licht fotografieren! (Kein Abzug)")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with b2:
                if st.button("⚖️ WIDERSPRUCH"):
                    with st.spinner("Widerspruch wird generiert..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Dokument unleserlich. Bitte schärferes Foto nutzen! (Kein Abzug)")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Bitte Guthaben aufladen.")

    if st.session_state.full_res:
        st.divider(); st.markdown(st.session_state.full_res)
        st.subheader("📥 Downloads")
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Antwort.docx")
        with d2: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with d3: st.download_button("📊 Excel", create_excel(st.session_state.full_res), "Fristen.xlsx")
        with d4: st.download_button("📅 Kalender", create_ics(st.session_state.full_res), "Termin.ics")
        with d5: 
            if st.button("🔄 Neu"): st.session_state.full_res = ""; st.rerun()

with t2:
    st.header("⚡ Vorlagen")
    st.info("**Fristverlängerung:**\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der Frist bis zum [Datum], da mir noch Unterlagen fehlen.")
    st.info("**Widerspruch (Fristwahrend):**\nHiermit lege ich gegen den Bescheid vom [Datum] Widerspruch ein. Begründung folgt separat.")
    st.info("**Akteneinsicht:**\nIch beantrage hiermit Akteneinsicht gemäß § 25 SGB X.")

with t3:
    st.header("❓ FAQ")
    st.markdown('<span class="faq-q">Ist das ein Abonnement?</span>', unsafe_allow_html=True)
    st.write("Nein. Wir hassen Abos. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans.")
    st.markdown('<span class="faq-q">Wie sicher sind meine Dokumente?</span>', unsafe_allow_html=True)
    st.write("Verschlüsselt an OpenAI übertragen, keine dauerhafte Speicherung, sofortige Löschung.")

with t4:
    st.header("⚖️ Impressum")
    st.write("Elisabeth Reinecke | Ringelsweide 9, 40223 Düsseldorf | amtsschimmel-killer@proton.me")

with t5:
    st.header("🔒 Datenschutz")
    st.write("DSGVO-konform. TLS-Verschlüsselung. Keine Datennutzung für Werbezwecke.")

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
