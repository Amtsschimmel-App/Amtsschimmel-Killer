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
# 1. RECHTSTEXTE & KONSTANTEN (FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

LOGO_DATEI = "icon_final_blau.png"

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

FAQ_TEXT = """
**Ist das ein Abonnement?**  
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**  
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**  
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**  
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**  
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.
"""

VORLAGEN = [
    ("Fristverlängerung", "Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]"),
    ("Widerspruch einlegen (Fristwahrend)", "Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]"),
    ("Akteneinsicht einfordern", "Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]")
]

# ==========================================
# 2. SESSION STATE
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
# 3. EXPORT FUNKTIONEN (REPARIERT)
# ==========================================
def clean_txt(t):
    return t.replace("###","").replace("**","").replace("🚦","").replace("📖","").replace("📅","").replace("✍️","").replace("📋","").encode('latin-1', 'replace').decode('latin-1')

def create_pdf_final(text):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_DATEI): 
        pdf.image(LOGO_DATEI, x=10, y=8, w=33)
        pdf.ln(25)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "ANALYSE-ERGEBNIS", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, txt=clean_txt(text))
    return pdf.output(dest='S').encode('latin-1')

def create_excel_final(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    if not dates: dates = ["Nicht erkannt"]
    df = pd.DataFrame({
        "Datum": dates, 
        "Analyse-Auszug": [text[:200] + "..." for _ in range(len(dates))]
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.sheets['Sheet1'].set_column(1, 1, 100)
    return output.getvalue()

def create_ics_final(text):
    dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', text)
    ics = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for d in dates:
        try:
            cd = datetime.strptime(d, "%d.%m.%Y").strftime("%Y%m%d")
            ics += f"BEGIN:VEVENT\nSUMMARY:Frist Amtsschimmel\nDTSTART:{cd}\nDTEND:{cd}\nDESCRIPTION:Frist aus Analyse\nEND:VEVENT\n"
        except: pass
    ics += "END:VCALENDAR"
    return ics.encode('utf-8')

# ==========================================
# 4. KI-LOGIK
# ==========================================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_text(file):
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

def run_ai(raw_text, lang, mode):
    if len(raw_text.strip()) < 40: return "FEHLER_UNSCHARF"
    label = "Widerspruch" if mode == "W" else "Antwortbrief"
    sys_p = f"""Rechtsexperte. Sprache: {lang}. 
    Erstelle IMMER folgende Sektionen:
    1. ### 🚦 DRINGLICHKEITS-AMPEL ### (ROT/GELB/GRÜN + Begründung)
    2. ### 📖 BEHÖRDEN-DOLMETSCHER ### (Glossar: 3-4 Begriffe einfach erklärt)
    3. ### 📅 WICHTIGE FRISTEN ### (Datum | Aktion)
    4. ### ✍️ DEIN {label.upper()} ### (Der vollständige {label})
    5. ### 📋 VERSAND-CHECKLISTE ### (Anleitung: Einschreiben etc.)"""
    resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": raw_text}])
    return resp.choices.message.content

# ==========================================
# 5. UI & HAUPTFUNKTION
# ==========================================
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    st.metric("Dein Guthaben", f"{st.session_state.credits} Scans")
    lang_choice = st.selectbox("🌍 Sprache wählen", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский"])
    st.divider()
    with st.expander("ℹ️ Impressum"): st.write(IMPRESSUM_TEXT)
    with st.expander("🛡️ Datenschutz"): st.write(DATENSCHUTZ_TEXT)
    with st.expander("❓ FAQ"): st.write(FAQ_TEXT)

st.title("📄 Amtsschimmel-Killer")
st.write("Verwandle Behörden-Deutsch in klare Antworten.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Dokument hochladen")
    u_file = st.file_uploader("Brief fotografieren oder PDF hochladen", type=['png', 'jpg', 'jpeg', 'pdf'])
    mode = st.radio("Was soll ich erstellen?", ["📝 Antwortbrief", "🛑 Widerspruch"], horizontal=True)
    
    if u_file and st.button("🚀 Jetzt analysieren (-1 Scan)"):
        if st.session_state.credits > 0:
            with st.spinner("KI liest und übersetzt..."):
                raw = get_text(u_file)
                res = run_ai(raw, lang_choice, "W" if "Widerspruch" in mode else "A")
                if res == "FEHLER_UNSCHARF":
                    st.error("Text zu unscharf! Bitte neu fotografieren.")
                else:
                    st.session_state.full_res = res
                    st.session_state.credits -= 1
                    st.rerun()
        else:
            st.warning("Kein Guthaben mehr! Bitte im Shop aufladen.")

with col2:
    st.subheader("2. Analyse & Ergebnis")
    if st.session_state.full_res:
        st.markdown(st.session_state.full_res)
        st.divider()
        st.download_button("📥 Als PDF speichern", create_pdf_final(st.session_state.full_res), "Analyse.pdf")
        st.download_button("📊 In Excel (Fristen)", create_excel_final(st.session_state.full_res), "Fristen.xlsx")
        st.download_button("📅 Kalender-Termin", create_ics_final(st.session_state.full_res), "Fristen.ics")
    else:
        st.info("Hier erscheint das Ergebnis nach dem Scan.")

st.divider()
st.subheader("📋 Schnelle Vorlagen")
for titel, text in VORLAGEN:
    with st.expander(titel):
        st.code(text)
