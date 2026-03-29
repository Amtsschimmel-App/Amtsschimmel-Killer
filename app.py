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
# 1. DESIGN & CSS (UNVERÄNDERLICH)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563eb; transform: translateY(-2px); }
    .buy-button { text-decoration: none; display: block; padding: 12px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; margin-bottom: 10px; color: #1e3a8a !important; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: all 0.2s; font-size: 0.9em; }
    .buy-button:hover { border-color: #1e3a8a; background: #f8fafc; transform: scale(1.01); }
    .faq-q { font-weight: bold; color: #1e3a8a; margin-top: 20px; display: block; font-size: 1.1em; }
    .faq-a { margin-bottom: 20px; padding-left: 10px; color: #475569; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE (CREDIT-SPEICHERUNG)
# ==========================================
# WICHTIG: Damit Credits beim Upload nicht gelöscht werden
if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = ""
if "processed_sessions" not in st.session_state:
    st.session_state.processed_sessions = []

# Admin & Stripe Check (wird nur einmal pro Session verarbeitet)
params = st.query_params
if params.get("admin") == "GeheimAmt2024!" and st.session_state.credits < 500:
    st.session_state.credits = 999

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
    if len(raw_text.strip()) < 40: 
        return "FEHLER_UNSCHARF"
    intent = "Antwortbrief" if mode == "Standard" else "WIDERSPRUCH (hart, mit Paragraphen)"
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Struktur IMMER:
    ### 🚦 DRINGLICHKEITS-AMPEL ### [Farbe + Grund]
    ### 📖 BEHÖRDEN-DOLMETSCHER ### [3 Begriffe einfach erklärt]
    ### 📅 FRISTEN ### [Datum | Aktion]
    ### ✍️ ANTWORTBRIEF ### [Vollständiger Entwurf als {intent}]
    ### 📋 VERSAND-CHECKLISTE ### [Anweisungen]"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

# ==========================================
# 4. EXPORT FUNKTIONEN (WORD, PDF, EXCEL, ICS)
# ==========================================
def create_docx(text):
    doc = Document()
    doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(text.replace("###", "").replace("**", ""))
    bio = io.BytesIO(); doc.save(bio); return bio.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    clean = text.replace("###", "").replace("**", "")
    pdf.multi_cell(0, 8, txt=clean.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

def create_excel(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    df = pd.DataFrame({"Datum": dates, "Aktion": ["Frist aus Brief" for _ in dates]})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    if os.path.exists("icon_final_blau.png"):
        st.image("icon_final_blau.png", use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    lang_choice = st.selectbox("🌍 Sprache wählen", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"])
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# ==========================================
# 6. HAUPTBEREICH (TABS)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Brief hochladen & killen 🚀")
    c1, c2 = st.columns(2)
    with c1:
        upload = st.file_uploader("Datei wählen:", type=['pdf', 'png', 'jpg', 'jpeg'], key="uploader")
        if upload:
            # VORSCHAU FIX
            if upload.type.startswith("image"):
                st.image(upload, caption="Dein Dokument", use_container_width=True)
            else: st.info("PDF erfolgreich geladen.")

    with c2:
        if upload and st.session_state.credits > 0:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Analyse läuft..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Text zu unscharf. (Kein Abzug)")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with b2:
                if st.button("⚖️ WIDERSPRUCH"):
                    with st.spinner("Wird erstellt..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Text zu unscharf. (Kein Abzug)")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Bitte Guthaben aufladen.")

    if st.session_state.full_res:
        st.divider(); st.markdown(st.session_state.full_res)
        st.subheader("📥 Downloads")
        d1, d2, d3, d4 = st.columns(4)
        with d1: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Antwort.docx")
        with d2: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with d3: st.download_button("📊 Excel", create_excel(st.session_state.full_res), "Fristen.xlsx")
        with d4: 
            if st.button("🔄 Neu"): st.session_state.full_res = ""; st.rerun()

# TAB TEXTE (UNVERÄNDERLICH)
with t2:
    st.header("⚡ Vorlagen")
    st.info("**Fristverlängerung:**\nSehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.info("**Widerspruch (Fristwahrend):**\nSehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt separat. Mit freundlichen Grüßen, [Name]")
    st.info("**Akteneinsicht:**\nSehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht.")

with t3:
    st.header("❓ FAQ")
    st.markdown('<p class="faq-q">Ist das ein Abonnement?</p>', unsafe_allow_html=True)
    st.write("Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.")
    st.markdown('<p class="faq-q">Wie sicher sind meine Dokumente?</p>', unsafe_allow_html=True)
    st.write("Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig verarbeitet und niemals dauerhaft gespeichert. Nach der Analyse werden die Daten gelöscht.")
    st.markdown('<p class="faq-q">Ersetzt die App eine Rechtsberatung?</p>', unsafe_allow_html=True)
    st.write("Nein. Wir bieten eine Formulierungshilfe. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.")
    st.markdown('<p class="faq-q">Was passiert, wenn der Scan fehlschlägt?</p>', unsafe_allow_html=True)
    st.write("Ein Scan wird erst berechnet, wenn die KI erfolgreich war. Bei unscharfen Fotos wird kein Guthaben abgezogen.")

with t4:
    st.header("⚖️ Impressum")
    st.markdown("Amtsschimmel-Killer  \nBetreiberin: Elisabeth Reinecke  \nRingelsweide 9  \n40223 Düsseldorf  \n\n**Kontakt:**  \nTelefon: +49 211 15821329  \nE-Mail: amtsschimmel-killer@proton.me  \nWeb: amtsschimmel-killer.streamlit.app  \n\n**Haftung:**  \nInhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.")

with t5:
    st.header("🔒 Datenschutz")
    st.markdown("1. **Datenschutz auf einen Blick**: Wir behandeln Ihre Daten vertraulich (DSGVO).  \n2. **Hosting**: Streamlit Cloud.  \n3. **Dokumente**: Übertragung per TLS an OpenAI. Keine Speicherung auf Servern.  \n4. **Stripe**: Zahlungsdaten werden direkt bei Stripe verarbeitet.  \n5. **Ihre Rechte**: Auskunft & Löschung unter amtsschimmel-killer@proton.me.")

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
