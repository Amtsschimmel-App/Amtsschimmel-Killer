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
# 3. KI-LOGIK & OCR (FEHLER KORRIGIERT)
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
    if len(raw_text.strip()) < 50: 
        return "FEHLER_UNSCHARF"
    
    intent = "Antwortbrief" if mode == "Standard" else "WIDERSPRUCH (hart, mit Paragraphen)"
    
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Struktur IMMER:
    ### AMPEL ### Dringlichkeit: [Niedrig/Mittel/Hoch] + Grund: [Satz]
    ### GLOSSAR ### (Erkläre 3 schwierige Begriffe einfach)
    ### FRISTEN ### (Datum | Aktion | Dringlichkeit)
    ### ANTWORTBRIEF ### (Erstelle einen {intent})
    ### CHECKLISTE ### (Versandanweisungen)"""
    
    resp = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}]
    )
    # KORREKTUR HIER: .choices[0].message.content (Index 0 hinzugefügt)
    return resp.choices[0].message.content

# ==========================================
# 4. EXPORT FUNKTIONEN
# ==========================================
def create_docx(text):
    doc = Document(); doc.add_heading('Amtsschimmel-Killer Analyse', 0)
    clean_text = text.replace("###", "").replace("**", "")
    doc.add_paragraph(clean_text); bio = io.BytesIO()
    doc.save(bio); return bio.getvalue()

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
# 5. SIDEBAR (LOGO & FLAGGEN)
# ==========================================
with st.sidebar:
    LOGO_PATH = "icon_final_blau.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.title("📄 Amtsschimmel-Killer")
    
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    st.divider()
    lang_choice = st.selectbox("🌍 Sprache wählen", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", 
        "🇪🇸 Español", "🇫🇷 Français", "🇦🇱 Albanian", "🇮🇹 Italiano", 
        "🇳🇱 Nederlands", "🇸🇦 العربية", "🇺🇦 Українська"
    ])
    
    st.divider()
    st.subheader("Guthaben aufladen")
    pkgs = [("📄 Basis", st.secrets["STRIPE_LINK_1"], "1 Scan", "3,99 €"), ("🚀 Spar", st.secrets["STRIPE_LINK_3"], "3 Scans", "9,99 €"), ("💎 Profi", st.secrets["STRIPE_LINK_10"], "10 Scans", "19,99 €")]
    for n, l, c, p in pkgs:
        st.markdown(f'<a href="{l}" target="_blank" class="buy-button"><b>{n}</b><br>{p} | {c}<br><small>✔ Einmalzahlung | <b>KEIN ABO</b></small></a>', unsafe_allow_html=True)

# ==========================================
# 6. HAUPTBEREICH (MIT VORSCHAU & FESTEN TEXTEN)
# ==========================================
t1, t2, t3, t4, t5 = st.tabs(["🚀 Brief-Killer", "⚡ Vorlagen", "❓ FAQ", "⚖️ Impressum", "🔒 Datenschutz"])

with t1:
    st.title("Brief hochladen & killen 🚀")
    c1, c2 = st.columns(2)
    with c1:
        upload = st.file_uploader("Datei wählen (PDF oder Bild):", type=['pdf', 'png', 'jpg', 'jpeg'])
        # VORSCHAU WIEDER EINGEBAUT
        if upload:
            if upload.type.startswith("image"):
                st.image(upload, caption="Vorschau deines Briefes", use_container_width=True)
            else:
                st.success("PDF erfolgreich geladen!")

    with c2:
        if upload and st.session_state.credits > 0:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🚀 ANALYSE STARTEN"):
                    with st.spinner("Analyse läuft..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Standard")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Text ist zu unscharf, bitte nochmal mit mehr Licht fotografieren. (Kein Abzug)")
                        else: st.session_state.full_res = res; st.session_state.credits -= 1; st.rerun()
            with b2:
                if st.button("⚖️ WIDERSPRUCH ERSTELLEN"):
                    with st.spinner("Widerspruch wird generiert..."):
                        txt = get_text_from_file(upload)
                        res = analyze_letter(txt, lang_choice, "Widerspruch")
                        if "FEHLER_UNSCHARF" in res: st.error("⚠️ Text ist zu unscharf, bitte nochmal mit mehr Licht fotografieren. (Kein Abzug)")
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
    st.markdown("### Fristverlängerung")
    st.info("Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]")
    st.markdown("### Widerspruch einlegen (Fristwahrend)")
    st.info("Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]")
    st.markdown("### Akteneinsicht einfordern")
    st.info("Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")

with t3:
    st.header("❓ FAQ")
    st.markdown('<span class="faq-q">Ist das ein Abonnement?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.</div>', unsafe_allow_html=True)
    st.markdown('<span class="faq-q">Wie sicher sind meine Dokumente?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.</div>', unsafe_allow_html=True)
    st.markdown('<span class="faq-q">Ersetzt die App eine Rechtsberatung?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.</div>', unsafe_allow_html=True)
    st.markdown('<span class="faq-q">Was passiert, wenn der Scan fehlschlägt?</span>', unsafe_allow_html=True)
    st.markdown('<div class="faq-a">Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.</div>', unsafe_allow_html=True)

with t4:
    st.header("⚖️ Impressum")
    st.markdown("""
    **Amtsschimmel-Killer**  
    Betreiberin: Elisabeth Reinecke  
    Ringelsweide 9, 40223 Düsseldorf  
    Telefon: +49 211 15821329  
    E-Mail: amtsschimmel-killer@proton.me  
    Web: amtsschimmel-killer.streamlit.app  
    
    Haftung: Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.
    """)

with t5:
    st.header("🔒 Datenschutz")
    st.markdown("""
    **1. Datenschutz auf einen Blick**  
    Wir behandeln Ihre personenbezogenen Daten vertraulich entsprechend der DSGVO.  
    **2. Datenerfassung & Hosting**  
    Diese App wird auf Streamlit Cloud gehostet. Logfiles werden automatisch vom Hoster erfasst.  
    **3. Dokumentenverarbeitung**  
    Ihre hochgeladenen Briefe werden per TLS an OpenAI (USA) übertragen. Wir speichern keine Briefe.  
    **4. Zahlungsabwicklung**  
    Abwicklung über Stripe. Wir erhalten nur Zahlungsbestätigungen.
    """)

st.sidebar.caption(f"© {datetime.now().year} Elisabeth Reinecke")
