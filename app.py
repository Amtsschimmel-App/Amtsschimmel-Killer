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
# 1. SETUP & KOMPAKTES DESIGN (STRENG FIXIERT)
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
    </style>
    """, unsafe_allow_html=True)

LOGO_DATEI = "icon_final_blau.png"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 2. ADMIN & SESSION STATE (999 SCANS)
# ==========================================
if "credits" not in st.session_state: st.session_state.credits = 0
if "full_res" not in st.session_state: st.session_state.full_res = ""

if st.query_params.get("admin") == "GeheimAmt2024!":
    st.session_state.credits = 999

# ==========================================
# 3. OBERE ZEILE: 4 BOXEN EINGEKLAPPT (EXAKT)
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
Ein Scan wird erst berechnet, wenn die KI den Text erfolgreich verarbeitet hat. Sollte ein Upload technisch scheitern, wird kein Guthaben abgezogen.

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
# 4. HAUPTBEREICH (PAKETE | UPLOAD | ANALYSE)
# ==========================================
c_pak, c_up, c_res = st.columns([0.8, 1.2, 1.5])

with c_pak:
    st.subheader("🌐 Sprachen")
    st.selectbox("Wahl", [
        "🇩🇪 Deutsch", "🇺🇸 English", "🇹🇷 Türkçe", "🇵🇱 Polski", 
        "🇷🇺 Русский", "🇸🇦 العربية", "🇪🇸 Español", "🇫🇷 Français", 
        "🇮🇹 Italiano", "🇷🇴 Română", "🇺🇦 Українська", "🇬🇷 Ελληνικά"
    ], label_visibility="collapsed")
    
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=110)
    
    st.write("---")
    # KOMPAKTE PAKET BOXEN MIT FIXIERTEN STRIPE LINKS
    st.markdown(f'<div class="paket-card"><div class="paket-title">📦 Basis Paket</div><div class="price-tag">3,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_1)
    
    st.markdown(f'<div class="paket-card"><div class="paket-title">🎁 Spar Paket</div><div class="price-tag">9,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_2)
    
    st.markdown(f'<div class="paket-card"><div class="paket-title">💎 Premium Paket</div><div class="price-tag">19,99 €</div><div class="no-abo-text">Einmalpreis • KEIN ABO</div></div>', unsafe_allow_html=True)
    st.link_button("Jetzt kaufen", STRIPE_3)

with c_up:
    st.subheader("📄 Upload & Vorschau")
    st.info(f"Guthaben: **{st.session_state.credits} Scans**")
    
    # Drag & Drop box tiefer setzen
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    upped = st.file_uploader("Datei upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if upped:
        st.markdown("---")
        if upped.type == "application/pdf":
            try:
                images = convert_from_bytes(upped.read())
                for i, img in enumerate(images): st.image(img, caption=f"Seite {i+1}", use_container_width=True)
            except: st.error("Vorschau nicht möglich")
        else:
            st.image(upped, caption="Vorschau", use_container_width=True)
        
        if st.session_state.credits > 0:
            if st.button("🚀 JETZT ANALYSIEREN"):
                with st.spinner("Analyse läuft..."):
                    # Hier GPT-4o Logik einfügen
                    st.session_state.full_res = "### 🚦 Wichtigkeit\nHoch\n\n### 📖 Analyse\nAnalyse fertig.\n\n### 📅 Fristen\n31.12.2025"
                    st.session_state.credits -= 1
                    st.rerun()

with c_res:
    st.subheader("📊 Ergebnisse")
    if st.session_state.full_res:
        res = st.session_state.full_res
        st.info(f"**🚦 Wichtigkeit**\n{re.search(r'🚦(.*?)(?=📖|$)', res, re.S).group(1) if '🚦' in res else '...'}")
        st.write(f"**📖 Zusammenfassung**\n{re.search(r'📖(.*?)(?=📅|$)', res, re.S).group(1) if '📖' in res else '...'}")
        st.warning(f"**📅 Fristen**\n{re.search(r'📅(.*?)(?=✍️|$)', res, re.S).group(1) if '📅' in res else '...'}")
        st.success(f"**✍️ Antwort-Entwurf**\n{re.search(r'✍️(.*)', res, re.S).group(1) if '✍️' in res else '...'}")
    else:
        st.info("Bitte Dokument links hochladen.")
