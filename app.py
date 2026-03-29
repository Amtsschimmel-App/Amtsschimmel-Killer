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
# 1. KONSTANTEN (FEST FIXIERT)
# ==========================================
IMPRESSUM_TEXT = """
**Amtsschimmel-Killer**  
Betreiberin: Elisabeth Reinecke  
Ringelsweide 9  
40223 Düsseldorf  

**Kontakt:**  
Telefon: +49 211 15821329  
E-Mail: amtsschimmel-killer@proton.me  
Web: amtsschimmel-killer.streamlit.app  

**Haftung:**  
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
"""

DATENSCHUTZ_TEXT = """
**1. Datenschutz auf einen Blick**  
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**  
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**  
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**  
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**  
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.
"""

FAQ_DATA = [
    ("Ist das ein Abonnement?", "Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung."),
    ("Wie sicher sind meine Dokumente?", "Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht."),
    ("Ersetzt die App eine Rechtsberatung?", "Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt."),
    ("Was passiert, wenn der Scan fehlschlägt?", "Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen."),
    ("Wie erreiche ich Elisabeth Reinecke?", "Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.")
]

VORLAGEN = {
    "Fristverlängerung": "Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]",
    "Widerspruch einlegen (Fristwahrend)": "Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]",
    "Akteneinsicht einfordern": "Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]"
}

# ==========================================
# 2. SESSION STATE (GUTHABEN-SICHERUNG)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""
if "processed_sessions" not in st.session_state: st.session_state.processed_sessions = []

# Admin & Stripe Check (Bleibt stabil im Session State)
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
# 3. FUNKTIONEN (OCR, KI & EXPORT)
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text(file):
    text = ""
    try:
        if file.type == "application/pdf":
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
            if len(text.strip()) < 30:
                images = convert_from_bytes(file.getvalue())
                for img in images: text += pytesseract.image_to_string(img)
        else:
            img = Image.open(file)
            text = pytesseract.image_to_string(img)
    except: pass
    return text

def analyze(raw_text, lang, mode="Standard"):
    if len(raw_text.strip()) < 45: return "FEHLER_UNSCHARF"
    intent = "Antwortbrief" if mode == "Standard" else "WIDERSPRUCH"
    sys_p = f"Rechtsexperte. Sprache: {lang}. Struktur: ### AMPEL ###, ### GLOSSAR ###, ### FRISTEN ###, ### ANTWORTBRIEF ###, ### CHECKLISTE ###."
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices[0].message.content

def create_docx(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    doc.add_paragraph(text.replace("###", "").replace("**", "")); bio = io.BytesIO()
    doc.save(bio); return bio.getvalue()

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    clean = text.replace("###", "").replace("**", "").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean); return bytes(pdf.output(dest='S'))

# ==========================================
# 4. SIDEBAR & DESIGN
# ==========================================
st.markdown("<style>.stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #1e3a8a; color: white; font-weight: bold; }</style>", unsafe_allow_html=True)

with st.sidebar:
    LOGO_PATH = "icon_final_blau.png"
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    lang = st.selectbox("🌍 Sprache", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"])
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" style="text-decoration:none;"><div style="background:white; border:1px solid #e2e8f0; padding:10px; border-radius:10px; margin-bottom:10px; color:#1e3a8a; text-align:center;"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung</small></div></a>', unsafe_allow_html=True)

# ==========================================
# 5. HAUPTBEREICH (TABS)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Brief-Killer 🚀")
    col1, col2 = st.columns(2)
    with col1:
        upload = st.file_uploader("Datei wählen:", type=['pdf', 'png', 'jpg', 'jpeg'], key="up")
        if upload: # VORSCHAU FIX
            if upload.type.startswith("image"): st.image(upload, caption="Vorschau", use_container_width=True)
            else: st.info("PDF geladen.")
    with col2:
        if upload and st.session_state.credits > 0:
            if st.button("🚀 ANALYSE STARTEN"):
                with st.spinner("Analyse..."):
                    res = analyze(get_text(upload), lang, "Standard")
                    if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf!")
                    else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            if st.button("⚖️ WIDERSPRUCH"):
                with st.spinner("Wird erstellt..."):
                    res = analyze(get_text(upload), lang, "Widerspruch")
                    if "FEHLER_UNSCHARF" in res: st.error("⚠️ Foto zu unscharf!")
                    else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
        elif upload: st.warning("Guthaben leer.")

    if st.session_state.full_res:
        st.divider(); st.markdown(st.session_state.full_res)
        st.subheader("📥 Downloads")
        d_col = st.columns(3)
        with d_col[0]: st.download_button("📝 Word", create_docx(st.session_state.full_res), "Antwort.docx")
        with d_col[1]: st.download_button("📄 PDF", create_pdf(st.session_state.full_res), "Analyse.pdf")
        with d_col[2]: 
            if st.button("🔄 Neu"): st.session_state.full_res = ""; st.rerun()

with t2:
    st.header("⚡ Vorlagen")
    for k, v in VORLAGEN.items(): st.markdown(f"**{k}:**"); st.info(v)

with t3:
    st.header("❓ FAQ")
    for q, a in FAQ_DATA: st.markdown(f"**{q}**"); st.write(a); st.divider()

with t4:
    st.header("⚖️ Impressum")
    st.markdown(IMPRESSUM_TEXT)

with t5:
    st.header("🔒 Datenschutz")
    st.markdown(DATENSCHUTZ_TEXT)

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
