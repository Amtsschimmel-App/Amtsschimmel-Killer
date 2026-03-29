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

# DEINE STRIPE LINKS (FIXIERT)
STRIPE_1 = "https://buy.stripe.com/eVqcN53Pd5YLgo8alq1gs02"
STRIPE_2 = "https://buy.stripe.com/8x228retRbj50paalq1gs03"
STRIPE_3 = "https://buy.stripe.com/28EcN50D1bj52xi8di1gs04"

st.markdown("""
    <style>
        .block-container { padding-top: 1rem; }
        .paket-card {
            border: 1px solid #0d47a1;
            padding: 8px;
            border-radius: 10px;
            background-color: #f8fbff;
            margin-bottom: 2px;
            text-align: center;
        }
        .price-tag { font-size: 18px; font-weight: bold; color: #0d47a1; margin: 0px; }
        .no-abo-text { font-size: 10px; color: #d32f2f; font-weight: bold; text-transform: uppercase; }
        .paket-title { font-size: 13px; font-weight: bold; color: #333; }
        .stLinkButton a {
            width: 100% !important;
            background-color: #0d47a1 !important;
            color: white !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            padding: 5px !important;
            font-size: 12px !important;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .stExpander div { line-height: 1.4 !important; white-space: pre-wrap !important; font-size: 12px; }
        .analysis-box { 
            background-color: #ffffff; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #ddd;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            white-space: pre-wrap;
        }
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"

# OpenAI Client
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("Bitte OPENAI_API_KEY in den Streamlit Secrets hinterlegen!")

# ==========================================
# 2. SESSION STATE & ADMIN
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""

# Admin-Modus via URL: ?admin=GeheimAmt2024!
if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=safe_text)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. OBERE ZEILE: TEXTE (EXAKT ÜBERNOMMEN)
# ==========================================
st.title("Amtsschimmel-Killer 🪓")

t1, t2, t3, t4 = st.columns(4)
with t1:
    with st.expander("⚖️ Impressum", expanded=False):
        st.write("""Amtsschimmel-Killer
Betreiberin: Elisabeth Reinecke
Ringelsweide 9
40223 Düsseldorf

**Kontakt:**
Telefon: +49 211 15821329
E-Mail: amtsschimmel-killer@proton.me
Web: amtsschimmel-killer.streamlit.app

**Haftung:**
Inhalte nach § 5 TMG. Keine Haftung für KI-generierte Texte.""")
with t2:
    with st.expander("🛡️ Datenschutz", expanded=False):
        st.write("""**1. Datenschutz auf einen Blick**
Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Vorschriften (DSGVO).

**2. Datenerfassung & Hosting**
Diese App wird auf Streamlit Cloud gehostet. Beim Besuch werden Logfiles (IP-Adresse, Browser) automatisch vom Hoster erfasst. Wir nutzen diese Daten nicht.

**3. Dokumentenverarbeitung**
Ihre hochgeladenen Briefe werden per TLS-verschlüsselter Schnittstelle an OpenAI (USA) zur Analyse übertragen. Wir speichern keine Briefe auf unseren Servern. Die Verarbeitung dient rein dem Zweck, Ihnen einen Antwortentwurf zu erstellen.

**4. Zahlungsabwicklung (Stripe)**
Bei Käufen werden Sie zu Stripe weitergeleitet. Stripe erhebt die erforderlichen Daten zur Abrechnung. Wir erhalten lediglich eine Bestätigung über die erfolgreiche Zahlung.

**5. Ihre Rechte**
Sie haben das Recht auf Auskunft, Löschung und Sperrung Ihrer Daten. Kontaktieren Sie uns unter amtsschimmel-killer@proton.me.""")
with t3:
    with st.expander("❓ FAQ", expanded=False):
        st.write("""**Ist das ein Abonnement?**
Nein. Wir hassen Abos genauso wie Amtsschimmel. Jede Zahlung ist eine Einmalzahlung für eine feste Anzahl an Scans. Es gibt keine automatische Verlängerung.

**Wie sicher sind meine Dokumente?**
Ihre Dokumente werden verschlüsselt an die KI (OpenAI) übertragen, dort nur kurzzeitig im Arbeitsspeicher verarbeitet und niemals dauerhaft auf unseren Servern gespeichert. Nach der Analyse werden die Daten gelöscht.

**Ersetzt die App eine Rechtsberatung?**
Nein. Wir bieten eine Formulierungshilfe und Unterstützung beim Textverständnis. Für verbindliche Rechtsberatung wenden Sie sich bitte an einen Rechtsanwalt.

**Was passiert, wenn der Scan fehlschlägt?**
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern (z.B. wegen eines unscharfen Fotos), wird kein Guthaben abgezogen.

**Wie erreiche ich Elisabeth Reinecke?**
Nutzen Sie einfach die E-Mail amtsschimmel-killer@proton.me oder die Telefonnummer im Impressum.""")
with t4:
    with st.expander("📝 Vorlagen", expanded=False):
        st.write("""**Fristverlängerung:**
Sehr geehrte Damen und Herren, in der Angelegenheit [Aktenzeichen] bitte ich um Verlängerung der gesetzten Frist bis zum [Datum], da mir noch notwendige Unterlagen fehlen. Mit freundlichen Grüßen, [Name]

**Widerspruch einlegen (Fristwahrend):**
Sehr geehrte Damen und Herren, gegen Ihren Bescheid vom [Datum], erhalten am [Datum], lege ich hiermit Widerspruch ein. Eine detaillierte Begründung folgt in einem separaten Schreiben. Mit freundlichen Grüßen, [Name]

**Akteneinsicht einfordern:**
Sehr geehrte Damen und Herren, zur Prüfung des Sachverhalts [Aktenzeichen] beantrage ich hiermit gemäß § 25 SGB X bzw. § 29 VwVfG Akteneinsicht. Mit freundlichen Grüßen, [Name]""")

st.divider()

# ==========================================
# 4. HAUPTBEREICH
# ==========================================
c_pak, c_up, c_res = st.columns([0.8, 1.2, 1.5])

with c_pak:
    st.subheader("🌐 Sprachen")
    selected_lang = st.selectbox("Wahl", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", 
        "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", 
        "🇮🇹 Italiano", "🇷🇴 Română", "🇺🇦 Українська", "🇬🇷 Ελληνικά"
    ], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=110)
    
    st.write("---")
    st.markdown(f'<div class="paket-card"><div class="paket-title">📦 Basis Paket</div><div class="price-tag">3,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_1)
    
    st.markdown(f'<div class="paket-card"><div class="paket-title">🎁 Spar Paket</div><div class="price-tag">9,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_2)
    
    st.markdown(f'<div class="paket-card"><div class="paket-title">💎 Premium Paket</div><div class="price-tag">19,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_3)

with c_up:
    st.subheader("📄 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    
    upped = st.file_uploader("Datei upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    doc_text = ""
    if upped:
        if upped.type == "application/pdf":
            try:
                # Schnelle PDF Text-Extraktion & Vorschau
                upped_bytes = upped.read()
                with pdfplumber.open(io.BytesIO(upped_bytes)) as pdf:
                    for page in pdf.pages: doc_text += page.extract_text() + "\n"
                
                # Zeige die erste Seite als Bild-Vorschau
                img_preview = convert_from_bytes(upped_bytes, first_page=1, last_page=1)
                st.image(img_preview[0], caption="PDF Vorschau", use_container_width=True)
            except: st.error("Fehler beim Lesen des PDFs.")
        else:
            img = Image.open(upped)
            st.image(img, caption="Vorschau", use_container_width=True)
            doc_text = pytesseract.image_to_string(img)
        
        st.divider()
        if st.button("🚀 JETZT ANALYSIEREN"):
            if st.session_state.credits > 0:
                if not doc_text or len(doc_text.strip()) < 10:
                    st.warning("Kein Text erkannt. Bitte ein schärferes Bild hochladen.")
                else:
                    with st.spinner("Amtsschimmel wird bekämpft..."):
                        try:
                            prompt = f"Analysiere diesen Behördenbrief auf {selected_lang}: 1. Zusammenfassung (was wird verlangt?) 2. Wichtige Fristen 3. Entwurf für eine Antwort. Hier der Text:\n\n{doc_text}"
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[{"role": "user", "content": prompt}]
                            )
                            st.session_state.full_res = response.choices.message.content
                            st.session_state.credits -= 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"KI-Fehler: {e}")
            else:
                st.error("⚠️ Guthaben auf 0! Bitte links ein Paket kaufen.")

with c_res:
    st.subheader("🔍 Analyse & Antwort")
    if st.session_state.full_res:
        st.markdown(f'<div class="analysis-box">{st.session_state.full_res}</div>', unsafe_allow_html=True)
        
        st.divider()
        pdf_data = generate_pdf(st.session_state.full_res)
        st.download_button(
            label="📥 Als PDF herunterladen",
            data=pdf_data,
            file_name=f"Amtsschimmel_Killer_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf"
        )
        if st.button("🔄 Neuer Scan"):
            st.session_state.full_res = ""
            st.rerun()
    else:
        st.info("Nach dem Upload und Klick auf 'Analysieren' erscheint hier das Ergebnis.")
