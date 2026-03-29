import streamlit as st
from openai import OpenAI
import pytesseract
from PIL import Image
import pdfplumber
from pdf2image import convert_from_bytes
import io
import os
from fpdf import FPDF 
from datetime import datetime

# ==========================================
# 1. SETUP & DESIGN (STRENG FIXIERT)
# ==========================================
st.set_page_config(page_title="Amtsschimmel-Killer", page_icon="📄", layout="wide")

# DEINE EXAKTEN STRIPE LINKS
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02" # 1 Dokument
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03" # 3 Dokumente
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04" # 10 Dokumente

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card {
            border: 1px solid #0d47a1; padding: 8px; border-radius: 10px;
            background-color: #f8fbff; margin-bottom: 2px; text-align: center;
        }
        .price-tag { font-size: 15px; font-weight: bold; color: #0d47a1; margin: 0px; }
        .no-abo-text { font-size: 10px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .paket-title { font-size: 12px; font-weight: bold; color: #333; margin-bottom: 2px; }
        .stLinkButton a {
            width: 100% !important; background-color: #0d47a1 !important;
            color: white !important; border-radius: 6px !important;
            font-weight: bold !important; padding: 5px !important;
            font-size: 12px !important; text-decoration: none;
            display: inline-block; text-align: center;
        }
        .stExpander div { line-height: 1.4 !important; white-space: pre-wrap !important; font-size: 12px; }
        .analysis-box { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #ddd; white-space: pre-wrap; }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. GUTHABEN-LOGIK & ZAHLUNGSERKENNUNG
# ==========================================
if "credits" not in st.session_state:
    st.session_state.credits = 0
if "full_res" not in st.session_state:
    st.session_state.full_res = ""

# Gutschrift nach Kauf via URL-Parameter
params = st.query_params
if "p" in params:
    val = params["p"]
    if val == "1": st.session_state.credits += 1
    elif val == "2": st.session_state.credits += 3
    elif val == "3": st.session_state.credits += 10 # 10 Dokumente
    st.query_params.clear()

# SADMIN MODUS
if params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_text)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. OBERE ZEILE: EINGEKLAPPTE INFOS (EXAKT)
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
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

3. Dokumentenverarbeitung
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

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
# 4. HAUPTBEREICH
# ==========================================
c_pak, c_up, c_res = st.columns([0.9, 1.1, 1.5])

with c_pak:
    st.subheader("🌐 Sprachen")
    lang = st.selectbox("Wahl", ["🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", "🇮🇹 Italiano", "🇷🇴 Română", "🇺🇦 Українська", "🇬🇷 Ελληνικά"], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=110)
    
    st.write("---")
    
    # PAKET 1: Analyse
    st.markdown(f'<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Analyse<br>(1 Dokument)</div><div class="price-tag">Einmalpreis 3,99 €</div><div class="no-abo-text">KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_1)
    
    # PAKET 2: Spar-Paket
    st.markdown(f'<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Spar-Paket<br>(3 Dokumente)</div><div class="price-tag">Einmalpreis 9,99 €</div><div class="no-abo-text">KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_2)
    
    # PAKET 3: Sorglos-Paket
    st.markdown(f'<div class="paket-card"><div class="paket-title">Amtsschimmel-Killer: Sorglos-Paket<br>(10 Dokumente)</div><div class="price-tag">Einmalpreis 19,99 €</div><div class="no-abo-text">KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_3)

with c_up:
    # ABSTAND FÜR MITTIGE AUSRICHTUNG NEBEN DEN PAKETEN
    st.markdown("<div style='height: 58px;'></div>", unsafe_allow_html=True)
    st.subheader("📄 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Dokumente**")
    
    upped = st.file_uploader("Datei", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    extracted_text = ""
    if upped:
        if upped.type == "application/pdf":
            try:
                raw_pdf = upped.read()
                with pdfplumber.open(io.BytesIO(raw_pdf)) as pdf:
                    for page in pdf.pages: extracted_text += (page.extract_text() or "") + "\n"
                imgs = convert_from_bytes(raw_pdf, first_page=1, last_page=1)
                st.image(imgs, caption="Vorschau", use_container_width=True)
            except: st.info("Vorschau lädt...")
        else:
            img = Image.open(upped)
            st.image(img, caption="Vorschau", use_container_width=True)
            extracted_text = pytesseract.image_to_string(img)
        
        if st.button("🚀 JETZT ANALYSIEREN"):
            if st.session_state.credits > 0:
                with st.spinner("Analyse läuft..."):
                    try:
                        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Analysiere auf {lang}:\n\n{extracted_text}"}])
                        st.session_state.full_res = res.choices.message.content
                        st.session_state.credits -= 1
                        st.rerun()
                    except Exception as e: st.error(f"Fehler: {e}")
            else:
                st.error("Guthaben: 0 Dokumente. Bitte ein Paket kaufen.")

with c_res:
    st.subheader("🔍 Analyse & Antwort")
    if st.session_state.full_res:
        st.markdown(f'<div class="analysis-box">{st.session_state.full_res}</div>', unsafe_allow_html=True)
        pdf_f = generate_pdf(st.session_state.full_res)
        st.download_button("📥 PDF herunterladen", data=pdf_f, file_name="Analyse.pdf", mime="application/pdf")
        if st.button("Neuer Scan"):
            st.session_state.full_res = ""
            st.rerun()
    else:
        st.info("Das Ergebnis erscheint hier nach der Analyse.")
