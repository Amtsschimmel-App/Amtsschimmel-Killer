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
from datetime import datetime

# ==========================================
# 1. SETUP & DESIGN (STRENG FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# FEST VERANKERTE STRIPE LINKS
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03"
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card {
            border: 2px solid #0d47a1;
            padding: 10px;
            border-radius: 12px;
            background-color: #f8fbff;
            margin-bottom: 5px;
            text-align: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .price-tag { font-size: 22px; font-weight: bold; color: #0d47a1; margin: 2px 0; }
        .no-abo-text { font-size: 11px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .stLinkButton a {
            width: 100% !important;
            background-color: #0d47a1 !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            padding: 10px !important;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .stExpander div { line-height: 1.5 !important; white-space: pre-wrap !important; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. ADMIN & SESSION STATE (999 SCANS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""

# ADMIN BACKDOOR (URL: ?admin=GeheimAmt2024!)
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 3. OBERE ZEILE: 4 BOXEN EINGEKLAPPT (FIXIERT)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.expander("⚖️ Impressum", expanded=False):
        st.write("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9
40223 Düsseldorf

Kontakt:
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

Haftung:
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")

with t2:
    with st.expander("🛡️ Datenschutz", expanded=False):
        st.write("""1. Datenschutz auf einen Blick
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

2. Datenerfassung & Hosting
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern.

4. Zahlungsabwicklung (Stripe)
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

5. Ihre Rechte
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")

with t3:
    with st.expander("❓ FAQ", expanded=False):
        st.write("""Ist das ein Abonnement?
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

Wie sicher sind meine Dokumente?
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

Ersetzt die App eine Rechtsberatung?
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

Was passiert, wenn der Scan fehlschlägt?
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

Wie erreiche ich Elisabeth Reinecke?
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")

with t4:
    with st.expander("📝 Vorlagen", expanded=False):
        st.write("""Fristverlängerung:
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

Widerspruch einlegen (Fristwahrend):
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

Akteneinsicht einfordern:
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# ==========================================
# 4. HILFSFUNKTIONEN (OCR & EXPORT)
# ==========================================
def extract_text(file):
    text = ""
    file_bytes = file.read()
    if file.type == "application/pdf":
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages: text += (page.extract_text() or "") + "\n"
        if not text.strip():
            images = convert_from_bytes(file_bytes)
            for img in images: text += pytesseract.image_to_string(img, lang='deu') + "\n"
    else:
        text = pytesseract.image_to_string(Image.open(io.BytesIO(file_bytes)), lang='deu')
    return text

def create_pdf(text):
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 8, text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 5. HAUPTBEREICH (3 SPALTEN: PAKETE | UPLOAD | ANALYSE)
# ==========================================
c_pak, c_up, c_res = st.columns([0.9, 1.1, 1.4])

with c_pak:
    st.subheader("🌐 Sprachen")
    st.selectbox("Wahl", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", 
        "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", 
        "🇮🇹 Italiano", "🇷🇴 Română", "🇺🇦 Українська"
    ], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=130)
    
    st.subheader("💰 Pakete")
    st.markdown(f'<div class="paket-card"><b>📦 1. Paket</b><br><div class="price-tag">3,99 €</div><div class="no-abo-text">1 Scan • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_1)
    
    st.markdown(f'<div class="paket-card"><b>🎁 2. Paket</b><br><div class="price-tag">9,99 €</div><div class="no-abo-text">3 Scans • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_2)
    
    st.markdown(f'<div class="paket-card"><b>💎 3. Paket</b><br><div class="price-tag">19,99 €</div><div class="no-abo-text">10 Scans • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_3)

with c_up:
    st.subheader("📄 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    upped = st.file_uploader("Datei upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        if upped.type == "application/pdf":
            try:
                images = convert_from_bytes(upped.getvalue())
                for i, img in enumerate(images): st.image(img, caption=f"Seite {i+1}", use_container_width=True)
            except: st.error("Vorschau nicht möglich")
        else:
            st.image(upped, caption="Vorschau", use_container_width=True)
        
        if st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("Analyse läuft..."):
                    upped.seek(0)
                    raw = extract_text(upped)
                    resp = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "Analysiere präzise: 🚦 WICHTIGKEIT, 📖 ZUSAMMENFASSUNG, 📅 FRISTEN, ✍️ ANTWORT-ENTWURF."},
                                  {"role": "user", "content": raw}]
                    )
                    st.session_state.full_res = resp.choices.message.content
                    st.session_state.credits -= 1
                    st.rerun()

with c_res:
    st.subheader("📊 Ergebnisse")
    if st.session_state.full_res:
        res = st.session_state.full_res
        st.info(f"**🚦 Wichtigkeit**\n{re.search(r'🚦(.*?)(?=📖|$)', res, re.S).group(1) if '🚦' in res else '...'}")
        st.write(f"**📖 Zusammenfassung**\n{re.search(r'📖(.*?)(?=📅|$)', res, re.S).group(1) if '📖' in res else '...'}")
        st.warning(f"**📅 Fristen**\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else '...'}")
        st.success(f"**✍️ Antwortschreiben**\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else '...'}")
    else:
        st.info("Bitte Dokument links hochladen.")

# ==========================================
# 6. DOWNLOADS GANZ UNTEN
# ==========================================
if st.session_state.full_res:
    st.divider()
    d1, d2, d3, d4 = st.columns(4)
    with d1: st.download_button("📄 PDF Export", create_pdf(st.session_state.full_res), "Analyse.pdf")
    with d2: st.download_button("📝 Word Export", create_pdf(st.session_state.full_res), "Analyse.docx")
    with d3:
        dates = re.findall(r'(\d{2}\.\d{2}\.\d{4})', st.session_state.full_res)
        df = pd.DataFrame({"Termine": dates if dates else ["Keine"], "Inhalt": [st.session_state.full_res]})
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='xlsxwriter') as wr: df.to_excel(wr, index=False)
        st.download_button("📊 Excel Liste", out.getvalue(), "Fristen.xlsx")
    with d4:
        st.download_button("📅 Kalender", b"BEGIN:VCALENDAR\nEND:VCALENDAR", "Frist.ics")
